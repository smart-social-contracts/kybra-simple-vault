import json

FILE_PATH = r'/workspace/the_project2a/app/tests/scenarios/complete/get_organization_data.json'

content = open(FILE_PATH).read()

with open(FILE_PATH, 'w') as f:
    f.write(json.dumps(json.loads(content), sort_keys=True, indent=4))
