# Preprocess logs
import json
import os
import shutil

def clear_directory(directory_path):
    """
    Clears all files in the specified directory.
    """
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

def extract_error_info_from_file(json_file_path):
    """
    Extracts error information from the specified JSON log file.
    
    Args:
        json_file_path (str): The path to the JSON log file.
        
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
    
    Args:
        directory_path (str): The path to the directory containing log files.
        output_directory (str): The path to the directory where processed files will be saved.
        
    Returns:
        list: A list of dictionaries containing all extracted error information.
    """
    all_error_info = []
    os.makedirs(output_directory, exist_ok=True)
    clear_directory(output_directory)
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

def summarize_error_info(error_info_list):
    """
    Summarizes the extracted error information.
    
    Args:
        error_info_list (list): A list of dictionaries containing error information.
        
    Returns:
        dict: A summary of the error information.
    """
    summary = {'total_errors_found': len(error_info_list), 'tasks_summary': {}}
    for error in error_info_list:
        task_id = error.get('id', 'No ID provided')
        name = error.get('name', 'No task name provided')
        task_key = f"{name} (ID: {task_id})"
        summary['tasks_summary'].setdefault(task_key, 0)
        summary['tasks_summary'][task_key] += 1
    return summary

def format_summary_to_screen_width(summary, terminal_width=150):
    """
    Formats the summary to fit the specified screen width.
    
    Args:
        summary (dict): The summary to format.
        terminal_width (int): The width of the terminal.
        
    Returns:
        str: The formatted summary.
    """
    formatted_summary = ""
    for key, value in summary.items():
        formatted_summary += f"{key}:\n"
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                formatted_summary += f"  {sub_key}: {sub_value}\n"
        else:
            formatted_summary += f"  {value}\n"
        formatted_summary += "-" * terminal_width + "\n"
    return formatted_summary

# Usage:
logs_directory_path = 'logs'
output_directory_path = 'preprocessed_logs'

error_info_list = save_error_info(logs_directory_path, output_directory_path)
