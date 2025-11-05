"""
AgentBay Unified Browser Automation Tool - Using Native API + Playwright
"""
from collections.abc import Generator
from typing import Any
import time

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.agentbay_client import LightweightAgentBayClient, get_agentbay_client
from utils.validators import validate_session_id
from utils.logger import get_logger

# Create logger instance
logger = get_logger(__name__)


class BrowserAutomationTool(Tool):
    """AgentBay Unified Browser Automation Tool - Integrating Navigation, Interaction, Screenshot and Other Functions"""

    # Supported browser operation types
    SUPPORTED_ACTIONS = {
        'navigate': 'Navigate to URL',
        'click': 'Click element',
        'type': 'Type text',
        'scroll': 'Scroll page',
        'screenshot': 'Take screenshot',
        'get_content': 'Get page content',
        'analyze_elements': 'Analyze page elements',
        'wait_element': 'Wait for element',
        'wait': 'Wait specified time'
    }

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute unified browser automation operation

        Args:
            tool_parameters: Tool parameters

        Yields:
            ToolInvokeMessage: Execution result message
        """
        logger.info("Starting browser automation tool execution")
        try:
            # Get basic parameters
            session_id = tool_parameters.get('session_id', '')
            action = tool_parameters.get('action', 'navigate')

            logger.info(f"Tool parameters: session_id={session_id}, action={action}")

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

            # Get operation-specific parameters
            operation_params = self._get_operation_params(tool_parameters, action)
            logger.info(f"Operation parameters: {operation_params}")

            # Validate operation-specific parameters
            validation_result = self._validate_operation_params(action, operation_params)
            if validation_result:
                logger.warning(f"Parameter validation failed: {validation_result}")
                yield self.create_text_message(validation_result)
                return

            # Get AgentBay client
            logger.info("Getting AgentBay client")
            client = get_agentbay_client(self.runtime.credentials)

            # Show operation info
            yield self.create_text_message(f"🌐 Executing browser operation: {self.SUPPORTED_ACTIONS[action]}")
            yield self.create_text_message(f"📋 Session ID: {session_id}")

            # Show specific operation parameters
            for message in self._show_operation_details(action, operation_params):
                yield message

            # Record start time
            start_time = time.time()

            # Execute specific operation
            logger.info(f"Executing browser operation: action={action}")
            result = self._execute_browser_operation(
                client, session_id, action, operation_params
            )

            # Calculate operation time
            operation_time = time.time() - start_time
            logger.info(f"Browser operation completed: took {operation_time:.2f} seconds")

            if result.success:
                logger.info(f"Browser operation successful: session_id={session_id}, action={action}")
                # Build success message
                success_message = self._build_success_message(
                    action, session_id, operation_time, result.data
                )
                yield self.create_text_message(success_message)

                # If screenshot operation, return image data using blob message
                if action == 'screenshot' and result.data and isinstance(result.data, dict) and result.data.get('screenshot_data'):
                    screenshot_data = result.data.get('screenshot_data')
                    # Use create_blob_message to return image file
                    yield self.create_blob_message(
                        blob=screenshot_data,
                        meta={
                            'mime_type': 'image/png',
                            'filename': 'screenshot.png'
                        }
                    )

                # Return JSON format result
                response_data = {
                    'session_id': session_id,
                    'action': action,
                    'success': True,
                    'operation_time': operation_time
                }

                # Handle special data for different operation types
                if action == 'screenshot' and result.data:
                    # Exclude binary data to avoid JSON serialization errors
                    json_data = {k: v for k, v in result.data.items() if k != 'screenshot_data'}
                    response_data.update(json_data)
                else:
                    # Other operations directly return all data
                    # Python's json library will automatically handle string escaping, including HTML content
                    response_data.update(result.data or {})

                yield self.create_json_message(response_data)

                # Return variables (for workflow use)
                yield self.create_variable_message("browser_action", action)
                yield self.create_variable_message("browser_success", "true")

                # Specific operation variables
                for message in self._set_action_variables(action, result.data):
                    yield message

            else:
                logger.error(f"Browser operation failed: session_id={session_id}, action={action}, error={result.error}")
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

                yield self.create_variable_message("browser_success", "false")

        except Exception as e:
            logger.error(f"Exception occurred during browser operation: {str(e)}", exc_info=True)
            yield self.create_text_message(f"❌ Exception occurred during browser operation: {str(e)}")

    def _get_operation_params(self, tool_parameters: dict[str, Any], action: str) -> dict[str, Any]:
        """Get operation-specific parameters"""
        params = {}

        # Common parameters
        params['wait_time'] = tool_parameters.get('wait_time', 3)

        # Navigation parameters
        if action == 'navigate':
            params['url'] = tool_parameters.get('url', '')

        # Element interaction parameters
        elif action in ['click', 'type', 'wait_element']:
            params['selector'] = tool_parameters.get('selector', '')
            if action == 'type':
                params['text'] = tool_parameters.get('text', '')

        # Scroll parameters
        elif action == 'scroll':
            params['direction'] = tool_parameters.get('direction', 'down')
            params['distance'] = tool_parameters.get('distance', 500)

        # Screenshot parameters
        elif action == 'screenshot':
            params['full_page'] = tool_parameters.get('full_page', True)

        return params

    def _validate_operation_params(self, action: str, params: dict[str, Any]) -> str:
        """Validate operation-specific parameters, return error message or empty string"""
        if action == 'navigate':
            if not params.get('url'):
                return "❌ Error: navigate operation requires url parameter"
            # Basic URL format check
            url = params['url']
            if not (url.startswith('http://') or url.startswith('https://')):
                params['url'] = 'https://' + url

        elif action in ['click', 'type', 'wait_element']:
            if not params.get('selector'):
                return f"❌ Error: {action} operation requires selector parameter"

        elif action == 'type':
            if not params.get('text'):
                return "❌ Error: type operation requires text parameter"

        return ""

    def _show_operation_details(self, action: str, params: dict[str, Any]):
        """Show operation details"""
        messages = []
        if action == 'navigate':
            messages.append(self.create_text_message(f"🔗 Target URL: {params['url']}"))
            messages.append(self.create_text_message(f"⏱️ Wait Time: {params['wait_time']} seconds"))

        elif action == 'click':
            messages.append(self.create_text_message(f"🖱️ Click Selector: {params['selector']}"))

        elif action == 'type':
            messages.append(self.create_text_message(f"⌨️ Input Selector: {params['selector']}"))
            messages.append(self.create_text_message(f"📝 Input Content: {params['text']}"))

        elif action == 'scroll':
            messages.append(self.create_text_message(f"📜 Scroll Direction: {params['direction']}"))
            messages.append(self.create_text_message(f"📏 Scroll Distance: {params['distance']}px"))

        elif action == 'screenshot':
            messages.append(self.create_text_message(f"📸 Full Page Screenshot: {'Yes' if params['full_page'] else 'No'}"))
        
        return messages

    def _execute_browser_operation(self, client: LightweightAgentBayClient, session_id: str, action: str, params: dict[str, Any]):
        """Execute specific browser operation"""
        try:
            if action == 'wait':
                # Simple wait doesn't need browser connection
                return self._execute_wait(params)
            else:
                # All other operations use playwright implementation
                return self._execute_playwright_operation(client, session_id, action, params)

        except Exception as e:
            from utils.agentbay_client import SimpleResult
            return SimpleResult(
                success=False,
                error=f"Failed to execute {action} operation: {str(e)}"
            )


    def _execute_wait(self, params: dict[str, Any]):
        """Execute wait operation"""
        import time
        wait_time = params['wait_time']
        time.sleep(wait_time)

        from utils.agentbay_client import SimpleResult
        return SimpleResult(
            success=True,
            data={
                'action': 'wait',
                'wait_time': wait_time,
                'message': f'Waited for {wait_time} seconds'
            }
        )

    def _execute_playwright_operation(self, client: LightweightAgentBayClient, session_id: str, action: str, params: dict[str, Any]):
        """Execute all browser operations using playwright"""
        try:
            # Get browser endpoint
            browser_init_result = client.browser_initialize(session_id=session_id)
            if not browser_init_result.success:
                return browser_init_result

            endpoint_url = browser_init_result.data.get('endpoint_url') if isinstance(browser_init_result.data, dict) else None
            if not endpoint_url:
                from utils.agentbay_client import SimpleResult
                return SimpleResult(
                    success=False,
                    error="Unable to get browser endpoint URL"
                )

            # Use playwright automation to execute operations
            from utils.browser_automation import run_browser_action

            if action == 'navigate':
                async def navigate_action(automation):
                    return await automation.navigate(params['url'], params['wait_time'])
                result = run_browser_action(endpoint_url, navigate_action)

            elif action == 'click':
                async def click_action(automation):
                    return await automation.click_element(params['selector'])
                result = run_browser_action(endpoint_url, click_action)

            elif action == 'type':
                async def type_action(automation):
                    return await automation.type_text(params['selector'], params['text'])
                result = run_browser_action(endpoint_url, type_action)

            elif action == 'scroll':
                async def scroll_action(automation):
                    return await automation.scroll_page(params['direction'], params['distance'])
                result = run_browser_action(endpoint_url, scroll_action)

            elif action == 'screenshot':
                async def screenshot_action(automation):
                    return await automation.screenshot(params['full_page'])
                result = run_browser_action(endpoint_url, screenshot_action)

            elif action == 'get_content':
                async def content_action(automation):
                    return await automation.get_page_content()
                result = run_browser_action(endpoint_url, content_action)

            elif action == 'wait_element':
                async def wait_action(automation):
                    return await automation.wait_for_element(params['selector'], params['wait_time'] * 1000)
                result = run_browser_action(endpoint_url, wait_action)

            elif action == 'analyze_elements':
                async def analyze_action(automation):
                    return await automation.analyze_page_elements()
                result = run_browser_action(endpoint_url, analyze_action)

            else:
                from utils.agentbay_client import SimpleResult
                return SimpleResult(
                    success=False,
                    error=f"Unsupported operation: {action}"
                )

            return result

        except Exception as e:
            from utils.agentbay_client import SimpleResult
            return SimpleResult(
                success=False,
                error=f"Playwright operation failed: {str(e)}"
            )

    def _build_success_message(self, action: str, session_id: str, operation_time: float, data: dict) -> str:
        """Build success message"""
        message = f"""✅ Browser {self.SUPPORTED_ACTIONS[action]} Successful!

📊 Operation Info:
• Session ID: {session_id}
• Operation Type: {self.SUPPORTED_ACTIONS[action]}
• Operation Time: {operation_time:.2f} seconds"""

        # Add operation-specific information
        if action == 'navigate' and data:
            url = data.get('url') or data.get('navigation', {}).get('url')
            if url:
                message += f"\n• Navigation URL: {url}"
            title = data.get('title') or data.get('navigation', {}).get('title')
            if title:
                message += f"\n• Page Title: {title}"

        elif action == 'screenshot' and data:
            size = data.get('size') or data.get('data_size', 0)
            if size:
                message += f"\n• Screenshot Size: {size} bytes"

        elif action in ['click', 'type'] and data:
            selector = data.get('selector')
            if selector:
                message += f"\n• Target Selector: {selector}"

        elif action == 'get_content' and data:
            content_length = data.get('content_length', 0)
            if content_length:
                message += f"\n• Page Content Length: {content_length} characters"

        # Add follow-up suggestions
        message += "\n\n💡 Next Steps:"
        if action == 'navigate':
            message += "\n• Use click operation to interact with page elements"
            message += "\n• Use screenshot operation to capture page screenshot"
            message += "\n• Use get_content operation to retrieve page content"
        elif action == 'screenshot':
            message += "\n• Use click or type operation to interact with page"
        else:
            message += "\n• Use screenshot operation to view operation result"

        return message

    def _build_error_message(self, action: str, session_id: str, operation_time: float, error: str) -> str:
        """Build error message"""
        return f"""❌ Browser {self.SUPPORTED_ACTIONS[action]} Failed

📋 Session ID: {session_id}
🎯 Operation Type: {self.SUPPORTED_ACTIONS[action]}
⏱️ Operation Time: {operation_time:.2f} seconds
🔍 Error Message: {error}

💡 Suggestions:
• Check if session is browser_latest type
• Verify session exists and is available
• Confirm browser environment is correctly configured
• Check network connection is stable
• Verify target element exists (for interaction operations)"""

    def _set_action_variables(self, action: str, data: dict):
        """Set operation-specific variables"""
        messages = []
        if action == 'navigate' and data:
            url = data.get('url') or data.get('navigation', {}).get('url')
            if url:
                messages.append(self.create_variable_message("browser_current_url", url))
            title = data.get('title') or data.get('navigation', {}).get('title')
            if title:
                messages.append(self.create_variable_message("browser_page_title", title))

        elif action == 'screenshot' and data:
            if data.get('output_path'):
                messages.append(self.create_variable_message("browser_screenshot_path", data['output_path']))

        elif action == 'get_content' and data:
            content = data.get('content')
            if content:
                messages.append(self.create_variable_message("browser_page_content", content[:1000]))  # Limit length

        return messages