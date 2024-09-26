import json
import os

# with open('label_mapping.json', "r") as file:
#     labels=json.load(file)

# if labels == {}:
#     print("empty dict")
# elif labels:
#     print(f"labels: {labels}")
# elif not labels:
#     print("False")


try:
    with open('label_mapping.json', "r") as f:
        if os.path.exists('label_mapping.json'):
            labels=json.load(f)
            print("file exists and can be used")
        else:
            print("file doeas not exist -> build_label_mapping")
except Exception:
    print("'label-mapping' is empty. Fix it")