import json
import re
import os
import extract_build_failures.error_patterns as error_patterns
import pandas as pd
from collections import defaultdict

INFRA_PATTERNS = error_patterns.INFRA_PATTERNS
BUILD_PATTERNS = error_patterns.BUILD_PATTERNS
LOG_DIRECTORY = 'preprocessed_logs'
OUTPUT_DIRECTORY = 'datasets'


def restructure_patterns(patterns):
    """
    Restructures the input patterns dictionary to a more structured format.
    """
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
    compiled_patterns = {}
    for main_category, subpatterns in patterns_dict.items():
        for sub_category, patterns in subpatterns.items():
            compiled_patterns.setdefault((main_category, sub_category), []).extend([re.compile(pattern) for pattern in patterns])
    return compiled_patterns


def purge_log_lines(log_entries, cutoff_intervall = 1000):
    """
    Purges log lines to keep only the start and end intervals if the log is too long.
    """
    if len(log_entries) < 2*cutoff_intervall:
        return log_entries
    start_intervall = log_entries[:cutoff_intervall]
    end_intervall = log_entries[-cutoff_intervall:]
    return start_intervall + end_intervall


def check_log_entry(log_entries, compiled_patterns):
    purged_log_entries = purge_log_lines(log_entries, 1000)
    matches_list = []
    for log_entry in purged_log_entries:
        for (main_category, sub_category), regex_list in compiled_patterns.items():
            for pattern in regex_list:
                match = pattern.search(log_entry)
                if match:
                    matches_list.append((main_category, sub_category, match))
    return matches_list


def process_single_file(directory_path, filename, compiled_patterns):
    """
    Processes a single log file and returns the summary, task matches, and dataset.
    """
    dataset = []
    task_matches = {}
    file_path = os.path.join(directory_path, filename)

    with open(file_path, 'r', encoding='utf-8') as file:
        log_entries = json.load(file)
        for log in log_entries:
            task_id = log.get('id', 'No ID provided')
            name = log.get('name', 'No task name provided')
            task_key = f"{name} (ID: {task_id})"

            stdout_text = "\n".join(log.get('stdout_lines', []))
            matches_list = check_log_entry(log.get('stdout_lines', []), compiled_patterns)
            if matches_list:
                task_matches.setdefault(task_key, defaultdict(set))
                for match in matches_list:
                    error_cluster, error_type, pattern = match
                    task_matches[task_key][(error_cluster, error_type, pattern)].add(stdout_text)
                for (error_cluster, error_type, pattern), log_entries in task_matches[task_key].items():
                    dataset.append((task_id, "\n".join(log_entries), error_cluster, error_type))
    
    output_file_name = os.path.splitext(filename)[0] + ".csv"
    output_path = os.path.join("datasets", output_file_name)
    dataset_df = pd.DataFrame(dataset, columns=['task_id', 'log_line', 'main_category', 'sub_category'])
    return output_path, output_file_name, dataset_df


def process_all_files(directory_path, compiled_patterns):
    """
    Processes all log files in the given directory, saving each one as a separate .csv in "datasets".
    Skips processing if the corresponding file already exists.
    """
    files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True) 

    for file in files:
        output_file_name = os.path.splitext(file)[0] + ".csv"
        output_path = os.path.join(OUTPUT_DIRECTORY, output_file_name)
        
        if os.path.exists(output_path):
            print(f"Skipping {file}, corresponding CSV already exists.")
            continue
        
        _, output_file_name, dataset_df = process_single_file(directory_path, file, compiled_patterns)
        dataset_df.to_csv(output_path, index=False)
        print(f"Processed and saved: {output_file_name}")


def main():
    """
    Main function to restructure, compile patterns and process log files.
    """
    restructured_infra_patterns = restructure_patterns(INFRA_PATTERNS)
    restructured_build_patterns = restructure_patterns(BUILD_PATTERNS)

    # Compile the restructured patterns
    compiled_infra_patterns = compile_patterns(restructured_infra_patterns)
    compiled_build_patterns = compile_patterns(restructured_build_patterns)

    # Combine all compiled patterns
    all_compiled_patterns = {**compiled_infra_patterns, **compiled_build_patterns}

    # Process log files
    process_all_files(LOG_DIRECTORY, all_compiled_patterns)

    print("Processing complete")

# Run the main function
if __name__ == '__main__':
    main()
