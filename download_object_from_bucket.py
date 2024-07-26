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
python3 download_object_from_bucket.py \
   --***REMOVED*** '***REMOVED***' \
   --***REMOVED*** '***REMOVED***' \
   --bucket_name 'ddad-ci-ai-build-failure-extraction-test' \
   --object_to_download '0000595bdf9db15a5679c0268c4d7311105336398528c42e2263b7d3935c8922__job-output.json' \
   --output_file 'out.json'
```

Extra reading:
- https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-download-file.html
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/download_file.html
"""

import argparse
import boto3


def main(configuration):
    # Initialise the client
    s3 = boto3.client(
        "s3",
        ***REMOVED***=configuration.***REMOVED***,
        ***REMOVED***=configuration.***REMOVED***,
    )

    # Download a particular file in a particular bucket to an output_file
    s3.download_file(
        configuration.bucket_name,
        configuration.object_to_download,
        configuration.output_file,
    )


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
        "--object_to_download",
        help="The specific object to download from the above bucket",
    )
    parser.add_argument(
        "--output_file", help="The file to output the downloaded object to"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    configuration = parse_input_arguments()
    main(configuration)