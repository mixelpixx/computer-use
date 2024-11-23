import asyncio
import base64
import os
import pyautogui
import shutil
from ctypes import windll
from typing import Optional

class ComputerTool(BaseAnthropicTool):
    def __init__(self):
        super().__init__()
        pyautogui.FAILSAFE = True
        # Get actual Windows screen size
        user32 = windll.user32
        self.screen_size = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
         
    async def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        screenshot.save(os.path.join(self.config.temp_dir, "screenshot.png"))
         
    async def click(self, x: int, y: int):
        pyautogui.click(x=x, y=y)

    async def type(self, text: str):
        pyautogui.typewrite(text)

    async def press(self, keys: str):
        pyautogui.press(keys)

    async def move_mouse(self, x: int, y: int):
        pyautogui.moveTo(x, y)

    async def scroll(self, amount: int):
        pyautogui.scroll(amount)

    async def get_clipboard(self) -> Optional[str]:
        try:
            return pyautogui.paste()
        except:
            return None

    async def set_clipboard(self, text: str):
        pyautogui.copy(text)

    async def open_file(self, file_path: str):
        os.startfile(file_path)

    async def open_url(self, url: str):
        import webbrowser
        webbrowser.open(url)

    async def delete_file(self, file_path: str):
        os.remove(file_path)

    async def delete_directory(self, dir_path: str):
        shutil.rmtree(dir_path)

    async def create_directory(self, dir_path: str):
        os.makedirs(dir_path, exist_ok=True)

    async def list_directory(self, dir_path: str) -> list:
        return os.listdir(dir_path)

    async def read_file(self, file_path: str) -> str:
        with open(file_path, 'r') as file:
            return file.read()

    async def write_file(self, file_path: str, content: str):
        with open(file_path, 'w') as file:
            file.write(content)

    async def encode_file(self, file_path: str) -> str:
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')

    async def decode_file(self, base64_str: str, file_path: str):
        with open(file_path, 'wb') as file:
            file.write(base64.b64decode(base64_str.encode('utf-8')))
