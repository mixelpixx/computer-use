import platform
from datetime import datetime
from enum import Enum

class APIProvider(Enum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"

PROVIDER_TO_DEFAULT_MODEL_NAME = {
    APIProvider.ANTHROPIC: "claude-2",
    APIProvider.BEDROCK: "amazon.titan-tg1-large",
    APIProvider.VERTEX: "text-bison",
}

SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilizing a Windows {platform.machine()} PC.
* You can use Windows CMD commands and PowerShell.
* GUI applications can be launched directly.
* Screen automation is handled through PyAutoGUI.
* The current date is {datetime.today().strftime('%A, %B %d, %Y').lstrip("0").replace(" 0", " ")}.
</SYSTEM_CAPABILITY>
"""
