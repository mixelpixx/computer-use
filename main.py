import anthropic
import gradio as gr
from typing import List, Dict, Optional, Union
import json
import sys
import os
import markdown
import subprocess
import tempfile
from datetime import datetime
import yaml
from pathlib import Path
import platform
from dotenv import load_dotenv
import winreg  # Windows registry access
import ctypes  # For Windows admin checks
from tools.debug import ui_logger, api_logger, log_system_info, monitor_resources
import traceback

load_dotenv()
    
api_key = os.getenv('ANTHROPIC_API_KEY')
os.environ['ANTHROPIC_API_KEY'] = api_key

class WindowsToolExecutor:
    def __init__(self):
        # Use Windows-style temp directory
        self.temp_dir = tempfile.mkdtemp(dir=os.environ.get('TEMP'))
        self.is_admin = self._check_admin()
        self._setup_windows_paths()
        
    def _check_admin(self) -> bool:
        """Check if the application has admin privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def _setup_windows_paths(self):
        """Setup common Windows paths."""
        self.desktop_path = Path(os.path.expanduser("~/Desktop"))
        self.documents_path = Path(os.path.expanduser("~/Documents"))
        self.downloads_path = Path(os.path.expanduser("~/Downloads"))
        
    def _get_windows_drives(self) -> List[str]:
        """Get available Windows drive letters."""
        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in range(65, 91):  # A-Z
            if bitmask & (1 << (letter - 65)):
                drives.append(chr(letter) + ":\\")
        return drives

    def execute_computer_tool(self, tool_input: Dict) -> Dict:
        """Execute computer-related tools with Windows compatibility."""
        try:
            if tool_input.get("type") == "computer_20241022":
                # Handle Windows-specific computer interactions
                return {"type": "computer_result", "success": True, "output": "Computer action completed"}
                
            elif tool_input.get("type") == "text_editor_20241022":
                # Use Windows path joining and encoding
                content = tool_input.get("content", "")
                temp_file = os.path.join(self.temp_dir, "temp_edit.txt")
                with open(temp_file, "w", encoding='utf-8') as f:
                    f.write(content)
                return {
                    "type": "text_editor_result",
                    "success": True,
                    "file_path": temp_file,
                    "content": content
                }
                
            elif tool_input.get("type") == "bash_20241022":
                # Convert to Windows command prompt commands
                command = self._convert_to_windows_command(tool_input.get("command", ""))
                if self._is_safe_command(command):
                    # Use Windows-specific command execution
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=self.temp_dir,
                        encoding='utf-8',
                        startupinfo=startupinfo
                    )
                    return {
                        "type": "bash_result",
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "error": result.stderr
                    }
                else:
                    return {
                        "type": "bash_result",
                        "success": False,
                        "error": "Command not allowed for security reasons"
                    }
        except Exception as e:
            return {"type": "error", "success": False, "error": str(e)}
    
    def _convert_to_windows_command(self, command: str) -> str:
        """Convert Unix-style commands to Windows command prompt format."""
        # Common command conversions
        conversions = {
            'ls': 'dir',
            'rm': 'del',
            'cp': 'copy',
            'mv': 'move',
            'cat': 'type',
            'clear': 'cls',
            'mkdir': 'md',
            'rmdir': 'rd'
        }
        
        # Split command into parts
        parts = command.split()
        if parts and parts[0] in conversions:
            parts[0] = conversions[parts[0]]
        
        return ' '.join(parts)
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if a Windows command is safe to execute."""
        command = command.lower()
        forbidden = [
            "rmdir /s", "del /f", "format", "reg", "net user",
            "net localgroup", "netsh", "taskkill", "shutdown",
            ">", ">>", "|", "&", ";", "start"
        ]
        return not any(cmd in command for cmd in forbidden)
        
        pass

class ClaudeChat:
    def __init__(self, config_path: Optional[str] = None):
        self.client = anthropic.Anthropic()
        self.conversation_history: List[Dict] = []
        self.tool_executor = WindowsToolExecutor()
        self.config = self._load_config(config_path)
        self.system_prompt = self.config.get("system_prompt", "")
        self.max_tokens = self.config.get("max_tokens", 1024)
        self.temperature = self.config.get("temperature", 0.7)

    def get_claude_response(self, user_input: str) -> str:
        """Process user input and get Claude's response."""
        try:
            ui_logger.info(f"Processing user input: {user_input[:100]}...")
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            response = self.client.beta.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                tools=[
                    {
                        "type": "computer_20241022",
                        "name": "computer",
                        "display_width_px": 1024,
                        "display_height_px": 768,
                        "display_number": 1,
                    },
                    {
                        "type": "text_editor_20241022",
                        "name": "str_replace_editor"
                    },
                    {
                        "type": "bash_20241022",
                        "name": "bash"
                    }
                ],
                messages=self.conversation_history,
                betas=["computer-use-2024-10-22"]
            )
            
            # Handle tool use in a loop
            while response.stop_reason == 'tool_use':
                tool_call = response.content[0].tool_calls[0]
                ui_logger.debug(f"Tool call received: {tool_call}")
                
                # Execute the tool and get the result
                tool_result = self.tool_executor.execute_computer_tool(tool_call)
                ui_logger.debug(f"Tool result: {tool_result}")
                
                # Continue the conversation with the tool result
                self.conversation_history.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })
                self.conversation_history.append({
                    "role": "tool",
                    "content": json.dumps(tool_result),
                    "tool_call_id": tool_call.id
                })
                
                # Get next response
                response = self.client.beta.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    messages=self.conversation_history,
                    tools=[
                        {
                            "type": "computer_20241022",
                            "name": "computer",
                            "display_width_px": 1024,
                            "display_height_px": 768,
                            "display_number": 1,
                        },
                        {
                            "type": "text_editor_20241022",
                            "name": "str_replace_editor"
                        },
                        {
                            "type": "bash_20241022",
                            "name": "bash"
                        }
                    ],
                    betas=["computer-use-2024-10-22"]
                )
            
            # Final response after tools are done
            assistant_message = response.content[0].text if response.content else ""
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return self.format_conversation_history()
            
        except Exception as e:
            ui_logger.error(f"Error processing request: {str(e)}")
            ui_logger.error(traceback.format_exc())
            return f"Error: {str(e)}"

    def format_conversation_history(self) -> str:
        """Format conversation history with markdown support."""
        formatted_chat = []
        for message in self.conversation_history:
            role = "You" if message["role"] == "user" else "Claude"
            content = markdown.markdown(message["content"])
            formatted_chat.append(f"### {role}:\n{content}\n")
        return "\n".join(formatted_chat)

    def clear_history(self) -> str:
        """Clear conversation history."""
        self.conversation_history = []
        return ""

    def update_temperature(self, temp: float) -> None:
        """Update the temperature setting."""
        self.temperature = float(temp)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration with Windows-compatible paths."""
        default_config = {
            "system_prompt": "You are a helpful AI assistant.",
            "temperature": 0.7,
            "max_tokens": 1024,
            "conversation_save_path": os.path.join(os.environ.get('USERPROFILE', ''), 'Documents', 'ClaudeChat')
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return {**default_config, **yaml.safe_load(f)}
        return default_config

    def save_conversation(self) -> str:
        """Save the conversation with Windows-compatible paths."""
        save_dir = Path(self.config["conversation_save_path"])
        save_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = save_dir / f"conversation_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, indent=2)
        
        return str(filename)

    def clear_history(self) -> str:
        """Clear conversation history."""
        self.conversation_history = []
        return ""

    def update_temperature(self, temp: float) -> None:
        """Update the temperature setting."""
        self.temperature = float(temp)
        
        pass

def create_ui() -> gr.Interface:
    # Check Windows version
    windows_version = platform.win32_ver()[0]
    is_windows_11 = windows_version.startswith("10.0") and int(platform.win32_ver()[1].split(".")[2]) >= 22000
    
    # Adjust theme based on Windows version
    theme = gr.themes.Soft() if is_windows_11 else gr.themes.Default()
    
    chat = ClaudeChat()
    
    with gr.Blocks(title="Claude Chat Assistant") as interface:
        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.HTML(
                    label="Chat History",
                )
            with gr.Column(scale=1):
                # Replace Box with a Group of components
                with gr.Group():
                    gr.Markdown("### Settings")
                    temperature = gr.Slider(
                        minimum=0,
                        maximum=1,
                        value=0.7,
                        step=0.1,
                        label="Temperature"
                    )
                    save_button = gr.Button("Save Conversation")
                    
        with gr.Row():
            with gr.Column(scale=4):
                msg = gr.Textbox(
                    label="Your message",
                    lines=3,
                    placeholder="Type your message here..."
                )
                
        with gr.Row():
            with gr.Column(scale=1):
                submit = gr.Button("Send", variant="primary")
            with gr.Column(scale=1):
                clear = gr.Button("Clear History")
        
        # Handle interactions
        submit.click(
            fn=chat.get_claude_response,
            inputs=msg,
            outputs=chatbot
        ).then(
            fn=lambda: "",
            outputs=msg
        )
        
        clear.click(
            fn=chat.clear_history,
            outputs=[chatbot, msg]
        )
        
        temperature.change(
            fn=chat.update_temperature,
            inputs=temperature
        )
        
        save_button.click(
            fn=chat.save_conversation
        )
        
        msg.submit(
            fn=chat.get_claude_response,
            inputs=msg,
            outputs=chatbot
        ).then(
            fn=lambda: "",
            outputs=msg
        )
    
    return interface

if __name__ == "__main__":
    # Set Windows-specific environment variables
    if platform.system() == 'Windows':
        os.environ['GRADIO_SERVER_PORT'] = '7860'
        # Ensure proper encoding for Windows console
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
    
    log_system_info()
    monitor_resources()
    interface = create_ui()
    interface.launch(
        server_name="127.0.0.1",  # Use localhost for Windows
        server_port=7860,
        share=True
    )
