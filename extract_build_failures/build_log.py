"""Utilities for matching streams in build logs."""
import typing as t
from collections import namedtuple
import pathlib

ErrorInfo = namedtuple('ErrorInfo', 'match, file')
"""Container for an error match and the corresponding log file in which it was found."""


class UnknownArgumentError(Exception):
    """The argument isn't known by any match function."""


def all_items(_):
    """Predicate for filtering all items."""
    return True


def match_stream_in_playbooks(playbooks: t.List[dict], *, streams: t.Tuple[str, ...] = ('stdout',),
                              regex: t.Pattern, playbook_predicate=all_items, **kwargs) \
        -> t.Iterator[ErrorInfo]:
    """Yields match objects found in playbooks which were filtered by a predicate."""
    filtered_playbooks = filter(playbook_predicate, playbooks)
    for playbook in filtered_playbooks:
        yield from match_stream_in_plays(
            playbook['plays'],
            streams=streams,
            regex=regex,
            **kwargs
        )


def match_stream_in_plays(plays: t.List[dict], *, streams: t.Tuple[str, ...] = ('stdout',),
                          regex: t.Pattern, play_predicate=all_items, **kwargs) \
        -> t.Iterator[ErrorInfo]:
    """Yields match objects found in plays which were filtered by a predicate."""
    filtered_plays = filter(play_predicate, plays)
    for play in filtered_plays:
        yield from match_stream_in_tasks(
            play['tasks'],
            streams=streams,
            regex=regex,
            **kwargs
        )


def match_stream_in_tasks(tasks: t.List[dict], *, streams: t.Tuple[str, ...] = ('stdout',),
                          regex: t.Pattern, task_predicate=all_items, **kwargs) \
        -> t.Iterator[ErrorInfo]:
    """Yields match objects found in tasks which were filtered by a predicate."""
    filtered_tasks = filter(task_predicate, tasks)
    for task in filtered_tasks:
        yield from match_stream_in_hosts(
            task['hosts'],
            streams=streams,
            regex=regex,
            **kwargs
        )


def match_stream_in_hosts(hosts: t.Dict[str, dict], *, streams: t.Tuple[str, ...] = ('stdout',),
                          regex: t.Pattern, redirect_regex: t.Optional[t.Pattern],
                          host_predicate=all_items, **kwargs) \
        -> t.Iterator[ErrorInfo]:
    """Yields match objects found in hosts which were filtered by a predicate."""
    filtered_hosts = filter(host_predicate, hosts.values())
    for host in filtered_hosts:
        for stream in streams:
            if stream in host and host[stream] and isinstance(host[stream], str):
              for match in regex.finditer(host[stream]):
                  yield ErrorInfo(match, None)
            elif stream in host and host[stream] and isinstance(host[stream], list):
              for entry in host[stream]:
                  if isinstance(entry, str):
                      for match in regex.finditer(entry):
                          yield ErrorInfo(match, None)


        yield from match_stream_in_redirected_command(host.get('cmd'), regex, redirect_regex)

        if 'results' in host:
            yield from match_stream_in_results(
                host['results'],
                streams=streams,
                regex=regex,
                redirect_regex=redirect_regex,
                **kwargs
            )


def match_stream_in_results(results: t.List[dict], *, streams: t.Tuple[str, ...] = ('stdout',),
                            regex: t.Optional[t.Pattern], redirect_regex: t.Optional[t.Pattern],
                            result_predicate=all_items, **kwargs) \
        -> t.Iterator[ErrorInfo]:
    """Yields match objects found in results which were filtered by a predicate."""
    if kwargs:
        raise UnknownArgumentError(kwargs)

    filtered_results = filter(result_predicate, results)
    for result in filtered_results:
        for stream in streams:
            if stream in result:
                for match in regex.finditer(result[stream]):
                    yield ErrorInfo(match, None)

        yield from match_stream_in_redirected_command(result.get('cmd'), regex, redirect_regex)


def match_stream_in_redirected_command(cmd: t.Optional[str], regex: t.Pattern,
                                       redirect_regex: t.Optional[t.Pattern]) \
        -> t.Iterator[ErrorInfo]:
    """Yields found matches from within a redirected command output log file."""
    if redirect_regex and cmd and isinstance(cmd, str):
        redirect_match = redirect_regex.search(cmd)
        if redirect_match:
            fpath = pathlib.Path(redirect_match.group('path'))
            if fpath.exists():
                for match in regex.finditer(fpath.read_text(errors='ignore')):
                    yield ErrorInfo(match, fpath.name)
            else:
                print(f'File not found: {fpath}')