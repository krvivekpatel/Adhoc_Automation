import re

def callback(message):
    try:
        m = message.decode("utf-8")
        if not re.search(r"(?i)CMIT|QA", m):
            return ("[JIRA-123] " + m).encode("utf-8")
        return message
    except Exception as e:
        with open("filter_error.log", "a") as f:
            f.write(f"Error processing commit: {e}\n")
        return message
