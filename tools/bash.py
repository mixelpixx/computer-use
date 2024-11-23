import asyncio
import os
import subprocess
from typing import ClassVar

class BashTool:
    command: str = "cmd.exe" if os.name == 'nt' else "/bin/bash"
    
    async def start(self):
        self._process = await asyncio.create_subprocess_shell(
            self.command,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
