import pprint

# Original string (shortened variable name for readability)
raw_data = open('deleteme.json', 'r').read()

# Replace \\n with actual newlines for readability
cleaned_data = raw_data.replace('\\\\n', '\n').replace('\\n', '\n').replace('\\"', '"')

print(cleaned_data)

open('deleteme2.txt', 'w').write(cleaned_data)