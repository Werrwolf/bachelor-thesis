# Preprocess logs
import json
import os
import shutil

def clean_directory(directory_path, datasets_path, no_matches_file):
    """
    Clears files in the directory if a corresponding CSV file exists in the datasets
    directory or the file is not listed in no_matches_list.txt.
    Args:
        directory_path (str): Path to the directory to be cleared.
        datasets_path (str): Path to the datasets directory containing CSV files.
        no_matches_file (str): Path to the file containing names of files to be kept.
    """
    # Load the no_matches_list.txt
    with open(no_matches_file, 'r') as f:
        no_matches_list = f.read().splitlines()
    
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        csv_file_path = os.path.join(datasets_path, f"{os.path.splitext(filename)[0]}.csv")
        
        if os.path.isfile(file_path) or os.path.islink(file_path):
            if os.path.exists(csv_file_path) and filename not in no_matches_list:
                os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

# Example usage
# clear_directory('path/to/your/directory', 'path/to/datasets', 'path/to/no_matches_list.txt')


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
    clean_directory(directory_path, datasets_path, no_matches_file)
    for filename in filter(lambda f: f.endswith('.json'), os.listdir(directory_path)):
        file_path = os.path.join(directory_path, filename)
        error_info = extract_error_info_from_file(file_path)
        all_error_info.extend(error_info)
        if error_info:
            new_filename = f"{os.path.splitext(filename)[0]}_cropped.json"
            new_file_path = os.path.join(output_directory, new_filename)
            with open(new_file_path, 'w', encoding='utf-8') as new_file:
                json.dump(error_info, new_file, indent=4)
    return all_error_info

# Usage:
logs_directory_path = 'logs'
output_directory_path = 'preprocessed_logs'
directory_path = 'preprocessed_logs'
datasets_path='datasets'
no_matches_file='no_matches_list.txt'

error_info_list = save_error_info(logs_directory_path, output_directory_path)