from dataclasses import dataclass
import os
import platform

@dataclass
class ToolConfig:
    temp_dir: str = os.path.join(os.getenv('TEMP', 'C:\\Temp'))
    output_dir: str = os.path.join(os.getenv('TEMP', 'C:\\Temp'), 'outputs')
    
    def ensure_dirs(self):
        os.makedirs(self.output_dir, exist_ok=True)
