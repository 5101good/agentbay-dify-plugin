"""
AgentBay Unified File Operations Tool - Integrating File Read, Write, and Directory List Functions
"""
from collections.abc import Generator
from typing import Any
import time

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.agentbay_client import LightweightAgentBayClient, get_agentbay_client
from utils.validators import validate_session_id, sanitize_content
from utils.logger import get_logger

# Create logger instance
logger = get_logger(__name__)


class FileOperationsTool(Tool):
    """AgentBay Unified File Operations Tool - Integrating File Read, Write, and Directory List Functions"""

    # Supported file operation types
    SUPPORTED_ACTIONS = {
        'read': 'Read file',
        'write': 'Write file',
        'list': 'List directory contents'
    }

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute unified file operation

        Args:
            tool_parameters: Tool parameters

        Yields:
            ToolInvokeMessage: Execution result message
        """
        try:
            # Get basic parameters
            session_id = tool_parameters.get('session_id', '')
            action = tool_parameters.get('action', 'read')

            # Parameter validation
            if not session_id:
                yield self.create_text_message("❌ Error: session_id parameter is required")
                return

            if not validate_session_id(session_id):
                yield self.create_text_message(f"❌ Error: Invalid session ID format: {session_id}")
                return

            if action not in self.SUPPORTED_ACTIONS:
                yield self.create_text_message(f"❌ Error: Unsupported operation type: {action}")
                yield self.create_text_message(f"Supported operations: {', '.join(self.SUPPORTED_ACTIONS.keys())}")
                return

            # Get operation-specific parameters
            operation_params = self._get_operation_params(tool_parameters, action)

            # Validate operation-specific parameters
            validation_result = self._validate_operation_params(action, operation_params)
            if validation_result:
                yield self.create_text_message(validation_result)
                return

            # Get AgentBay client
            client = get_agentbay_client(self.runtime.credentials)

            # Show operation info
            yield self.create_text_message(f"📁 Executing file operation: {self.SUPPORTED_ACTIONS[action]}")
            yield self.create_text_message(f"📋 Session ID: {session_id}")

            # Show specific operation parameters
            for message in self._show_operation_details(action, operation_params):
                yield message

            # Record start time
            start_time = time.time()

            # Execute specific operation
            result = self._execute_file_operation(
                client, session_id, action, operation_params
            )

            # Calculate operation time
            operation_time = time.time() - start_time

            if result.success:
                # Build success message
                success_message = self._build_success_message(
                    action, session_id, operation_time, result.data
                )
                yield self.create_text_message(success_message)

                # Return JSON format result
                response_data = {
                    'session_id': session_id,
                    'action': action,
                    'success': True,
                    'operation_time': operation_time
                }
                response_data.update(result.data or {})

                yield self.create_json_message(response_data)

                # Return variables (for workflow use)
                yield self.create_variable_message("file_action", action)
                yield self.create_variable_message("file_operation_success", "true")

                # Specific operation variables
                for message in self._set_action_variables(action, result.data):
                    yield message

            else:
                # Build error message
                error_message = self._build_error_message(
                    action, session_id, operation_time, result.error
                )
                yield self.create_text_message(error_message)

                # Return failure result
                yield self.create_json_message({
                    'session_id': session_id,
                    'action': action,
                    'success': False,
                    'error': result.error,
                    'operation_time': operation_time
                })

                yield self.create_variable_message("file_operation_success", "false")

        except Exception as e:
            yield self.create_text_message(f"❌ Exception occurred during file operation: {str(e)}")

    def _get_operation_params(self, tool_parameters: dict[str, Any], action: str) -> dict[str, Any]:
        """Get operation-specific parameters"""
        params = {}

        if action in ['read', 'write']:
            params['file_path'] = tool_parameters.get('file_path', '')

        if action == 'write':
            params['content'] = tool_parameters.get('content', '')

        if action == 'list':
            params['directory_path'] = tool_parameters.get('directory_path', '.')

        return params

    def _validate_operation_params(self, action: str, params: dict[str, Any]) -> str:
        """Validate operation-specific parameters, return error message or empty string"""
        if action in ['read', 'write']:
            if not params.get('file_path'):
                return f"❌ Error: {action} operation requires file_path parameter"

        if action == 'write':
            # content can be empty string, so no validation here
            pass

        return ""

    def _show_operation_details(self, action: str, params: dict[str, Any]):
        """Show operation details"""
        messages = []
        if action in ['read', 'write']:
            messages.append(self.create_text_message(f"📄 File path: {params['file_path']}"))

        if action == 'write':
            content_size = len(params['content'])
            messages.append(self.create_text_message(f"📊 Content size: {content_size} bytes"))

        if action == 'list':
            messages.append(self.create_text_message(f"📂 Directory path: {params['directory_path']}"))

        return messages

    def _execute_file_operation(self, client: LightweightAgentBayClient, session_id: str, action: str, params: dict[str, Any]):
        """Execute specific file operation"""
        try:
            if action == 'read':
                return client.read_file(session_id, params['file_path'])

            elif action == 'write':
                content = params['content']
                return client.write_file(session_id, params['file_path'], content)

            elif action == 'list':
                return client.list_directory(session_id, params['directory_path'])

            else:
                from utils.agentbay_client import SimpleResult
                return SimpleResult(
                    success=False,
                    error=f"Unsupported operation: {action}"
                )

        except Exception as e:
            from utils.agentbay_client import SimpleResult
            return SimpleResult(
                success=False,
                error=f"Failed to execute {action} operation: {str(e)}"
            )

    def _build_success_message(self, action: str, session_id: str, operation_time: float, data: dict) -> str:
        """Build success message"""
        message = f"""✅ File {self.SUPPORTED_ACTIONS[action]} Successful!

📊 Operation Info:
• Session ID: {session_id}
• Operation Type: {self.SUPPORTED_ACTIONS[action]}
• Operation Time: {operation_time:.2f} seconds"""

        # Add operation-specific information
        if action == 'read' and data:
            file_path = data.get('file_path')
            file_size = data.get('size', 0)
            content = data.get('content', '')

            if file_path:
                message += f"\n• File Path: {file_path}"
            if file_size:
                message += f"\n• File Size: {file_size} bytes"

            # Show content preview
            if content:
                preview = content[:500] if len(content) > 500 else content
                if len(content) > 500:
                    preview += "\n... (content truncated, see JSON output for complete content)"
                message += f"\n\n📄 File Content:\n{preview}"

        elif action == 'write' and data:
            file_path = data.get('file_path')
            file_size = data.get('size', 0)

            if file_path:
                message += f"\n• File Path: {file_path}"
            if file_size:
                message += f"\n• Written Size: {file_size} bytes"

        elif action == 'list' and data:
            directory_path = data.get('directory_path')
            files = data.get('files', [])
            count = data.get('count', 0)

            if directory_path:
                message += f"\n• Directory Path: {directory_path}"
            message += f"\n• File Count: {count}"

            if count > 0:
                # Show file list preview
                files_display = []
                for file_info in files[:10]:  # Show first 10 files
                    if isinstance(file_info, dict):
                        name = file_info.get('name', 'unknown')
                        file_type = file_info.get('type', 'unknown')
                        if file_type == 'directory':
                            files_display.append(f"📁 {name}/")
                        else:
                            size = file_info.get('size', 0)
                            files_display.append(f"📄 {name} ({size} bytes)")
                    else:
                        files_display.append(f"📄 {str(file_info)}")

                if len(files) > 10:
                    files_display.append(f"... and {len(files) - 10} more files")

                message += f"\n\n📋 File List:\n" + "\n".join(files_display)

        return message

    def _build_error_message(self, action: str, session_id: str, operation_time: float, error: str) -> str:
        """Build error message"""
        return f"""❌ File {self.SUPPORTED_ACTIONS[action]} Failed

📋 Session ID: {session_id}
🎯 Operation Type: {self.SUPPORTED_ACTIONS[action]}
⏱️ Operation Time: {operation_time:.2f} seconds
🔍 Error Message: {error}

💡 Suggestions:
• Check if session exists and is available
• Verify file/directory path is correct
• Confirm appropriate permissions
• Check network connection is stable"""

    def _set_action_variables(self, action: str, data: dict):
        """Set operation-specific variables"""
        messages = []
        if action == 'read' and data:
            content = data.get('content')
            if content:
                # Limit variable length
                var_content = content[:1000] if len(content) > 1000 else content
                messages.append(self.create_variable_message("file_content", var_content))

            file_size = data.get('size')
            if file_size is not None:
                messages.append(self.create_variable_message("file_size", str(file_size)))

        elif action == 'write' and data:
            file_path = data.get('file_path')
            if file_path:
                messages.append(self.create_variable_message("written_file_path", file_path))

            file_size = data.get('size')
            if file_size is not None:
                messages.append(self.create_variable_message("written_file_size", str(file_size)))

        elif action == 'list' and data:
            directory_path = data.get('directory_path')
            if directory_path:
                messages.append(self.create_variable_message("listed_directory", directory_path))

            count = data.get('count')
            if count is not None:
                messages.append(self.create_variable_message("directory_file_count", str(count)))

        return messages