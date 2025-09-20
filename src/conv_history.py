import json

def message_history_to_string(msgs):
    new_str = json.dumps(msgs)
    return new_str

def string_to_message_history(s):
    json_object = json.loads(s)
    return json_object

