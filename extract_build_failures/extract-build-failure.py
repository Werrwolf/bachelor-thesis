import argparse
import json
import pathlib
import re
import typing

import build_log
import error_patterns
import github
from timeit import default_timer

# in ms
MAX_PATTERN_TIME = 20000.0

def main():
    parser = argparse.ArgumentParser(
        description='Extract the failure reason of a build from a JSON log file and post it as a '
                    'comment to the pull request.'
    )
    parser.add_argument(
        '--file',
        help='Path to file that should be searched.',
        required=True
    )
    parser.add_argument(
        '--github-api-url',
        help='Github API URL used for the POST request to create a pull request comment.'
    )
    parser.add_argument(
        '--job',
        help='Name of the failed zuul job.',
        required=True
    )
    parser.add_argument(
        '--log',
        help='Path to a log file which will be created by this script, containing more detailed '
             'error information.',
        required=True
    )
    parser.add_argument(
        '--zuul-log-url',
        help='URL to the zuul logs.',
        required=True
    )
    parser.add_argument(
        '--max-length',
        help='Maximum number of error message lines that will be reported to the pull request.',
        required=True,
        type=int
    )
    parser.add_argument(
        '--contact',
        help='One or more github groups to contact in case a build failure cause could not be '
             'identified.',
        required=True,
    )
    parser.add_argument(
        '--report-last-error',
        help='Instead of reporting all errors found (default), report only the last one.',
        action="store_true",
    )
    parser.add_argument(
        '--report-regex-performance',
        help='Filename to report a timing performance test of the used regexes in order to identify poorly performing regex patterns.',
        required=False,
    )

    args = parser.parse_args()

    log_parser = LogParser(
        file=pathlib.Path(args.file),
        job=args.job,
        log=pathlib.Path(args.log),
        log_url=args.zuul_log_url,
        max_length=args.max_length,
        contact=args.contact,
        report_last_error=args.report_last_error,
        report_regex_performance=args.report_regex_performance
    )

    message = log_parser.parse()

    if args.github_api_url:
        github.create_comment(url=args.github_api_url, message=message)
    else:
        print(message)


class Playbook:
    """Container for information of an Ansible playbook."""
    def __init__(self, playbook):
        self.playbook_info = playbook

    @property
    def status(self):
        if any(s['failures'] for _, s in self.playbook_info['stats'].items()):
            return 'failed'
        if any(s['unreachable'] for _, s in self.playbook_info['stats'].items()):
            return 'unreachable'
        return 'successful'

    @property
    def name(self):
        return self.playbook_info['playbook']

    @property
    def phase(self):
        return self.playbook_info['phase']


class LogParser:
    """Parser for json log files."""
    build_patterns = error_patterns.BUILD_PATTERNS
    infra_patterns = error_patterns.INFRA_PATTERNS
    try:
        redirect_regex = error_patterns.CMD_REDIRECT_REGEX
    # for backwards compatibility, in case an error_patterns.py does not define CMD_REDIRECT_REGEX
    except AttributeError:
        redirect_regex = None

    unknown_errors = False

    def __init__(
        self,
        file: pathlib.Path,
        job,
        log: pathlib.Path,
        log_url,
        max_length,
        contact,
        report_last_error,
        report_regex_performance
    ):
        self.file = file
        self.job = job
        self.log = log
        self.log_url = log_url
        self.max_length = max_length
        self.contact = contact
        self.report_last_error = report_last_error
        self.report_regex_performance = report_regex_performance

        self.build_errors = []
        self.infra_errors = []
        self.failed_phases = []
        self.found_errors = {}

    @property
    def input_url(self):
        """URL of the input log file."""
        return f'{self.log_url}{self.file.name}'

    @property
    def output_url(self):
        """URL of the output log file."""
        return f'{self.log_url}{self.log.name}'

    @property
    def error_message(self):
        """Return an error message, depending on the type of occurring errors."""
        if not self.failed_phases:
            # no failed/unreachable playbook means probably an ansible/zuul syntax error.
            return f'I could be wrong, but it looks like **{self.job}** failed due to a timeout ' \
                   f'or some Ansible/Zuul syntax error.\nPlease take a look at the [log]' \
                   f'({self.input_url.replace(".json", ".txt")}) for more information.'

        prefix = f'It looks like **{self.job}**'
        postfix = f'Here\'s what I found in the [logs]({self.log_url}):'

        message = []
        if self.build_errors:
            message.append(f'{prefix} went up in smoke... :boom:')
            message.append(postfix)
            message.extend(self.build_errors)
        elif self.infra_errors:
            message.append(
                f'{prefix} has stumbled upon an infrastructure problem... :construction:'
            )
            if 'pre' in self.failed_phases:
                message.append(
                    'I will retry, but if the problem persists, you might want to *recheck*.'
                )
            else:
                message.append('You might want to *recheck*.')

            message.append(postfix)
            message.extend(self.infra_errors)

        if message:
            message.append(
                f'\n:bulb: For more information take a look at the '
                f'[error summary]({self.output_url}).\n\nHappy bug fixing! :wave:'
            )

        if self.unknown_errors:
            if not message:
                message.append(
                    f'I looked through the [log]({self.input_url}) of the failing job '
                    f'**{self.job}**, but could\'t find the reason why it failed... :confused:\n'
                    f'You can have a look at the [error summary]({self.output_url}) for more '
                    f'information on the failed playbook.'
                )
            contacts = ' '.join([f'@{contact}' for contact in self.contact.split()])
            message.append(f'\n\n{contacts}: I think I need an update! :innocent:')

        return '\n'.join(message)

    @staticmethod
    def _predicate(x: dict) -> bool:
        """Filter predicate for the build_log module.

        Return true if a dictionary contains any of the following keys:
            - ``rc``, with a value that is not 0
            - ``exception``
            - ``msg``
        """
        return bool(x.get('rc')) or any(k in x for k in ('exception', 'msg'))

    def _find_matches(self, plays, patterns, error_cause, tool=None) -> str:
        """Find matching errors in a list of plays and return the first error found."""
        output_msg = None

        error_msg = f'error cause : {error_cause}'
        if tool:
            error_msg += f' ({tool})'

        # iterate over the regex patterns for _one_ error cause
        for pattern in patterns:

            if self.report_regex_performance:
                start_time = default_timer()

            for error_info in build_log.match_stream_in_plays(
                plays,
                streams=('stdout', 'stderr', 'msg', 'exception', 'errors'),
                regex=re.compile(pattern, re.MULTILINE),
                redirect_regex=self.redirect_regex,
                host_predicate=lambda x: self._predicate(x),
                result_predicate=lambda x: self._predicate(x),
            ):
                match_groups = error_info.match.groupdict()
                details = match_groups.get('details') or error_info.match.group()
                detail_lines = re.split('[\r\n]+', details)

                # get whitespace offset of the log message detail lines
                ws_offset = len(detail_lines[0]) - len(detail_lines[0].lstrip(' '))

                file_info = match_groups.get('file')
                line_info = match_groups.get('line')
                type_info = match_groups.get('type')

                # build the error message header for this match
                message = [80 * '-', error_msg]
                if file_info:
                    file_msg = f'file        : {file_info.strip()}'
                    if line_info:
                        file_msg += f' (line {line_info})'
                    message.append(file_msg)
                if type_info:
                    type_msg = f'error type  : {type_info.strip()}'
                    message.append(type_msg)
                message.append(f'log file    : {error_info.file or self.file.name}')
                message.append(80 * '-' + '\n')

                self._write_log(*message, '', *[line[ws_offset:] for line in detail_lines])

                # build the error message body for this match
                for i, line in enumerate(detail_lines):
                    # limit length of reported error details
                    if i >= self.max_length:
                        message.append('...')
                        break
                    message.append(line[ws_offset:])

                # only return the first match of an error cause
                if not output_msg:
                    output_msg = '```\n' + '\n'.join(message) + '\n```'

            if self.report_regex_performance:
                end_time = default_timer()
                elapsed_time = round((end_time - start_time) * 1000, 3)
                if elapsed_time > MAX_PATTERN_TIME:
                    self._write_log(f"LIMIT EXCEEDED: {elapsed_time} using pattern: '{pattern}'", is_performance_log=True)
                else:
                    self._write_log(f"elapsed time: {elapsed_time} ms using pattern: '{pattern}'", is_performance_log=True)

        return output_msg

    def _find_errors(self, plays, pattern_dict) -> typing.List[str]:
        """Search a list of plays for errors matching a set of regular expressions."""
        errors = []

        for error_cause, value in pattern_dict.items():
            if isinstance(value, dict):
                for tool, patterns in value.items():
                    matches = self._find_matches(
                        plays=plays,
                        patterns=patterns,
                        error_cause=error_cause,
                        tool=tool
                    )
                    tools = self.found_errors.setdefault(error_cause, {})
                    if tool == '':
                        tool = '_no_tool_'
                    tools.setdefault(tool, False)
                    if matches:
                        tools[tool] = True
                        # if match was already found in a tool, the other tools need not be checked
                        break
            else:
                matches = self._find_matches(plays=plays, patterns=value, error_cause=error_cause)
                self.found_errors.setdefault(error_cause, False)
                if matches:
                    self.found_errors[error_cause] = True

            if matches:
                errors.append(matches)

        if self.report_last_error:
            return errors[-1:]

        return errors

    def _write_log(self, *args, is_performance_log=False):
        """Write lines to the log file."""
        # escape characters causing an encoding error with a backslash
        log = self.log
        if is_performance_log and self.report_regex_performance:
            log = self.report_regex_performance

        with open(log, 'a', errors='backslashreplace') as f:
            f.write('\n'.join(args) + '\n')

    def parse(self):
        """Extract the error information from a json log file."""
        with open(self.file, 'r', errors='backslashreplace') as f:
            log_obj = json.load(f)

        for p in log_obj:
            playbook = Playbook(p)

            if playbook.status != 'successful':
                self._write_log(
                    100 * '=',
                    f'Playbook    : {playbook.name}',
                    f'Phase       : {playbook.phase}',
                    f'Status      : {playbook.status}',
                    100 * '='
                )
                self.failed_phases.append(playbook.phase)

                infra_errors = self._find_errors(
                    plays=playbook.playbook_info['plays'],
                    pattern_dict=self.infra_patterns
                )
                if infra_errors:
                    self.infra_errors.extend(infra_errors)
                    continue

                build_errors = self._find_errors(
                    plays=playbook.playbook_info['plays'],
                    pattern_dict=self.build_patterns
                )
                if build_errors:
                    self.build_errors.extend(build_errors)
                    continue

                self.unknown_errors = True

        self.found_errors['unknown_errors'] = self.unknown_errors

        json_log_file = self.log.with_suffix('.json')
        json_log_file.write_text(json.dumps(self.found_errors, indent=2))

        return self.error_message


if __name__ == '__main__':
    main()