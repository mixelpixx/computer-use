import subprocess
from typing import ClassVar

class BashTool:
    command: str = "cmd.exe"
    
    def execute(self, command: str):
        command = command.replace('/', '\\')
        command = f'cmd /c {command}'
        subprocess.run(command, shell=True)
