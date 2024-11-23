import asyncio
import base64
import os
import pyautogui
import shutil
from typing import Optional

class ComputerTool(BaseAnthropicTool):
    def __init__(self):
        super().__init__()
        pyautogui.FAILSAFE = True
        self.screen_size = pyautogui.size()
         
    async def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        screenshot.save(os.path.join(self.config.temp_dir, "screenshot.png"))
         
    async def click(self, x: int, y: int):
        pyautogui.click(x=x, y=y)

...rest of the code...
