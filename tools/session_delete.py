"""
AgentBay Session Deletion Tool
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


class SessionDeleteTool(Tool):
    """AgentBay Session Deletion Tool"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Delete existing AgentBay session

        Args:
            tool_parameters: Tool parameters

        Yields:
            ToolInvokeMessage: Execution result message
        """
        logger.info("Starting session deletion tool execution")
        try:
            # Get parameters
            session_id = tool_parameters.get('session_id', '')
            sync_context = tool_parameters.get('sync_context', False)

            logger.info(f"Tool parameters: session_id={session_id}, sync_context={sync_context}")

            # Parameter validation
            if not session_id:
                logger.warning("session_id parameter missing")
                yield self.create_text_message("❌ Error: session_id parameter is required")
                return

            if not validate_session_id(session_id):
                logger.warning(f"Invalid session ID format: {session_id}")
                yield self.create_text_message(f"❌ Error: Invalid session ID format: {session_id}")
                return

            # Get AgentBay client
            logger.info("Getting AgentBay client")
            client = get_agentbay_client(self.runtime.credentials)

            # Show deletion warning
            yield self.create_text_message(f"⚠️ Preparing to delete session: {session_id}")
            if sync_context:
                yield self.create_text_message("🔄 Will synchronize context data before deletion...")

            # Delete session
            logger.info(f"Calling client to delete session: session_id={session_id}")
            result = client.delete_session(session_id, sync_context=sync_context)

            if result.success:
                logger.info(f"Session deleted successfully: session_id={session_id}")
                delete_info = result.data
                
                # Success message
                success_message = f"""✅ Session Deleted Successfully!

📋 Deletion Information:
• Session ID: {delete_info['session_id']}
• Deletion Status: {delete_info['deleted']}
• Context Sync: {'Yes' if sync_context else 'No'}

🎯 Cleanup Complete:
Session and its related resources have been permanently deleted
"""
                
                yield self.create_text_message(success_message)
                
                # Return JSON format deletion info (for other tools to use)
                yield self.create_json_message(delete_info)
                
                # Return variables (for workflow use)
                yield self.create_variable_message("deleted_session_id", delete_info['session_id'])
                yield self.create_variable_message("deletion_success", "true")
                
            else:
                logger.error(f"Session deletion failed: session_id={session_id}, error={result.error}")
                error_message = f"""❌ Session Deletion Failed

🔍 Error Message: {result.error}

💡 Suggestions:
• Check if session ID is correct
• Verify session still exists
• Confirm API key has permission to delete this session
• Check network connection
"""
                yield self.create_text_message(error_message)

        except Exception as e:
            logger.error(f"Exception occurred while deleting session: {str(e)}", exc_info=True)
            yield self.create_text_message(f"❌ Exception occurred while deleting session: {str(e)}")
