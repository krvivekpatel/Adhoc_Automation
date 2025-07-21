import re

def callback(message):
    m = message.decode("utf-8")
    if not re.search(r"(?i)CMIT|QA", m):  # case-insensitive search
        return "[JIRA-123] " + m
    return m
