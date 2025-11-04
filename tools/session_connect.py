"""
AgentBay Session Connection Tool
"""
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.agentbay_client import get_agentbay_client
from utils.validators import validate_session_id
from utils.logger import get_logger

# Create logger instance
logger = get_logger(__name__)

# Temporarily not needed as session_create automatically connects to session
class SessionConnectTool(Tool):
    """AgentBay Session Connection Tool"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Connect to existing AgentBay session
        
        Args:
            tool_parameters: Tool parameters
            
        Yields:
            ToolInvokeMessage: Execution result message
        """
        try:
            # Get parameters
            session_id = tool_parameters.get('session_id', '')
            
            # Parameter validation
            if not session_id:
                yield self.create_text_message("❌ Error: session_id parameter is required")
                return
                
            if not validate_session_id(session_id):
                yield self.create_text_message(f"❌ Error: Invalid session ID format: {session_id}")
                return
            
            # Get AgentBay client
            client = get_agentbay_client(self.runtime.credentials)
            
            # Connect to session
            result = client.get_session_info(session_id)
            
            if result.success:
                session_info = result.data
                
                # Success message
                success_message = f"""✅ Session Connected Successfully!

📋 Session Information:
• Session ID: {session_info['session_id']}
• Environment Type: {session_info['image_id']}
• Status: {session_info['status']}

🎯 Session Available:
You can now use the following tools to operate this session:
• command_execute - Execute shell commands
• file_read/file_write - File operations
• code_execute - Code execution
"""
                
                yield self.create_text_message(success_message)
                
                # Return JSON format session info (for other tools to use)
                yield self.create_json_message(session_info)
                
                # Return variables (for workflow use)
                yield self.create_variable_message("session_id", session_info['session_id'])
                yield self.create_variable_message("session_status", session_info['status'])
                
            else:
                error_message = f"""❌ Session Connection Failed

🔍 Error Message: {result.error}

💡 Suggestions:
• Check if session ID is correct
• Verify session still exists
• Confirm API key has permission to access this session
• Check network connection
"""
                yield self.create_text_message(error_message)
                
        except Exception as e:
            yield self.create_text_message(f"❌ Exception occurred while connecting to session: {str(e)}")
