import json
import re
import os
import textwrap
import extract_build_failures.error_patterns as error_patterns
import pandas as pd
from collections import defaultdict

INFRA_PATTERNS = error_patterns.INFRA_PATTERNS
BUILD_PATTERNS = error_patterns.BUILD_PATTERNS

def restructure_patterns(patterns):
    """
    Restructures the input patterns dictionary to a more structured format.
    """
    print(" reached: restructure_patterns")
    restructured_patterns = {}
    for pattern_type, subpatterns in patterns.items():
        if isinstance(subpatterns, (set, list)):
            restructured_patterns[pattern_type] = {"": list(subpatterns)}
        elif isinstance(subpatterns, dict):
            restructured_patterns[pattern_type] = {}
            for subtype, regex_list in subpatterns.items():
                if isinstance(regex_list, (list, set)):
                    restructured_patterns[pattern_type][subtype] = list(regex_list)
                else:
                    raise ValueError(f"Unexpected type for regex list: {type(regex_list)}")
        else:
            raise ValueError(f"Unexpected type for subpatterns: {type(subpatterns)}")
    return restructured_patterns


def compile_patterns(patterns_dict):
    """
    Compiles the restructured patterns dictionary into a dictionary of compiled regex patterns.
    """
    print(" reached: compiled_patterns")
    compiled_patterns = {}
    for main_category, subpatterns in patterns_dict.items():
        for sub_category, patterns in subpatterns.items():
            compiled_patterns.setdefault((main_category, sub_category), []).extend([re.compile(pattern) for pattern in patterns])
    return compiled_patterns


def purge_log_lines(log_entries, cutoff_intervall = 1000):
    if len(log_entries) < 2*cutoff_intervall:
        return log_entries
    start_intervall = log_entries[:cutoff_intervall]
    end_intervall = log_entries[-cutoff_intervall:]
    return start_intervall + end_intervall


def check_log_entry(log_entries, compiled_patterns):
    print("reached: check log entry")
    purged_log_entries = purge_log_lines(log_entries, 1000)
    matches_list = []
    for log_entry in purged_log_entries:
        for (main_category, sub_category), regex_list in compiled_patterns.items():
            for pattern in regex_list:
                match = pattern.search(log_entry)
                if match:
                    matches_list.append((main_category, sub_category, match))
    return matches_list


def process_single_file(file_path, compiled_patterns):
    """
    Processes a single log file and returns the summary, task matches, and dataset.
    """
    print(" reached: process_single_log_file")
    summary = {'tasks_summary': {}}
    task_matches = {}
    dataset = []
    checked_logs = 0 # TODO fix this, assign prior
    with open(file_path, 'r', encoding='utf-8') as file:
        log_entries = json.load(file)
        for log in log_entries:
            task_id = log.get('id', 'No ID provided')
            name = log.get('name', 'No task name provided')
            task_key = f"{name} (ID: {task_id})"
            summary['tasks_summary'].setdefault(task_key, 0)
            summary['tasks_summary'][task_key] += 1

            stdout_text = "\n".join(log.get('stdout_lines', []))
            matches_list = check_log_entry(log.get('stdout_lines', []), compiled_patterns)
            checked_logs +=1
            if checked_logs % 100 == 0 and checked_logs>= 100:
                print(checked_logs)
            if matches_list:
                task_matches.setdefault(task_key, defaultdict(set))
                for match in matches_list:
                    # benennung angleichen, is main & subcategory TODO
                    error_cluster, error_type, pattern = match
                    task_matches[task_key][(error_cluster, error_type, pattern)].add(stdout_text)
                for (error_cluster, error_type, pattern), log_entries in task_matches[task_key].items():
                    dataset.append((task_id, "\n".join(log_entries), error_cluster, error_type))

    return summary, task_matches, dataset, checked_logs

def process_log_files(directory_path, compiled_patterns):
    """
    Processes all log files in the given directory and returns the summary, file matches, and dataset.
    """
    print(" reached: format_log_files")
    final_summary = {'tasks_summary': {}}
    file_matches = {}
    all_dataset = []

    for filename in filter(lambda f: f.endswith('.json'), os.listdir(directory_path)):
        file_path = os.path.join(directory_path, filename)
        summary, task_matches, dataset, checked_logs = process_single_file(file_path, compiled_patterns)

        for task_key, count in summary['tasks_summary'].items():
            final_summary['tasks_summary'].setdefault(task_key, 0)
            final_summary['tasks_summary'][task_key] += count

        if task_matches:
            file_matches[file_path] = task_matches
            
        all_dataset.extend(dataset)

    return all_dataset, checked_logs



def format_summary_to_screen_width(summary, terminal_width=150):
    """
    Formats the summary dictionary to fit the given terminal width.
    """
    print(" reached: format_summary_to_screeen")
    formatted_summary = ""
    for key, value in summary.items():
        if isinstance(value, dict):
            formatted_summary += f"{key}:\n"
            for sub_key, sub_value in value.items():
                wrapped_sub_value = textwrap.fill(str(sub_value), terminal_width - 4)
                formatted_summary += f"  {sub_key}: {wrapped_sub_value}\n"
        else:
            wrapped_value = textwrap.fill(str(value), terminal_width)
            formatted_summary += f"{key}: {wrapped_value}\n"
        formatted_summary += "-" * terminal_width + "\n"
    return formatted_summary

def format_file_matches(file_matches, terminal_width=150):
    """
    Formats the file matches dictionary to fit the given terminal width.
    """
    print(" reached: format_file_matches")
    formatted_matches = ""
    for file_path, tasks in file_matches.items():
        formatted_matches += f"File: {file_path}\n"
        for task_key, matches in tasks.items():
            formatted_matches += f"  Task: {task_key}\n"
            for (error_cluster, error_type, pattern), log_entries in matches.items():
                formatted_matches += f"    Error Cluster: {error_cluster}, Error Type: {error_type or error_cluster}, Pattern: {pattern}\n"
        formatted_matches += "-" * terminal_width + "\n"
    return formatted_matches

def main():
    # Restructure the patterns first
    print(" reached: main")
    restructured_infra_patterns = restructure_patterns(INFRA_PATTERNS)
    restructured_build_patterns = restructure_patterns(BUILD_PATTERNS)

    # Compile the restructured patterns
    compiled_infra_patterns = compile_patterns(restructured_infra_patterns)
    compiled_build_patterns = compile_patterns(restructured_build_patterns)

    # Combine all compiled patterns
    all_compiled_patterns = {**compiled_infra_patterns, **compiled_build_patterns}

    # Process log files
    directory_path = 'preprocessed_logs'
    dataset, checked_logs = process_log_files(directory_path, all_compiled_patterns)

    # Save the dataset
    dataset_df = pd.DataFrame(dataset, columns=['task_id', 'log_entry', 'error_cluster', 'error_type'])
    dataset_df.to_csv('labeled_dev_dataset.csv', index=True)
    # print(dataset)
    return dataset_df, checked_logs

dataset, checked_logs = main()

print("done")