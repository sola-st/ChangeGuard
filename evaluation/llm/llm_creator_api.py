import atexit
import json

from openai import OpenAI

try:
    with open('responses.json', 'r', encoding='utf-8') as f:
        responses = json.load(f)
except (json.decoder.JSONDecodeError, FileNotFoundError):
    responses = []

p_tokens = 0
r_tokens = 0
price_per_p_token = 10 / 1_000_000
price_per_r_token = 30 / 1_000_000


def save():
    with open('responses.json', 'w', encoding='utf-8') as f:
        json.dump(responses, f, indent=4)
        print('Prompt Tokens:', p_tokens)
        print('Response Tokens:', r_tokens)
        print(f'Cost: {p_tokens * price_per_p_token + r_tokens * price_per_r_token}' )


atexit.register(save)

with open('../../LExecutorCC/annotated_changes.json', 'r', encoding='utf-8') as f:
    functions = json.load(f)
functions = [entry['new_clean_function'] for entry in functions]

with open('./.secret', 'r', encoding='utf-8') as f:
    secret = f.read().splitlines()
client = OpenAI(api_key=secret[0], organization=secret[1])
system = ""
prompt = 'You are a Python expert, improve the quality of this Python code while preserving its behavior and without renaming variables, adding comments, adding a docstring, or adding imports:'
for idx, function in enumerate(functions[len(responses):], start=len(responses)):

    text = prompt + '\n' + function
    response = client.chat.completions.create(
        messages=[
            #{'role': 'system', 'content': system},
            {'role': 'user', 'content': text}
        ],
        #response_format={"type": "json_object"},
        #model='gpt-3.5-turbo-0125'
        model='gpt-4-turbo-2024-04-09'

    )
    print(response.choices[0].finish_reason)
    p_tokens += response.usage.prompt_tokens
    r_tokens += response.usage.completion_tokens
    responses.append({
        'old': function,
        'new': response.choices[0].message.content})



