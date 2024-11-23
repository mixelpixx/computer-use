import platform
from datetime import datetime

SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilizing a Windows {platform.machine()} PC.
* You can use Windows CMD commands and PowerShell.
* GUI applications can be launched directly.
* Screen automation is handled through PyAutoGUI.
* The current date is {datetime.today().strftime('%A, %B %d, %Y').lstrip("0").replace(" 0", " ")}.
</SYSTEM_CAPABILITY>
"""
