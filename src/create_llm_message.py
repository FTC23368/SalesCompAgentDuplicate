from langchain_core.messages import SystemMessage, BaseMessage

def create_llm_msg(system_prompt: str, messageHistory: list[BaseMessage]):
    resp = []
    resp.append(SystemMessage(content=system_prompt))
    resp.extend(messageHistory)
    return resp