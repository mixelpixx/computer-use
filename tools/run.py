import subprocess

def run(command: str, timeout: float = 120.0):
    command = command.replace('/', '\\')
    command = f'cmd /c {command}' if not command.startswith('cmd') else command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()
