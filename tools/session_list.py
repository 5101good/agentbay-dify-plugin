"""
AgentBay Session List Tool
"""
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.agentbay_client import get_agentbay_client
from utils.logger import get_logger

# Create logger instance
logger = get_logger(__name__)


class SessionListTool(Tool):
    """AgentBay Session List Tool"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        List all available AgentBay sessions

        Args:
            tool_parameters: Tool parameters

        Yields:
            ToolInvokeMessage: Execution result message
        """
        logger.info("Starting session list tool execution")
        try:
            # Get AgentBay client
            logger.info("Getting AgentBay client")
            client = get_agentbay_client(self.runtime.credentials)

            # Get session list
            logger.info("Calling client to list sessions")
            result = client.list_sessions()

            if result.success:
                session_data = result.data
                sessions = session_data['sessions']
                count = session_data['count']
                logger.info(f"Successfully retrieved session list: total {count} sessions")

                # Success message
                if count == 0:
                    success_message = """📋 Session List is Empty

🎯 No Sessions Found:
• No active sessions under current account
• You can use session_create tool to create new sessions
"""
                else:
                    session_list_text = "\n".join([
                        f"• {session['session_id']} - {session['image_id']} ({session['status']}) - Created: {session['created_at']}"
                        for session in sessions
                    ])
                    
                    success_message = f"""📋 Session List (Total: {count})

🎯 Active Sessions:
{session_list_text}

💡 Operation Tips:
• Use command_execute to execute commands in sessions
• Use session_delete to remove unwanted sessions
"""
                
                yield self.create_text_message(success_message)
                
                # Return JSON format session list (for other tools to use)
                yield self.create_json_message(session_data)
                
                # Return variables (for workflow use)
                yield self.create_variable_message("session_count", str(count))
                if count > 0:
                    # Return first session ID as default value
                    yield self.create_variable_message("first_session_id", sessions[0]['session_id'])
                
            else:
                logger.error(f"Failed to get session list: {result.error}")
                error_message = f"""❌ Failed to Get Session List

🔍 Error Message: {result.error}

💡 Suggestions:
• Check if API key is correctly configured
• Verify network connection is stable
• Confirm permission to view session list
"""
                yield self.create_text_message(error_message)

        except Exception as e:
            logger.error(f"Exception occurred while getting session list: {str(e)}", exc_info=True)
            yield self.create_text_message(f"❌ Exception occurred while getting session list: {str(e)}")
