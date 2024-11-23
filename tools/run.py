import subprocess

def run(command: str, timeout: float = 120.0):
    # Handle Windows paths and commands
    if '/' in command:
        command = command.replace('/', '\\')
    
    if not command.startswith('cmd'):
        command = f'cmd /c {command}'
        
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr
