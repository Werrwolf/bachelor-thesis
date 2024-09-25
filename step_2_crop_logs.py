# Preprocess logs
import json
import os
import tqdm

# Usage:
SOURCE_DIR = 'logs'
TARGET_DIR = 'preprocessed_logs'
DATASET_DIR='datasets'
BLACKLIST='blacklist.txt'

def decide_file_handling(blacklist):
    """
    1: Welche files müssen preproc werden?
        - nicht in datasets
        - nicht bereits aussortiert (aus gründen nicht benutzen) -> blacklist.txt
        - nicht in preprocessed_logs
    """
    # Load the blacklist.txt
    with open(blacklist, 'r') as f:
        blacklist = f.read().splitlines()
    files_to_process = []
    
    # check all files
    for file in os.listdir(SOURCE_DIR):
        # Build paths
        base_filename = os.path.splitext(file)[0]
        source_filepath = os.path.join(SOURCE_DIR, file)
        preprocessed_filepath = os.path.join(TARGET_DIR, f"{base_filename}_cropped.json")
        datasets_filepath = os.path.join(DATASET_DIR, f"{base_filename}_cropped.csv")        
        
        if os.path.isfile(source_filepath):
            # does log already exist in any of the other folders?
            # if (os.path.exists(datasets_filepath) or file in blacklist or os.path.exists(preprocessed_filepath)):
            #     os.remove(source_filepath)
            #     print(f"Deleted log file {source_filepath} as the log was either processed or blacklisted previously")
            
            if os.path.exists(datasets_filepath):
                print(f"{source_filepath} was found in 'datasets'.")
                os.remove(source_filepath)
            elif os.path.exists(preprocessed_filepath):
                print(f"{source_filepath} was found in 'preprocessed_logs'.")
                os.remove(source_filepath)
            elif file in blacklist:
                print(f"{source_filepath} was found in 'blacklist'.")
                os.remove(source_filepath)
            # => the file needs to be processed
            else:
                print(f"{source_filepath} will be processeed")
                files_to_process.append(file)
        # catching errors
        else: 
            print(f" There was an issue opening: {source_filepath}")
    return files_to_process


def extract_error_info_from_file(filenameWithExtension):
    """
    Extracts error information from the specified JSON log file.        
    Returns:
        list: A list of dictionaries containing error information.
    """
    log_filepath = os.path.join("logs", filenameWithExtension)    
    error_info_list = []
    try:
        with open(log_filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # data = list of dicts (items)
        # items = dict mit : branch, index, phase, playbook (all strings), plays (list), stats(dict)
        # plays = list of dicts ( u.a. tasks, tasks = list of dicts)
        # tasks = list of dicts of hosts
        # # hosts =  
        for item in data:
            for play in item.get('plays', []):
                for task in play.get('tasks', []):
                    task_info = task.get('task', {})
                    task_id = task_info.get('id', 'No ID provided')
                    for node, host_info in task.get('hosts', {}).items():
                        if host_info.get('failed'):
                            error_info = {
                                'stdout_lines': host_info.get('stdout_lines', []),
                                'id': task_id
                            }
                            # Logging for diagnostic purposes
                            if task_id == 'No ID provided':
                                print(f"Missing ID in task: {task_info}")
                            error_info_list.append(error_info)
    except Exception as e:
        print(f"An error occurred while processing {log_filepath}: {e}")
    return error_info_list

def save_error_info(target_dir):
    """
    Processes all log files in the specified directory, extracts error information,
    and saves the information to new files in the output directory.    
    Returns:
        list: A list of dictionaries containing all extracted error information.
    """     
    all_error_info = []
    os.makedirs(target_dir, exist_ok=True)
    files_to_process = decide_file_handling(BLACKLIST)
    for filename in files_to_process:
        error_info = extract_error_info_from_file(filename)
        all_error_info.extend(error_info)
        if error_info:
            new_filename = f"{os.path.splitext(filename)[0]}_cropped.json"
            new_file_path = os.path.join(target_dir, new_filename)
            with open(new_file_path, 'w', encoding='utf-8') as new_file:
                json.dump(error_info, new_file, indent=4)
            old_path = os.path.join('logs', filename)
            # print(old_path)
            os.remove(old_path)
    return all_error_info


error_info_list = save_error_info(TARGET_DIR)
