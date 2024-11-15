import openai
import json
import os




def make_request(message, system_msg = None, max_tokens = 220):
    # add sys message if there are any
    # message is already in gpt format, no need to modify it
    if system_msg:
        message.append({"role": "system", "content": f'''{system_msg}'''})

    print("##############################################")
    print(message)
    print("##############################################")
    response = openai.ChatCompletion.create (
    model = "gpt-3.5-turbo",
    messages = message,
    max_tokens = max_tokens
)   
    token_used = response.usage.total_tokens
    ## also return token used this time
    return response.choices[0].message, token_used



def save_history(response, session_id):
    file_name = f"{session_id}.json"
    if not os.path.isfile(file_name):
        with open(file_name, "w") as f:
            json.dump([response],f)
    else:
        with open(file_name, "r+") as f:
            existing_data = json.load(f)
            existing_data.append(response)
            # move the file pointer to the beginning of the file
            f.seek(0)
            json.dump(existing_data, f)


# merge later
def make_request_gpt4(message, system_msg = None, max_tokens = 220):
    if system_msg:
        message.append({"role": "system", "content": f'''{system_msg}'''})

    response = openai.ChatCompletion.create (
    model = "gpt-4-1106-preview",
    messages = message,
    max_tokens = max_tokens
)   
    token_used = response.usage.total_tokens
    ## also return token used this time
    return response.choices[0].message, token_used
