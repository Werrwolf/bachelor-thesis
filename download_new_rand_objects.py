"""
A simple script to download a specified object from an S3 bucket.
It requires the boto3 python library to be present in the current environment.
Any version should suffice.

To install the library in a venv in a Unix environment, the following commands can be run:

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip3 install boto3
```

The python script can then be run like the following:

```
python download_new_rand_objects.py --***REMOVED*** '***REMOVED***'  --***REMOVED*** '***REMOVED***' --bucket_name 'ddad-ci-ai-build-failure-extraction-test' --num_files 10
```

Extra reading:
- https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-download-file.html
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/download_file.html
"""

import argparse
import boto3
import os
import random
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

    # List all objects in the bucket
    response = s3.list_objects_v2(Bucket=configuration.bucket_name)
    all_objects = [obj['Key'] for obj in response.get('Contents', [])]

    if not all_objects:
        logging.error("No objects found in the bucket.")
        return

    # Randomly choose a predefined amount of objects
    chosen_objects = set()
    while len(chosen_objects) < configuration.num_files:
        random_object = random.choice(all_objects)
        local_file_path = os.path.join("logs", os.path.basename(random_object))
        if not os.path.exists(local_file_path):
            chosen_objects.add(random_object)

    # Download the chosen objects
    for obj in chosen_objects:
        local_file_path = os.path.join("logs", os.path.basename(obj))
        logging.info(f"Downloading {obj} to {local_file_path}")
        s3.download_file(configuration.bucket_name, obj, local_file_path)


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