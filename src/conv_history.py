import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

def message_history_to_string(msgs):
    new_str = json.dumps(msgs)
    return new_str

def string_to_message_history(s):
    json_object = json.loads(s)
    return json_object

def get_short_conv_title(client, conv):
    prompt = "Create a short title for this conversation"
    messages = [
        SystemMessage(prompt),
        HumanMessage(f"{conv}"),
    ]

    response = client.invoke(messages)
    return response.content
