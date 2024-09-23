"""
A simple script to download a specified object from an S3 bucket.
It requires the boto3 python library to be present in the current environment.
Any version should suffice.
To install the library in a venv in a Unix environment, the following commands can be run:
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip3 install boto3
The python script can then be run like the following:
python download_new_rand_objects.py --***REMOVED*** '***REMOVED***'  --***REMOVED*** '***REMOVED***' --bucket_name 'ddad-ci-ai-build-failure-extraction-test' --num_files 10
To count files in a dir in Unix: 
    ls -1 | wc -l
"""

import argparse
import boto3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(configuration):
    # Initialise the client
    s3 = boto3.client(
        "s3",
        ***REMOVED***=configuration.***REMOVED***,
        ***REMOVED***=configuration.***REMOVED***,
    )

    # Ensure the directory "logs" exists
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Generating a list of all objects in increments of 1000 (list_objects_v2 returns 1000 max.)
    actually_all_objects = []
    start_after_key = ""
    while True: 
        response = s3.list_objects_v2(Bucket=configuration.bucket_name, StartAfter= start_after_key)
        all_objects = [obj['Key'] for obj in response.get('Contents', [])]
        if not all_objects:
            logging.error("No more objects found in the bucket.")
            break
        start_after_key = all_objects[-1]
        actually_all_objects.extend(all_objects)


    # Choosing defined number of objects from actually_all_objects
    chosen_objects = set()
    object_iterator = iter(actually_all_objects)
    while len(chosen_objects) < configuration.num_files:
        current_object = next(object_iterator, "end")
        # If not enough new objects in bucket:
        if current_object == "end":
            logging.warning(f"only {len(chosen_objects)} objects found")
            break
        # Does log exist in datasets or preprocessed already? (Yes: skip, No: add to chosen_objects)
        preprocessed_filepath = os.path.join("preprocessed_logs", os.path.basename(current_object))
        datasets_filepath = os.path.join("datasets", os.path.basename(current_object))
        if not os.path.exists(preprocessed_filepath) or os.path.exists(datasets_filepath):          # TODO: check once if path correct split/joined!
            chosen_objects.add(current_object)


    # Download chosen_objects
    for obj in chosen_objects:
        preprocessed_filepath = os.path.join("logs", os.path.basename(obj))
        logging.info(f"Downloading {obj} to {preprocessed_filepath}")
        s3.download_file(configuration.bucket_name, obj, preprocessed_filepath)


def parse_input_arguments():
    parser = argparse.ArgumentParser(description="Inputs for script")
    parser.add_argument("--***REMOVED***", help="Service account access key ID")
    parser.add_argument(
        "--***REMOVED***", help="Service account access key secret"
    )
    parser.add_argument(
        "--bucket_name", help="The name of the bucket to download files from"
    )
    parser.add_argument(
        "--num_files", type=int, default=20, help="Number of files to download"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    configuration = parse_input_arguments()
    main(configuration)