from dataclasses import dataclass
import os
import platform

@dataclass
class ToolConfig:
    temp_dir: str = os.path.join(os.getenv('TEMP', os.path.expanduser('~')), 'app_temp')
    output_dir: str = os.path.join(os.getenv('TEMP', os.path.expanduser('~')), 'app_outputs')
    
    def __post_init__(self):
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
