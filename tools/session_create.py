"""
AgentBay Session Creation Tool
"""
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.agentbay_client import get_agentbay_client
from utils.validators import validate_image_id
from utils.logger import get_logger

# Create logger instance
logger = get_logger(__name__)


class SessionCreateTool(Tool):
    """AgentBay Session Creation Tool"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create new AgentBay session

        Args:
            tool_parameters: Tool parameters

        Yields:
            ToolInvokeMessage: Execution result message
        """
        logger.info("Starting session creation tool execution")
        try:
            # Get parameters
            image_id = tool_parameters.get('image_id', 'linux_latest')
            logger.info(f"Tool parameters: image_id={image_id}")

            # Parameter validation
            if not validate_image_id(image_id):
                logger.warning(f"Invalid image type: {image_id}")
                yield self.create_text_message(f"❌ Invalid image type: {image_id}")
                yield self.create_text_message("Supported image types: linux_latest, browser_latest, code_latest, windows_latest, mobile_latest")
                return

            # Get AgentBay client
            logger.info("Getting AgentBay client")
            client = get_agentbay_client(self.runtime.credentials)

            # Create session (automatically add dify_plugin label)
            logger.info(f"Calling client to create session: image_id={image_id}")
            result = client.create_session(image_id=image_id)
            
            if result.success:
                session_info = result.data
                logger.info(f"Session created successfully, returning user message: session_id={session_info['session_id']}")

                # Success message
                success_message = f"""✅ Session Created Successfully!

📋 Session Information:
• Session ID: {session_info['session_id']}
• Environment Type: {session_info['image_id']}
• Status: {session_info['status']}
• Request ID: {session_info['request_id']}

🎯 Next Steps:
You can now use the following tools to operate this session:
• command_execute - Execute shell commands
• file_operations - File operations
• code_execute - Code execution
• browser_automation - Browser automation
• ui_operations - UI automation

You can open the following link to preview the resource's visual interface:
[Access Preview Page]({session_info['resource_url']})
"""

                yield self.create_text_message(success_message)

                # Return JSON format session info (for other tools to use)
                yield self.create_json_message(session_info)

                # Return variables (for workflow use)
                yield self.create_variable_message("session_id", session_info['session_id'])
                yield self.create_variable_message("image_id", session_info['image_id'])

            else:
                logger.error(f"Session creation failed: {result.error}")
                error_message = f"""❌ Session Creation Failed

🔍 Error Message: {result.error}

💡 Suggestions:
• Check if API key is correctly configured
• Verify network connection is stable
• Confirm image type is supported
"""
                yield self.create_text_message(error_message)

        except Exception as e:
            logger.error(f"Exception occurred while creating session: {str(e)}", exc_info=True)
            yield self.create_text_message(f"❌ Exception occurred while creating session: {str(e)}")
