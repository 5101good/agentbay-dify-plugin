"""
AgentBay Mobile Device UI Operations Tool - Mobile Device Interaction and Automation
"""
from collections.abc import Generator
from typing import Any
import time
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.agentbay_client import get_agentbay_client
from utils.validators import validate_session_id
from utils.logger import get_logger

# Create logger instance
logger = get_logger(__name__)


class MobileOperationsTool(Tool):
    """AgentBay Mobile Device UI Operations Tool - Provides Touch, Input and UI Element Operations"""

    # Supported operation types
    SUPPORTED_ACTIONS = {
        'tap': 'Tap',
        'swipe': 'Swipe',
        'input_text': 'Input text',
        'send_key': 'Send key',
        'screenshot': 'Screenshot',
        'get_clickable_elements': 'Get clickable elements',
        'get_all_elements': 'Get all UI elements'
    }

    # Mobile device key codes
    KEY_CODES = {
        'home': 3,
        'back': 4,
        'volume_up': 24,
        'volume_down': 25,
        'power': 26,
        'menu': 82
    }

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute mobile device UI operations using AgentBay Mobile API

        Args:
            tool_parameters: Tool parameters

        Yields:
            ToolInvokeMessage: Execution result message
        """
        logger.info("Starting mobile device UI operation execution")
        try:
            # Get parameters
            session_id = tool_parameters.get('session_id', '')
            action = tool_parameters.get('action', 'tap')
            
            logger.info(f"Operation parameters: session_id={session_id}, action={action}")

            # Parameter validation
            if not session_id:
                logger.warning("session_id parameter missing")
                yield self.create_text_message("❌ Error: session_id parameter is required")
                return

            if not validate_session_id(session_id):
                logger.warning(f"Invalid session ID format: {session_id}")
                yield self.create_text_message(f"❌ Error: Invalid session ID format: {session_id}")
                return

            if action not in self.SUPPORTED_ACTIONS:
                logger.warning(f"Unsupported operation type: {action}")
                yield self.create_text_message(f"❌ Error: Unsupported operation type: {action}")
                yield self.create_text_message(f"Supported operations: {', '.join(self.SUPPORTED_ACTIONS.keys())}")
                return

            # Validate operation-specific parameters
            validation_result = self._validate_action_params(action, tool_parameters)
            if validation_result:
                logger.warning(f"Parameter validation failed: {validation_result}")
                yield self.create_text_message(validation_result)
                return

            # Get AgentBay client
            logger.info("Getting AgentBay client")
            client = get_agentbay_client(self.runtime.credentials)

            # Show operation info
            yield self.create_text_message(f"📱 Executing mobile device UI operation: {self.SUPPORTED_ACTIONS[action]}")
            yield self.create_text_message(f"📋 Session ID: {session_id}")

            # Record start time
            start_time = time.time()

            # Get Session instance
            logger.info(f"Getting session instance: {session_id}")
            session_result = client.client.get(session_id)
            if not session_result.success:
                logger.error(f"Failed to get session: {session_result.error_message}")
                yield self.create_text_message(f"❌ Failed to get session: {session_result.error_message}")
                return
            
            session = session_result.session
            mobile = session.mobile
            logger.info("Successfully got Mobile instance")

            # Call corresponding API based on operation type
            result = self._execute_action(mobile, action, tool_parameters)

            # Calculate operation time
            operation_time = time.time() - start_time
            logger.info(f"Operation completed: action={action}, took={operation_time:.2f}s, success={result.success}")

            # Handle result
            yield from self._handle_result(result, action, session_id, operation_time, tool_parameters)

        except Exception as e:
            logger.error(f"Exception occurred during mobile device UI operation: {str(e)}", exc_info=True)
            yield self.create_text_message(f"❌ Exception occurred during mobile device UI operation: {str(e)}")

    def _validate_action_params(self, action: str, params: dict) -> str:
        """Validate operation-specific parameters, return error message or empty string"""
        if action == 'tap':
            if params.get('x') is None or params.get('y') is None:
                return "❌ Error: tap operation requires x and y coordinate parameters"
        
        if action == 'swipe':
            if any(params.get(p) is None for p in ['start_x', 'start_y', 'end_x', 'end_y']):
                return "❌ Error: swipe operation requires start_x, start_y, end_x, end_y parameters"
        
        if action == 'input_text':
            if not params.get('text'):
                return "❌ Error: input_text operation requires text parameter"
        
        if action == 'send_key':
            key = params.get('key', '')
            if not key:
                return "❌ Error: send_key operation requires key parameter"
            # Validate key validity
            if key.lower() not in self.KEY_CODES and not isinstance(key, int):
                return f"❌ Error: Invalid key: {key}, supported: {', '.join(self.KEY_CODES.keys())} or numeric key code"
        
        return ""

    def _execute_action(self, mobile, action: str, params: dict):
        """Execute specific operation"""
        logger.info(f"Executing operation: {action}")
        
        try:
            if action == 'tap':
                x = int(params['x'])
                y = int(params['y'])
                logger.debug(f"Tapping screen: x={x}, y={y}")
                return mobile.tap(x=x, y=y)
            
            elif action == 'swipe':
                start_x = int(params['start_x'])
                start_y = int(params['start_y'])
                end_x = int(params['end_x'])
                end_y = int(params['end_y'])
                duration_ms = int(params.get('duration_ms', 300))
                logger.debug(f"Swiping: from=({start_x},{start_y}), to=({end_x},{end_y}), duration={duration_ms}ms")
                return mobile.swipe(start_x=start_x, start_y=start_y, end_x=end_x, end_y=end_y, duration_ms=duration_ms)
            
            elif action == 'input_text':
                text = params['text']
                logger.debug(f"Inputting text: text={text[:50]}...")  # Only log first 50 characters
                return mobile.input_text(text=text)
            
            elif action == 'send_key':
                key = params['key']
                # Convert to key code if string
                if isinstance(key, str):
                    key_code = self.KEY_CODES.get(key.lower())
                    if key_code is None:
                        try:
                            key_code = int(key)
                        except ValueError:
                            key_code = None
                else:
                    key_code = int(key)
                
                if key_code is None:
                    raise ValueError(f"Invalid key: {key}")
                
                logger.debug(f"Sending key: key={key}, key_code={key_code}")
                return mobile.send_key(key=key_code)
            
            elif action == 'screenshot':
                logger.debug("Taking screenshot")
                return mobile.screenshot()
            
            elif action == 'get_clickable_elements':
                timeout_ms = int(params.get('timeout_ms', 2000))
                logger.debug(f"Getting clickable elements: timeout={timeout_ms}ms")
                return mobile.get_clickable_ui_elements(timeout_ms=timeout_ms)
            
            elif action == 'get_all_elements':
                timeout_ms = int(params.get('timeout_ms', 2000))
                logger.debug(f"Getting all UI elements: timeout={timeout_ms}ms")
                return mobile.get_all_ui_elements(timeout_ms=timeout_ms)
            
        except Exception as e:
            logger.error(f"Failed to execute operation: {action}, error={str(e)}", exc_info=True)
            # Return an error result object
            from agentbay.model import BoolResult
            return BoolResult(request_id="", success=False, data=None, error_message=str(e))

    def _handle_result(self, result, action: str, session_id: str, operation_time: float, params: dict) -> Generator[ToolInvokeMessage, None, None]:
        """Handle operation result"""
        if result.success:
            yield from self._handle_success_result(result, action, session_id, operation_time, params)
        else:
            yield from self._handle_error_result(result, action, session_id, operation_time, params)

    def _handle_success_result(self, result, action: str, session_id: str, operation_time: float, params: dict) -> Generator[ToolInvokeMessage, None, None]:
        """Handle success result"""
        logger.info(f"Operation successful: action={action}")
        
        success_message = f"""✅ Mobile Device UI Operation Successful!

📊 Operation Info:
• Session ID: {session_id}
• Operation Type: {self.SUPPORTED_ACTIONS[action]}
• Operation Time: {operation_time:.2f} seconds
"""

        # Add specific information based on operation type
        if action == 'tap':
            success_message += f"• Tap Coordinates: ({params['x']}, {params['y']})"
        elif action == 'swipe':
            success_message += f"• Swiped from ({params['start_x']}, {params['start_y']}) to ({params['end_x']}, {params['end_y']})\n• Duration: {params.get('duration_ms', 300)}ms"
        elif action == 'input_text':
            text_preview = params['text'][:100] + ('...' if len(params['text']) > 100 else '')
            success_message += f"• Input Text: {text_preview}"
        elif action == 'send_key':
            key = params['key']
            key_name = key if isinstance(key, str) else f"key code {key}"
            success_message += f"• Sent Key: {key_name}"
        elif action == 'screenshot':
            screenshot_data = result.data if result.data else None
            if screenshot_data:
                success_message += f"• Screenshot Data: {screenshot_data}"
                # Create image message if URL is returned
                if isinstance(screenshot_data, str) and (screenshot_data.startswith('http://') or screenshot_data.startswith('https://')):
                    yield self.create_image_message(screenshot_data)
        elif action == 'get_clickable_elements':
            if hasattr(result, 'elements') and result.elements:
                element_count = len(result.elements)
                success_message += f"• Found {element_count} clickable elements"
                logger.info(f"Found {element_count} clickable elements")
        elif action == 'get_all_elements':
            if hasattr(result, 'elements') and result.elements:
                element_count = len(result.elements)
                success_message += f"• Found {element_count} UI elements"
                logger.info(f"Found {element_count} UI elements")

        yield self.create_text_message(success_message)

        # Build response data
        response_data = {
            'session_id': session_id,
            'action': action,
            'success': True,
            'operation_time': operation_time
        }

        # Add operation-specific data
        if action == 'tap':
            response_data.update({'x': params['x'], 'y': params['y']})
        elif action == 'swipe':
            response_data.update({
                'start_x': params['start_x'], 'start_y': params['start_y'],
                'end_x': params['end_x'], 'end_y': params['end_y'],
                'duration_ms': params.get('duration_ms', 300)
            })
        elif action == 'input_text':
            response_data['text'] = params['text']
        elif action == 'send_key':
            response_data['key'] = params['key']
        elif action == 'screenshot':
            if result.data:
                response_data['screenshot_data'] = result.data
        elif action in ['get_clickable_elements', 'get_all_elements']:
            if hasattr(result, 'elements') and result.elements:
                # Limit returned element count to avoid excessive data
                max_elements = 50
                elements_to_return = result.elements[:max_elements] if len(result.elements) > max_elements else result.elements
                response_data['elements'] = elements_to_return
                response_data['total_count'] = len(result.elements)
                response_data['truncated'] = len(result.elements) > max_elements

        yield self.create_json_message(response_data)

        # Return variables (for workflow use)
        yield self.create_variable_message("mobile_action", action)
        yield self.create_variable_message("mobile_operation_success", "true")

        if action == 'tap':
            yield self.create_variable_message("tap_x", str(params['x']))
            yield self.create_variable_message("tap_y", str(params['y']))
        elif action == 'screenshot' and result.data:
            if isinstance(result.data, str):
                yield self.create_variable_message("screenshot_url", result.data)
        elif action in ['get_clickable_elements', 'get_all_elements']:
            if hasattr(result, 'elements') and result.elements:
                yield self.create_variable_message("element_count", str(len(result.elements)))

    def _handle_error_result(self, result, action: str, session_id: str, operation_time: float, params: dict) -> Generator[ToolInvokeMessage, None, None]:
        """Handle error result"""
        logger.error(f"Operation failed: action={action}, error={result.error_message}")
        
        error_message = f"""❌ Mobile Device UI Operation Failed

📋 Session ID: {session_id}
📱 Operation Type: {self.SUPPORTED_ACTIONS[action]}
⏱️ Operation Time: {operation_time:.2f} seconds
🔍 Error Message: {result.error_message}

💡 Suggestions:
• Check if session is mobile device type (mobile_latest)
• Verify session exists and is available
• Confirm mobile device is started and connected
• Check if coordinates are within valid range
• Verify UI elements are accessible
"""

        yield self.create_text_message(error_message)

        # Return failure result
        response_data = {
            'session_id': session_id,
            'action': action,
            'success': False,
            'error': result.error_message,
            'operation_time': operation_time
        }

        yield self.create_json_message(response_data)
        yield self.create_variable_message("mobile_operation_success", "false")

