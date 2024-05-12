import re
import json

with open('responses.json', 'r', encoding='utf-8') as f:
    responses = json.load(f)

for i, response in enumerate(responses):
    text = response['new']
    cleaned_text = re.sub('^(?:.|\\n)*?```python\\n', '', text)
    cleaned_text = re.sub('```(?:.|\n)*$', '', cleaned_text)
    response['new'] = cleaned_text

with open('response_cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(responses, f, indent=4)
