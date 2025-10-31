"""
AgentBay Command Execution Tool
"""
from collections.abc import Generator
from typing import Any
import time

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.agentbay_client import get_agentbay_client
from utils.validators import validate_command, validate_session_id, validate_timeout
from utils.logger import get_logger

# Create logger instance
logger = get_logger(__name__)


class CommandExecuteTool(Tool):
    """AgentBay Command Execution Tool"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute shell command in AgentBay session

        Args:
            tool_parameters: Tool parameters

        Yields:
            ToolInvokeMessage: Execution result message
        """
        logger.info("Starting command execution tool")
        try:
            # Get required parameters
            session_id = tool_parameters.get('session_id', '')
            command = tool_parameters.get('command', '')

            # Get optional parameters
            timeout_ms = tool_parameters.get('timeout_ms', 30000)
            working_directory = tool_parameters.get('working_directory')

            logger.info(f"Tool parameters: session_id={session_id}, command={command[:100]}, timeout={timeout_ms}ms, working_dir={working_directory}")

            # Parameter validation
            if not session_id:
                logger.warning("session_id parameter missing")
                yield self.create_text_message("❌ Error: session_id parameter is required")
                return

            if not validate_session_id(session_id):
                logger.warning(f"Invalid session ID format: {session_id}")
                yield self.create_text_message(f"❌ Error: Invalid session ID format: {session_id}")
                return

            if not command:
                logger.warning("command parameter missing")
                yield self.create_text_message("❌ Error: command parameter is required")
                return

            if not validate_command(command):
                logger.warning(f"Command contains unsafe content: {command[:100]}")
                yield self.create_text_message(f"❌ Security Error: Command contains unsafe content")
                yield self.create_text_message("Please avoid using potentially dangerous commands like: rm -rf, dd, sudo rm, etc.")
                return

            if not validate_timeout(timeout_ms):
                logger.warning(f"Invalid timeout: {timeout_ms}ms")
                yield self.create_text_message(f"❌ Error: Invalid timeout: {timeout_ms}ms")
                yield self.create_text_message("Timeout should be between 1 second and 5 minutes")
                return

            # If working directory specified, combine commands
            if working_directory:
                if command.strip().startswith('cd '):
                    # If command itself is cd, combine paths
                    command = f"cd {working_directory} && {command}"
                else:
                    # Execute command in specified directory
                    command = f"cd {working_directory} && {command}"
                logger.info(f"Command after combining working directory: {command[:100]}")

            # Get AgentBay client
            logger.info("Getting AgentBay client")
            client = get_agentbay_client(self.runtime.credentials)

            # Show execution info
            yield self.create_text_message(f"🔄 Executing command...")
            yield self.create_text_message(f"📋 Session ID: {session_id}")
            yield self.create_text_message(f"💻 Command: {command}")

            # Record start time
            start_time = time.time()

            # Execute command
            logger.info(f"Calling client to execute command: session_id={session_id}, command={command[:100]}")
            result = client.execute_command(
                session_id=session_id,
                command=command,
                timeout_ms=timeout_ms
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            logger.info(f"Command execution completed: took {execution_time:.2f} seconds")

            if result.success:
                command_data = result.data
                logger.info(f"Command executed successfully: session_id={session_id}, exit_code={command_data.get('exit_code', 0)}")

                success_message = f"""✅ Command Executed Successfully!

📊 Execution Info:
• Session ID: {session_id}
• Execution Time: {execution_time:.2f} seconds
• Exit Code: {command_data.get('exit_code', 0)}

📤 Command Output:
{command_data.get('output', '(no output)')}
"""

                # Also show error output if exists
                if command_data.get('error'):
                    success_message += f"\n⚠️ Error Output:\n{command_data['error']}"

                yield self.create_text_message(success_message)

                # Return JSON format result
                yield self.create_json_message({
                    'session_id': session_id,
                    'command': command,
                    'output': command_data.get('output', ''),
                    'error': command_data.get('error'),
                    'exit_code': command_data.get('exit_code', 0),
                    'execution_time': execution_time
                })

                # Return variables (for workflow use)
                yield self.create_variable_message("command_output", command_data.get('output', ''))
                yield self.create_variable_message("exit_code", str(command_data.get('exit_code', 0)))

            else:
                logger.error(f"Command execution failed: session_id={session_id}, error={result.error}")
                error_message = f"""❌ Command Execution Failed

📋 Session ID: {session_id}
💻 Command: {command}
⏱️ Execution Time: {execution_time:.2f} seconds
🔍 Error Message: {result.error}

💡 Suggestions:
• Check if session exists and is available
• Verify command syntax is correct
• Confirm sufficient permissions to execute command
• Check network connection is stable
"""
                yield self.create_text_message(error_message)

        except Exception as e:
            logger.error(f"Exception occurred while executing command: {str(e)}", exc_info=True)
            yield self.create_text_message(f"❌ Exception occurred while executing command: {str(e)}")
