import asyncio
import os
import platform

async def run(command: str, timeout: float = 120.0):
    if platform.system() == 'Windows':
        command = command.replace('/', '\\')
        command = f'cmd /c {command}' if not command.startswith('cmd') else command
    
    process = await asyncio.create_subprocess_shell(
        command,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
