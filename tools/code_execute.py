"""
AgentBay Code Execution Tool - Using Native API
"""
from collections.abc import Generator
from typing import Any
import time

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.agentbay_client import get_agentbay_client
from utils.validators import validate_session_id
from utils.logger import get_logger

# Create logger instance
logger = get_logger(__name__)


class CodeExecuteTool(Tool):
    """AgentBay Code Execution Tool - Using Native API"""

    # Supported programming languages
    SUPPORTED_LANGUAGES = {
        'python': 'Python',
        'javascript': 'JavaScript/Node.js',
        'java': 'Java',
        'go': 'Go',
        'bash': 'Bash Shell',
        'cpp': 'C++',
        'c': 'C',
        'php': 'PHP',
        'ruby': 'Ruby',
        'rust': 'Rust'
    }
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute code in session using AgentBay native API

        Args:
            tool_parameters: Tool parameters

        Yields:
            ToolInvokeMessage: Execution result message
        """
        logger.info("Starting code execution tool")
        try:
            # Get required parameters
            session_id = tool_parameters.get('session_id', '')
            language = tool_parameters.get('language', 'python')
            code = tool_parameters.get('code', '')

            logger.info(f"Tool parameters: session_id={session_id}, language={language}, code_length={len(code)}")

            # Parameter validation
            if not session_id:
                logger.warning("session_id parameter missing")
                yield self.create_text_message("❌ Error: session_id parameter is required")
                return

            if not validate_session_id(session_id):
                logger.warning(f"Invalid session ID format: {session_id}")
                yield self.create_text_message(f"❌ Error: Invalid session ID format: {session_id}")
                return

            if not code:
                logger.warning("code parameter missing")
                yield self.create_text_message("❌ Error: code parameter is required")
                return

            if language not in self.SUPPORTED_LANGUAGES:
                logger.warning(f"Unsupported programming language: {language}")
                yield self.create_text_message(f"❌ Error: Unsupported programming language: {language}")
                yield self.create_text_message(f"Supported languages: {', '.join(self.SUPPORTED_LANGUAGES.keys())}")
                return

            # Get AgentBay client
            logger.info("Getting AgentBay client")
            client = get_agentbay_client(self.runtime.credentials)

            # Show execution info
            yield self.create_text_message(f"🔄 Executing {self.SUPPORTED_LANGUAGES[language]} code...")
            yield self.create_text_message(f"📋 Session ID: {session_id}")
            yield self.create_text_message(f"💻 Language: {language}")

            # Record start time
            start_time = time.time()

            # Execute code using AgentBay native API
            logger.info(f"Calling client to execute code: session_id={session_id}, language={language}")
            result = client.run_code(
                session_id=session_id,
                code=code,
                language=language
            )

            # Calculate execution time
            execution_time = time.time() - start_time
            logger.info(f"Code execution completed: took {execution_time:.2f} seconds")

            if result.success:
                result_data = result.data
                logger.info(f"Code executed successfully: session_id={session_id}, language={language}")

                success_message = f"""✅ Code Executed Successfully!

📊 Execution Info:
• Session ID: {session_id}
• Programming Language: {self.SUPPORTED_LANGUAGES[language]}
• Execution Time: {execution_time:.2f} seconds

📤 Execution Result:
{result_data.get('result', '(no output)')}
"""

                # Also show error output if exists
                if result_data.get('error'):
                    success_message += f"\n⚠️ Error Output:\n{result_data['error']}"

                yield self.create_text_message(success_message)

                # Return JSON format result
                yield self.create_json_message({
                    'session_id': session_id,
                    'language': language,
                    'result': result_data.get('result', ''),
                    'output': result_data.get('output', result_data.get('result', '')),
                    'error': result_data.get('error'),
                    'execution_time': execution_time
                })

                # Return variables (for workflow use)
                yield self.create_variable_message("code_output", result_data.get('output', result_data.get('result', '')))
                yield self.create_variable_message("code_success", "true")

            else:
                logger.error(f"Code execution failed: session_id={session_id}, language={language}, error={result.error}")
                error_message = f"""❌ Code Execution Failed

📋 Session ID: {session_id}
💻 Language: {self.SUPPORTED_LANGUAGES[language]}
⏱️ Execution Time: {execution_time:.2f} seconds
🔍 Error Message: {result.error}

💡 Suggestions:
• Check if session exists and is available
• Verify code syntax is correct
• Confirm session image supports this programming language
• Check network connection is stable
"""
                yield self.create_text_message(error_message)

                # Return failure result
                yield self.create_json_message({
                    'session_id': session_id,
                    'language': language,
                    'error': result.error,
                    'execution_time': execution_time,
                    'success': False
                })

                yield self.create_variable_message("code_success", "false")

        except Exception as e:
            logger.error(f"Exception occurred while executing code: {str(e)}", exc_info=True)
            yield self.create_text_message(f"❌ Exception occurred while executing code: {str(e)}")
