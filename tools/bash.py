import asyncio
import os
from typing import ClassVar, Literal

from anthropic.types.beta import BetaToolBash20241022Param

from .base import BaseAnthropicTool, CLIResult, ToolError, ToolResult
from .debug import tool_logger, log_performance


class _BashSession:
    """A session of a Windows command prompt."""

    _started: bool
    _process: asyncio.subprocess.Process

    command: str = "cmd.exe"
    _output_delay: float = 0.2  # seconds
    _timeout: float = 120.0  # seconds
    _sentinel: str = "END_OF_COMMAND"

    def __init__(self):
        self._started = False
        self._timed_out = False

    @log_performance
    async def start(self):
        if self._started:
            return

        try:
            self._process = await asyncio.create_subprocess_shell(
                self.command,
                shell=True,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            tool_logger.info(f"Started Windows command prompt process: {self._process.pid}")
        except Exception as e:
            tool_logger.error(f"Failed to start Windows command prompt: {str(e)}")
            raise ToolError(f"Failed to start Windows command prompt: {str(e)}")

        self._started = True

    def stop(self):
        """Terminate the command prompt."""
        if not self._started:
            raise ToolError("Session has not started.")
        if self._process.returncode is not None:
            return
        self._process.terminate()
        tool_logger.info("Terminated Windows command prompt process")

    async def run(self, command: str):
        """Execute a command in the command prompt."""
        if not self._started:
            raise ToolError("Session has not started.")
        if self._process.returncode is not None:
            tool_logger.error(f"Command prompt exited with code {self._process.returncode}")
            return ToolResult(
                system="tool must be restarted",
                error=f"command prompt has exited with returncode {self._process.returncode}",
            )
        if self._timed_out:
            raise ToolError(
                f"timed out: command prompt has not returned in {self._timeout} seconds and must be restarted",
            )

        # we know these are not None because we created the process with PIPEs
        assert self._process.stdin
        assert self._process.stdout
        assert self._process.stderr

        # send command to the process
        self._process.stdin.write(
            command.encode() + f" && echo {self._sentinel}\n".encode()
        )
        await self._process.stdin.drain()

        # read output from the process, until the sentinel is found
        try:
            async with asyncio.timeout(self._timeout):
                while True:
                    await asyncio.sleep(self._output_delay)
                    # if we read directly from stdout/stderr, it will wait forever for
                    # EOF. use the StreamReader buffer directly instead.
                    output = self._process.stdout._buffer.decode()  # pyright: ignore[reportAttributeAccessIssue]
                    if self._sentinel in output:
                        # strip the sentinel and break
                        output = output[: output.index(self._sentinel)]
                        break
        except asyncio.TimeoutError:
            self._timed_out = True
            raise ToolError(
                f"timed out: command prompt has not returned in {self._timeout} seconds and must be restarted",
            ) from None

        if output.endswith("\n"):
            output = output[:-1]

        error = self._process.stderr._buffer.decode()  # pyright: ignore[reportAttributeAccessIssue]
        if error.endswith("\n"):
            error = error[:-1]

        # clear the buffers so that the next output can be read correctly
        self._process.stdout._buffer.clear()  # pyright: ignore[reportAttributeAccessIssue]
        self._process.stderr._buffer.clear()  # pyright: ignore[reportAttributeAccessIssue]

        return CLIResult(output=output, error=error)


class BashTool(BaseAnthropicTool):
    """
    A tool that allows the agent to run Windows command prompt commands.
    The tool parameters are defined by Anthropic and are not editable.
    """

    _session: _BashSession | None
    name: ClassVar[Literal["bash"]] = "bash"
    api_type: ClassVar[Literal["bash_20241022"]] = "bash_20241022"

    def __init__(self):
        self._session = None
        super().__init__()

    async def __call__(
        self, command: str | None = None, restart: bool = False, **kwargs
    ):
        if restart:
            if self._session:
                self._session.stop()
            self._session = _BashSession()
            await self._session.start()

            return ToolResult(system="tool has been restarted.")

        if self._session is None:
            self._session = _BashSession()
            await self._session.start()

        if command is not None:
            return await self._session.run(command)

        raise ToolError("no command provided.")

    def to_params(self) -> BetaToolBash20241022Param:
        return {
            "type": self.api_type,
            "name": self.name,
        }
