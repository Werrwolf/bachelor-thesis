import json
import re
import os
import pandas as pd
from collections import defaultdict


INPUT_DIR = 'preprocessed_logs'
OUTPUT_DIRECTORY = 'datasets'
BLACKLIST = 'blacklist.txt'

def load_pattern(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def compile_patterns(patterns):
    """	
    Compiles the restructured patterns dictionary into a dictionary of compiled regex patterns.	
    """	
    compiled_patterns = {}	
    for main_category, subpatterns in patterns.items():	
        for sub_category, patterns in subpatterns.items():	
            compiled_patterns.setdefault((main_category, sub_category), []).extend([re.compile(pattern) for pattern in patterns])	
    return compiled_patterns


def load_blacklist_file():
    with open (BLACKLIST, "a") as file : 
        return file 


def purge_log_lines(log_entries, cutoff_intervall = 1000):
    """
    Purges log lines to keep only the start and end intervals if the log is too long.
    """
    if len(log_entries) < 2*cutoff_intervall:
        return log_entries
    start_intervall = log_entries[:cutoff_intervall]
    end_intervall = log_entries[-cutoff_intervall:]
    return start_intervall + end_intervall


def check_purged_log(log_entries, compiled_patterns):
    purged_log_entries = purge_log_lines(log_entries, 1000)
    matches_list = []
    for log_entry in purged_log_entries:
        for (main_category, sub_category), regex_list in compiled_patterns.items():
            for pattern in regex_list:
                match = pattern.search(log_entry)
                if match:
                    matches_list.append((main_category, sub_category, match))
    return matches_list


def check_full_log(log_entries, compiled_patterns):
    matches_list = []
    for log_entry in log_entries:
        for (main_category, sub_category), regex_list in compiled_patterns.items():
            for pattern in regex_list:
                match = pattern.search(log_entry)
                if match:
                    matches_list.append((main_category, sub_category, match))
    return matches_list


def process_single_file(directory_path, filename, compiled_patterns):
    """
    Processes a single log file and returns a dateset with task_id, log entries, main_category, sub_category.
    """
    dataset = []
    task_matches = {}
    file_path = os.path.join(directory_path, filename)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            log_entries = json.load(file)
            for log in log_entries:
                task_id = log.get('id', 'No ID provided')
                name = log.get('name', 'No task name provided')
                task_key = f"{name} (ID: {task_id})"

                stdout_text = "\n".join(log.get('stdout_lines', []))

                # check shortened log version, returns 'none' if no match found in short version
                matches_list = check_purged_log(log.get('stdout_lines', []), compiled_patterns)
                if matches_list:
                    task_matches.setdefault(task_key, defaultdict(set))
                    for match in matches_list:
                        main_category, sub_category, pattern = match
                        task_matches[task_key][(main_category, sub_category, pattern)].add(stdout_text)
                    for (main_category, sub_category, pattern), log_entries in task_matches[task_key].items():
                        dataset.append((task_id, "\n".join(log_entries), main_category, sub_category))
                else: 
                    # check full version
                    matches_list = check_full_log(task_key, defaultdict(set))

                    if matches_list:
                        task_matches.setdefault(task_key, defaultdict(set))
                        for match in matches_list:
                            main_category, sub_category, pattern = match
                            task_matches[task_key][(main_category, sub_category, pattern)].add(stdout_text)
                        for (main_category, sub_category, pattern), log_entries in task_matches[task_key].items():
                            dataset.append((task_id, "\n".join(log_entries), main_category, sub_category))
                    # still no matches? Theres a unknown error, label as such and proceed
                    else:
                        isthisadict ={}
                        isthisadict.setdefault(task_id, defaultdict(set))
                        for log_entry in log_entries:
                            dataset.append((task_id, stdout_text, "Unknown error", "Unknown error"))

    except json.JSONDecodeError:
        with open(BLACKLIST, 'a') as blacklist:
            blacklist.write("\n")
            blacklist.write(filename)
        os.remove(file_path)
        print(f"Error decoding JSON file {filename}, File has been deleted and added to the blacklist.")
        return None, None, None
    
    if dataset:
        output_file_name = os.path.splitext(filename)[0] + ".csv"
        output_path = os.path.join("datasets", output_file_name)
        dataset_df = pd.DataFrame(dataset, columns=['task_id', 'log_line', 'main_category', 'sub_category'])
        return output_path, output_file_name, dataset_df
    
    else:
        return None, None, None
    

def process_all_files(directory_path, compiled_patterns):
    """
    Processes all log files in the given directory, saving each one as a separate .csv in "datasets".
    Skips processing if the corresponding file already exists.
    """
    files = [f for f in os.listdir(directory_path) if f.endswith('.json')]

    for file in files:
        output_file_name = os.path.splitext(file)[0] + ".csv"
        output_path = os.path.join(OUTPUT_DIRECTORY, output_file_name)
        file_path = os.path.join(directory_path, file)
        with open(BLACKLIST, 'r') as blacklist:
            if os.path.exists(output_path) or file in blacklist: 
                os.remove(file_path)
                print(f"Deleted {file}, corresponding CSV dataset already exists or log was blacklisted previously.")
                continue
                
            # Process file
            output_path, output_file_name, dataset_df = process_single_file(directory_path, file, compiled_patterns)
            if dataset_df is not None:
                dataset_df.to_csv(output_path, index=False)
                os.remove(file_path)
                print(f"Processed and saved: {output_file_name}")
            else:
                print('dataset_df is None')
    return 


def main():
    """
    Main function to restructure, compile patterns and process log files.
    """
    # Compile the restructured patterns
    all_patterns = load_pattern("patterns.json")
    compiled_patterns = compile_patterns(all_patterns)

    # Process log files
    process_all_files(INPUT_DIR, compiled_patterns)

# Run the main function
if __name__ == '__main__':
    main()
