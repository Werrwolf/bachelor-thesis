
import json
file = 'label_mapping.json'

with open ('label_mapping.json') as f:
    label_mapping=json.load(f)

print(label_mapping)
