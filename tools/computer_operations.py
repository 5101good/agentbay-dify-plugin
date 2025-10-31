"""
AgentBay Desktop UI Operations Tool - Desktop Computer Interaction and Automation
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


class ComputerOperationsTool(Tool):
    """AgentBay Desktop UI Operations Tool - Provides Mouse, Keyboard and Screen Operations"""

    # Supported operation types
    SUPPORTED_ACTIONS = {
        'click_mouse': 'Click mouse',
        'move_mouse': 'Move mouse',
        'drag_mouse': 'Drag mouse',
        'scroll': 'Scroll',
        'input_text': 'Input text',
        'press_keys': 'Press keys',
        'screenshot': 'Screenshot',
        'get_screen_size': 'Get screen size',
        'get_cursor_position': 'Get cursor position'
    }

    # Mouse button types
    MOUSE_BUTTONS = ['left', 'right', 'middle', 'double_left']
    
    # Scroll directions
    SCROLL_DIRECTIONS = ['up', 'down', 'left', 'right']

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute desktop UI operations using AgentBay Computer API

        Args:
            tool_parameters: Tool parameters

        Yields:
            ToolInvokeMessage: Execution result message
        """
        logger.info("Starting desktop UI operation execution")
        try:
            # Get parameters
            session_id = tool_parameters.get('session_id', '')
            action = tool_parameters.get('action', 'click_mouse')
            
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
            yield self.create_text_message(f"🖥️ Executing desktop UI operation: {self.SUPPORTED_ACTIONS[action]}")
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
            computer = session.computer
            logger.info("Successfully got Computer instance")

            # Call corresponding API based on operation type
            result = self._execute_action(computer, action, tool_parameters)

            # Calculate operation time
            operation_time = time.time() - start_time
            logger.info(f"Operation completed: action={action}, took={operation_time:.2f}s, success={result.success}")

            # Handle result
            yield from self._handle_result(result, action, session_id, operation_time, tool_parameters)

        except Exception as e:
            logger.error(f"Exception occurred during desktop UI operation: {str(e)}", exc_info=True)
            yield self.create_text_message(f"❌ Exception occurred during desktop UI operation: {str(e)}")

    def _validate_action_params(self, action: str, params: dict) -> str:
        """Validate operation-specific parameters, return error message or empty string"""
        if action in ['click_mouse', 'move_mouse', 'scroll']:
            if params.get('x') is None or params.get('y') is None:
                return f"❌ Error: {action} operation requires x and y coordinate parameters"
        
        if action == 'drag_mouse':
            if any(params.get(p) is None for p in ['from_x', 'from_y', 'to_x', 'to_y']):
                return "❌ Error: drag_mouse operation requires from_x, from_y, to_x, to_y parameters"
        
        if action == 'input_text':
            if not params.get('text'):
                return "❌ Error: input_text operation requires text parameter"
        
        if action == 'press_keys':
            if not params.get('keys'):
                return "❌ Error: press_keys operation requires keys parameter (string list)"
        
        if action == 'click_mouse' or action == 'drag_mouse':
            button = params.get('button', 'left')
            if button not in self.MOUSE_BUTTONS:
                return f"❌ Error: Invalid mouse button type: {button}, supported: {', '.join(self.MOUSE_BUTTONS)}"
        
        if action == 'scroll':
            direction = params.get('direction', 'up')
            if direction not in self.SCROLL_DIRECTIONS:
                return f"❌ Error: Invalid scroll direction: {direction}, supported: {', '.join(self.SCROLL_DIRECTIONS)}"
        
        return ""

    def _execute_action(self, computer, action: str, params: dict):
        """Execute specific operation"""
        logger.info(f"Executing operation: {action}")
        
        try:
            if action == 'click_mouse':
                x = int(params['x'])
                y = int(params['y'])
                button = params.get('button', 'left')
                logger.debug(f"Clicking mouse: x={x}, y={y}, button={button}")
                return computer.click_mouse(x=x, y=y, button=button)
            
            elif action == 'move_mouse':
                x = int(params['x'])
                y = int(params['y'])
                logger.debug(f"Moving mouse: x={x}, y={y}")
                return computer.move_mouse(x=x, y=y)
            
            elif action == 'drag_mouse':
                from_x = int(params['from_x'])
                from_y = int(params['from_y'])
                to_x = int(params['to_x'])
                to_y = int(params['to_y'])
                button = params.get('button', 'left')
                logger.debug(f"Dragging mouse: from=({from_x},{from_y}), to=({to_x},{to_y}), button={button}")
                return computer.drag_mouse(from_x=from_x, from_y=from_y, to_x=to_x, to_y=to_y, button=button)
            
            elif action == 'scroll':
                x = int(params['x'])
                y = int(params['y'])
                direction = params.get('direction', 'up')
                amount = int(params.get('amount', 1))
                logger.debug(f"Scrolling: x={x}, y={y}, direction={direction}, amount={amount}")
                return computer.scroll(x=x, y=y, direction=direction, amount=amount)
            
            elif action == 'input_text':
                text = params['text']
                logger.debug(f"Inputting text: text={text[:50]}...")  # Only log first 50 characters
                return computer.input_text(text=text)
            
            elif action == 'press_keys':
                keys = params['keys']
                if isinstance(keys, str):
                    # Support comma-separated key strings
                    keys = [k.strip() for k in keys.split(',')]
                hold = params.get('hold', False)
                logger.debug(f"Pressing keys: keys={keys}, hold={hold}")
                return computer.press_keys(keys=keys, hold=hold)
            
            elif action == 'screenshot':
                logger.debug("Taking screenshot")
                return computer.screenshot()
            
            elif action == 'get_screen_size':
                logger.debug("Getting screen size")
                return computer.get_screen_size()
            
            elif action == 'get_cursor_position':
                logger.debug("Getting cursor position")
                return computer.get_cursor_position()
            
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
        
        success_message = f"""✅ Desktop UI Operation Successful!

📊 Operation Info:
• Session ID: {session_id}
• Operation Type: {self.SUPPORTED_ACTIONS[action]}
• Operation Time: {operation_time:.2f} seconds
"""

        # Add specific information based on operation type
        if action == 'click_mouse':
            success_message += f"• Click Coordinates: ({params['x']}, {params['y']})\n• Mouse Button: {params.get('button', 'left')}"
        elif action == 'move_mouse':
            success_message += f"• Moved to: ({params['x']}, {params['y']})"
        elif action == 'drag_mouse':
            success_message += f"• Dragged from ({params['from_x']}, {params['from_y']}) to ({params['to_x']}, {params['to_y']})"
        elif action == 'scroll':
            success_message += f"• Position: ({params['x']}, {params['y']})\n• Direction: {params.get('direction', 'up')}\n• Amount: {params.get('amount', 1)}"
        elif action == 'input_text':
            text_preview = params['text'][:100] + ('...' if len(params['text']) > 100 else '')
            success_message += f"• Input Text: {text_preview}"
        elif action == 'press_keys':
            keys = params['keys']
            if isinstance(keys, str):
                keys = [k.strip() for k in keys.split(',')]
            success_message += f"• Keys: {', '.join(keys)}\n• Hold: {params.get('hold', False)}"
        elif action == 'screenshot':
            screenshot_data = result.data if result.data else None
            if screenshot_data:
                success_message += f"• Screenshot Data: {screenshot_data}"
                # Create image message if URL is returned
                if isinstance(screenshot_data, str) and (screenshot_data.startswith('http://') or screenshot_data.startswith('https://')):
                    yield self.create_image_message(screenshot_data)
        elif action == 'get_screen_size':
            if result.data:
                success_message += f"• Screen Width: {result.data.get('width', 'N/A')}\n• Screen Height: {result.data.get('height', 'N/A')}\n• DPI Scaling: {result.data.get('dpiScalingFactor', 'N/A')}"
        elif action == 'get_cursor_position':
            if result.data:
                success_message += f"• Cursor Position: ({result.data.get('x', 'N/A')}, {result.data.get('y', 'N/A')})"

        yield self.create_text_message(success_message)

        # Build response data
        response_data = {
            'session_id': session_id,
            'action': action,
            'success': True,
            'operation_time': operation_time
        }

        # Add operation-specific data
        if action == 'click_mouse':
            response_data.update({'x': params['x'], 'y': params['y'], 'button': params.get('button', 'left')})
        elif action == 'move_mouse':
            response_data.update({'x': params['x'], 'y': params['y']})
        elif action == 'drag_mouse':
            response_data.update({
                'from_x': params['from_x'], 'from_y': params['from_y'],
                'to_x': params['to_x'], 'to_y': params['to_y'],
                'button': params.get('button', 'left')
            })
        elif action == 'scroll':
            response_data.update({
                'x': params['x'], 'y': params['y'],
                'direction': params.get('direction', 'up'),
                'amount': params.get('amount', 1)
            })
        elif action == 'input_text':
            response_data['text'] = params['text']
        elif action == 'press_keys':
            response_data['keys'] = params['keys']
            response_data['hold'] = params.get('hold', False)
        elif action in ['screenshot', 'get_screen_size', 'get_cursor_position']:
            if result.data:
                response_data['data'] = result.data

        yield self.create_json_message(response_data)

        # Return variables (for workflow use)
        yield self.create_variable_message("computer_action", action)
        yield self.create_variable_message("computer_operation_success", "true")

        if action in ['click_mouse', 'move_mouse']:
            yield self.create_variable_message("x", str(params['x']))
            yield self.create_variable_message("y", str(params['y']))
        elif action == 'screenshot' and result.data:
            if isinstance(result.data, str):
                yield self.create_variable_message("screenshot_url", result.data)

    def _handle_error_result(self, result, action: str, session_id: str, operation_time: float, params: dict) -> Generator[ToolInvokeMessage, None, None]:
        """Handle error result"""
        logger.error(f"Operation failed: action={action}, error={result.error_message}")
        
        error_message = f"""❌ Desktop UI Operation Failed

📋 Session ID: {session_id}
🖥️ Operation Type: {self.SUPPORTED_ACTIONS[action]}
⏱️ Operation Time: {operation_time:.2f} seconds
🔍 Error Message: {result.error_message}

💡 Suggestions:
• Check if session is desktop type (e.g. windows_latest, linux_latest, etc.)
• Verify session exists and is available
• Confirm coordinates are within valid range
• Check if permissions are sufficient
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
        yield self.create_variable_message("computer_operation_success", "false")

