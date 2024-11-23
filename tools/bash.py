import subprocess
from typing import ClassVar

class BashTool:
    def execute(self, command: str):
        # Execute Windows commands directly
        if not command.startswith('cmd'):
            command = f'cmd /c {command}'
        subprocess.run(command, shell=True)
