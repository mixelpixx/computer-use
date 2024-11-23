import os
import platform

CACHE_DIR = os.path.join(os.getenv('TEMP', 'C:\\Temp'), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

...rest of the code...
