# Preprocess logs
import json
import os
import shutil

# Usage:
SOURCE_DIR = 'logs'
TARGET_DIR = 'preprocessed_logs'
DATASET_DIR='datasets'
NO_MATCHES_FILE='no_matches_list.txt'

def clean_directory(no_matches_file):
    # Load the no_matches_list.txt
    with open(no_matches_file, 'r') as f:
        no_matches_list = f.read().splitlines()
    counter=0
    files_to_process = []
    
    # check all files
    for file in os.listdir(SOURCE_DIR):

        # Build paths
        base_filename = os.path.splitext(file)[0]
        log_filepath = os.path.join(SOURCE_DIR, file)    # TODO check 
        preprocessed_filepath = os.path.join(TARGET_DIR, f"{base_filename}_cropped.json")
        datasets_filepath = os.path.join(DATASET_DIR, f"{base_filename}_cropped.csv")        
        """
        Deletes files if:
        - a corresponding CSV file exists in the datasets (already processed earlier)
        Skip files if:
        - file in preprocessed_logs already (do not need to process again)
        Process file if:
        - neither 
        """
        if os.path.isfile(log_filepath):  # Check if it's a file
            # If the corresponding dataset CSV exists, delete the log file
            if os.path.exists(datasets_filepath) and file not in no_matches_list:
                os.unlink(log_filepath)
                print(f"Deleted log file {log_filepath} as corresponding dataset exists.")

            # If preprocessed version already exists, skip it
            elif os.path.exists(preprocessed_filepath):
                os.unlink(log_filepath)
                print(f"Skipping {log_filepath} as a preprocessed version already exists.")

            # Otherwise, the file needs to be processed
            else:
                print(f"{log_filepath} will be processeed")  # TODO: implement / change code so it achtually is processed!
                files_to_process.append(log_filepath)
                counter += 1
        # For safety
        else: 
            print(f"{log_filepath} does not exist.")
    print(f"Files to process: {counter}")
    return files_to_process

# # Example usage
# clean_directory(NO_MATCHES_FILE)
# print("check completed")

def extract_error_info_from_file(json_file_path):
    """
    Extracts error information from the specified JSON log file.        
    Returns:
        list: A list of dictionaries containing error information.
    """
    error_info_list = []
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        for item in data:
            for play in item.get('plays', []):
                for task in play.get('tasks', []):
                    task_info = task.get('task', {})
                    task_id = task_info.get('id', 'No ID provided')
                    task_name = task_info.get('name', 'No task name provided')
                    for node, host_info in task.get('hosts', {}).items():
                        if host_info.get('failed'):
                            error_info = {
                                'node': node,
                                'stderr': host_info.get('stderr', ''),
                                'stdout_lines': host_info.get('stdout_lines', []),
                                'id': task_id,
                                'name': task_name
                            }
                            # Logging for diagnostic purposes
                            if task_id == 'No ID provided':
                                print(f"Missing ID in task: {task_info}")
                            if task_name == 'No task name provided':
                                print(f"Missing Name in task: {task_info}")
                            error_info_list.append(error_info)
    except Exception as e:
        print(f"An error occurred while processing {json_file_path}: {e}")
    return error_info_list

def save_error_info(directory_path, output_directory):
    """
    Processes all log files in the specified directory, extracts error information,
    and saves the information to new files in the output directory.    
    Returns:
        list: A list of dictionaries containing all extracted error information.
    """
    all_error_info = []
    os.makedirs(output_directory, exist_ok=True)
    files_to_process = clean_directory(NO_MATCHES_FILE)
    for filename in files_to_process:
        file_path = os.path.join(directory_path, filename)
        error_info = extract_error_info_from_file(file_path)
        all_error_info.extend(error_info)
        if error_info:
            new_filename = f"{os.path.splitext(filename)[0]}_cropped.json"
            new_file_path = os.path.join(output_directory, new_filename)
            with open(new_file_path, 'w', encoding='utf-8') as new_file:
                json.dump(error_info, new_file, indent=4)
    return all_error_info


error_info_list = save_error_info(SOURCE_DIR, TARGET_DIR)
# should be 0 if run repeatedly