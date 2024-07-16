"""Utilities for interacting with GitHub."""
import json
import requests
import time


ATTEMPT_AFTER_SECONDS = 0, 10, 30


def create_comment(url, message):
    """Create a comment sending a POST request."""
    data = dict(body=message)
    print(
        f'Starting POST request to {url} with data:\n'
        f'{json.dumps(data, indent=2)}'
    )

    response = None
    for attempt, delay in enumerate(ATTEMPT_AFTER_SECONDS, start=1):

        time.sleep(delay)
        response = requests.post(url, json=data)

        print(f'POST request finished with status code {response.status_code}.')

        if response.status_code < 400:
            break

        print(f'Attempt {attempt} failed.')
    else:
        print('All attempts failed.')

    # will have a value in all executed paths:
    response.raise_for_status()