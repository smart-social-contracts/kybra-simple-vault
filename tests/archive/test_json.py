from test_utils import parse_dfx_answer

content = open(r'/workspace/the_project2a/app/tests/scenarios/json/dfx_get_tokens.txt').read()
gotten = parse_dfx_answer(content)

expected = ''

import ggg.utils as utils
print(utils.compare_json(expected, gotten))



# import os
# import json
# import sys
# import ast

# '''
# dfx canister call canister_main get_universe
# dfx canister call canister_main run_code "$(cat tests/scenarios/complete/extension.py)"
# '''

# def validate_json_files(directory):
#     # Check if the directory exists
#     if not os.path.isdir(directory):
#         print(f"Error: '{directory}' is not a valid directory")
#         return

#     # Iterate through all files in the directory
#     for filename in os.listdir(directory):
#         # if filename != 'dfx_get_universe.txt':
#         #     continue

#         filepath = os.path.join(directory, filename)
        
#         # Skip directories
#         if not os.path.isfile(filepath):
#             continue

#         # Try to read file contents
#         try:
#             with open(filepath, 'r', encoding='utf-8') as f:
#                 content = f.read()
#         except UnicodeDecodeError:
#             print(f"⛔ {filename}: Not a text file (binary or encoding issue)")
#             continue
#         except Exception as e:
#             print(f"⚠️ {filename}: Error reading file - {str(e)}")
#             continue

#         # Try to parse JSON
#         try:
#             # print('content', content)
#             if 'dfx' in filename:
#                 content = content.strip()[2:-2].strip(",").strip().strip('"')
#                 content = content.replace('\\"', '"')
#                 content = content.replace('\\\\', '\\')
#                 content = content.replace("\\'", "'")
#                 # print('content', content)
#                 json.loads(content)
#             else:
#                 json.loads(content)
#             print(f"✅ {filename}: Valid JSON")
#         except json.JSONDecodeError as e:
#             print(f"❌ {filename}: Invalid JSON - {str(e)}")
#         except Exception as e:
#             print(f"⚠️ {filename}: Unexpected error - {str(e)}")

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python json_validator.py <directory>")
#         sys.exit(1)
    
#     target_directory = sys.argv[1]
#     validate_json_files(target_directory)