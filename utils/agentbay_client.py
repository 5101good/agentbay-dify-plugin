"""
Lightweight AgentBay Client Designed for Serverless Environments
- Stateless design
- Fast initialization
- Memory efficient
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
import os

# Import AgentBay SDK directly
from agentbay import AgentBay
from agentbay.session import Session
from agentbay.session_params import CreateSessionParams
from agentbay.exceptions import AgentBayError

# Import logging utility
from utils.logger import get_logger

# Create logger instance
logger = get_logger(__name__)


@dataclass
class SimpleResult:
    """Simplified result object"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class LightweightAgentBayClient:
    """Lightweight AgentBay Client Adapted for Serverless Environments"""
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize client

        Args:
            credentials: Credentials dictionary containing api_key and other info
        """
        logger.info("Initializing LightweightAgentBayClient")
        self.api_key = credentials.get('api_key')
        if not self.api_key:
            logger.error("API key not provided")
            raise ValueError("API key is required")

        logger.info("Client initialization successful")
        # Lightweight configuration, no state saved
        #self.base_url = credentials.get('base_url', 'https://agentbay.console.aliyun.com')
        self._client = None
    
    @property
    def client(self) -> AgentBay:
        """Get AgentBay client instance (lazy loading)"""
        if self._client is None:
            logger.info("Creating AgentBay client instance")
            self._client = AgentBay(api_key=self.api_key)
        return self._client
    
    def create_session(self, image_id: str = 'linux_latest') -> SimpleResult:
        """
        Create session (stateless, automatically add dify_plugin label)

        Args:
            image_id: Image ID

        Returns:
            SimpleResult: Creation result
        """
        logger.info(f"Starting to create session: image_id={image_id}")
        try:
            # All sessions use unified dify_plugin label
            dify_labels = {"dify_plugin": "true"}

            params = CreateSessionParams(
                image_id=image_id,
                labels=dify_labels
            )

            result = self.client.create(params)

            if result.success:
                session_id = result.session.session_id
                logger.info(f"Session created successfully: session_id={session_id}, image_id={image_id}")
                return SimpleResult(
                    success=True,
                    data={
                        'session_id': session_id,
                        'image_id': image_id,
                        'status': 'created',
                        'request_id': result.request_id,
                        'resource_url': result.session.resource_url
                    }
                )
            else:
                logger.error(f"Session creation failed: {result.error_message}")
                return SimpleResult(
                    success=False,
                    error=result.error_message
                )

        except AgentBayError as e:
            logger.error(f"AgentBay API error: {str(e)}")
            return SimpleResult(
                success=False,
                error=f"AgentBay API error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unknown error occurred while creating session: {str(e)}", exc_info=True)
            return SimpleResult(
                success=False,
                error=f"Unknown error: {str(e)}"
            )
    
    def get_session_info(self, session_id: str) -> SimpleResult:
        """
        Get session information (stateless, real-time query from cloud)

        Args:
            session_id: Session ID

        Returns:
            SimpleResult: Session information
        """
        logger.info(f"Querying session info: session_id={session_id}")
        try:
            from agentbay.model.response import GetSessionResult
            result: GetSessionResult = self.client.get_session(session_id)

            if not result.success:
                logger.error(f"Failed to query session info: session_id={session_id}, error={result.error_message}")
                return SimpleResult(
                    success=False,
                    error=f"Failed to query session info: {result.error_message}"
                )

            # Find the specified session_id in the result
            if hasattr(result, 'data') and result.data:
                logger.info(f"Successfully retrieved session info: session_id={session_id}")
                return SimpleResult(
                    success=True,
                    data=result.data
                )

            logger.warning(f"Session does not exist or is inaccessible: session_id={session_id}")
            return SimpleResult(
                success=False,
                error=f"Session {session_id} does not exist or is inaccessible"
            )
        except Exception as e:
            logger.error(f"Exception occurred while getting session info: session_id={session_id}, error={str(e)}", exc_info=True)
            return SimpleResult(
                success=False,
                error=f"Failed to get session info: {str(e)}"
            )
    
    def execute_command(self, session_id: str, command: str, timeout_ms: int = 30000) -> SimpleResult:
        """
        Execute command (stateless, directly create Session instance)

        Args:
            session_id: Session ID
            command: Command
            timeout_ms: Timeout in milliseconds

        Returns:
            SimpleResult: Execution result
        """
        logger.info(f"Executing command: session_id={session_id}, command={command[:100]}, timeout={timeout_ms}ms")
        try:
            # Check if session exists and is available
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info  # Return error info

            # Directly create Session instance using session_id (stateless way)
            from agentbay.session import Session
            session = Session(self.client, session_id)

            result = session.command.execute_command(command, timeout_ms=timeout_ms)

            if result.success:
                logger.info(f"Command executed successfully: session_id={session_id}, exit_code={getattr(result, 'exit_code', 0)}")
            else:
                logger.error(f"Command execution failed: session_id={session_id}, error={result.error_message}")

            return SimpleResult(
                success=result.success,
                data={
                    'output': result.output,
                    'error': getattr(result, 'error', None),
                    'exit_code': getattr(result, 'exit_code', None)
                } if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            logger.error(f"Exception occurred while executing command: session_id={session_id}, error={str(e)}", exc_info=True)
            return SimpleResult(
                success=False,
                error=f"Command execution failed: {str(e)}"
            )
    
    def delete_session(self, session_id: str, sync_context: bool = False) -> SimpleResult:
        """
        Delete session (stateless way)

        Args:
            session_id: Session ID
            sync_context: Whether to synchronize context

        Returns:
            SimpleResult: Deletion result
        """
        logger.info(f"Deleting session: session_id={session_id}, sync_context={sync_context}")
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info  # Return error info

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            result = self.client.delete(session, sync_context=sync_context)

            if result.success:
                logger.info(f"Session deleted successfully: session_id={session_id}")
            else:
                logger.error(f"Session deletion failed: session_id={session_id}, error={result.error_message}")

            return SimpleResult(
                success=result.success,
                data={'session_id': session_id, 'deleted': True} if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            logger.error(f"Exception occurred while deleting session: session_id={session_id}, error={str(e)}", exc_info=True)
            return SimpleResult(
                success=False,
                error=f"Session deletion failed: {str(e)}"
            )
    
    def list_sessions(self) -> SimpleResult:
        """
        List all sessions created by dify plugin (stateless way, auto-handle pagination)

        Returns:
            SimpleResult: Session list
        """
        logger.info("Starting to list all sessions")
        try:
            # Use new list API to query all sessions created by dify plugin
            dify_labels = {"dify_plugin": "true"}
            all_session_ids = []
            page = 1
            limit = 100

            # Loop to get all paginated data
            while True:
                result = self.client.list(labels=dify_labels, page=page, limit=limit)

                if not result.success:
                    return SimpleResult(
                        success=False,
                        error=f"Failed to query session list: {result.error_message}"
                    )

                # Collect session_ids from current page
                if hasattr(result, 'session_ids') and result.session_ids:
                    all_session_ids.extend(result.session_ids)

                # Check if there are more pages
                total = result.total if hasattr(result, 'total') else len(result.session_ids)
                if len(all_session_ids) >= total or not result.session_ids:
                    break

                page += 1

            # Build session list
            session_list = []
            for session_id in all_session_ids:
                session_list.append({
                    'session_id': session_id,
                    'status': 'active',
                })

            logger.info(f"Successfully listed sessions: total {len(session_list)} sessions")
            return SimpleResult(
                success=True,
                data={'sessions': session_list, 'count': len(session_list)}
            )

        except Exception as e:
            logger.error(f"Exception occurred while listing sessions: {str(e)}", exc_info=True)
            return SimpleResult(
                success=False,
                error=f"Failed to list sessions: {str(e)}"
            )

    def read_file(self, session_id: str, file_path: str) -> SimpleResult:
        """
        Read file

        Args:
            session_id: Session ID
            file_path: File path

        Returns:
            SimpleResult: File content
        """
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            result = session.file_system.read_file(file_path)

            return SimpleResult(
                success=result.success,
                data={
                    'file_path': file_path,
                    'content': result.content,
                    'size': len(result.content) if result.content else 0
                } if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            return SimpleResult(
                success=False,
                error=f"Failed to read file: {str(e)}"
            )

    def write_file(self, session_id: str, file_path: str, content: str) -> SimpleResult:
        """
        Write file

        Args:
            session_id: Session ID
            file_path: File path
            content: File content

        Returns:
            SimpleResult: Write result
        """
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info

            # Directly create Session instance using session_id
            session = Session(self.client, session_id)

            result = session.file_system.write_file(file_path, content)

            return SimpleResult(
                success=result.success,
                data={
                    'file_path': file_path,
                    'size': len(content)
                } if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            return SimpleResult(
                success=False,
                error=f"Failed to write file: {str(e)}"
            )

    def list_directory(self, session_id: str, directory_path: str) -> SimpleResult:
        """
        List directory contents

        Args:
            session_id: Session ID
            directory_path: Directory path

        Returns:
            SimpleResult: Directory contents
        """
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            result = session.file_system.list_directory(directory_path)

            return SimpleResult(
                success=result.success,
                data={
                    'directory_path': directory_path,
                    'files': result.files if hasattr(result, 'files') else [],
                    'count': len(result.files) if hasattr(result, 'files') else 0
                } if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            return SimpleResult(
                success=False,
                error=f"Failed to list directory: {str(e)}"
            )

    def run_code(self, session_id: str, code: str, language: str) -> SimpleResult:
        """
        Execute code using AgentBay native API

        Args:
            session_id: Session ID
            code: Code content
            language: Programming language

        Returns:
            SimpleResult: Execution result
        """
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            result = session.code.run_code(code, language)
            logger.info(f"Code execution result: {result.result}")

            return SimpleResult(
                success=result.success,
                data={
                    'language': language,
                    'result': result.result,
                    'output': getattr(result, 'output', result.result),
                    'error': getattr(result, 'error', None)
                } if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            return SimpleResult(
                success=False,
                error=f"Code execution failed: {str(e)}"
            )

    def ui_screenshot(self, session_id: str) -> SimpleResult:
        """
        Take UI screenshot using AgentBay native API

        Args:
            session_id: Session ID

        Returns:
            SimpleResult: Screenshot result
        """
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            result = session.ui.screenshot()

            return SimpleResult(
                success=result.success,
                data=result.data if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            return SimpleResult(
                success=False,
                error=f"UI screenshot failed: {str(e)}"
            )

    def ui_click(self, session_id: str, x: int, y: int) -> SimpleResult:
        """
        Click UI element using AgentBay native API

        Args:
            session_id: Session ID
            x: X coordinate
            y: Y coordinate

        Returns:
            SimpleResult: Click result
        """
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            result = session.ui.click(x=x, y=y)

            return SimpleResult(
                success=result.success,
                data={
                    'action': 'click',
                    'x': x,
                    'y': y
                } if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            return SimpleResult(
                success=False,
                error=f"UI click failed: {str(e)}"
            )

    def ui_type(self, session_id: str, text: str) -> SimpleResult:
        """
        Type text using AgentBay native API

        Args:
            session_id: Session ID
            text: Text to type

        Returns:
            SimpleResult: Type result
        """
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            result = session.ui.type(text)

            return SimpleResult(
                success=result.success,
                data={
                    'action': 'type',
                    'text': text
                } if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            return SimpleResult(
                success=False,
                error=f"UI type failed: {str(e)}"
            )

    def ui_key(self, session_id: str, key: str) -> SimpleResult:
        """
        Press key using AgentBay native API

        Args:
            session_id: Session ID
            key: Key to press

        Returns:
            SimpleResult: Key press result
        """
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            result = session.ui.key(key)

            return SimpleResult(
                success=result.success,
                data={
                    'action': 'key',
                    'key': key
                } if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            return SimpleResult(
                success=False,
                error=f"UI key press failed: {str(e)}"
            )

    def browser_initialize(self, session_id: str) -> SimpleResult:
        """
        Initialize browser using AgentBay native API

        Args:
            session_id: Session ID

        Returns:
            SimpleResult: Initialization result
        """
        logger.info(f"Initializing browser: session_id={session_id}")
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info     

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            from agentbay.browser.browser import BrowserOption
            browser_option = BrowserOption()

            # Use synchronous method to initialize browser
            result = session.browser.initialize(browser_option)

            if result:
                endpoint_url = session.browser.get_endpoint_url()
                logger.info(f"Browser initialized successfully: session_id={session_id}, endpoint_url={endpoint_url}")
                return SimpleResult(
                    success=True,
                    data={
                        'initialized': True,
                        'endpoint_url': endpoint_url
                    }
                )
            else:
                logger.error(f"Browser initialization failed: session_id={session_id}")
                return SimpleResult(
                    success=False,
                    error="Browser initialization failed"
                )

        except Exception as e:
            logger.error(f"Exception occurred during browser initialization: session_id={session_id}, error={str(e)}", exc_info=True)
            return SimpleResult(
                success=False,
                error=f"Browser initialization failed: {str(e)}"
            )


    def get_installed_apps(self, session_id: str, start_menu: bool = True, desktop: bool = False, ignore_system_apps: bool = True) -> SimpleResult:
        """
        Get installed apps using AgentBay native API

        Args:
            session_id: Session ID
            start_menu: Include start menu apps
            desktop: Include desktop apps
            ignore_system_apps: Ignore system apps

        Returns:
            SimpleResult: App list
        """
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            result = session.application.get_installed_apps(
                start_menu=start_menu,
                desktop=desktop,
                ignore_system_apps=ignore_system_apps
            )

            return SimpleResult(
                success=result.success,
                data={
                    'apps': result.data,
                    'count': len(result.data) if result.data else 0
                } if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            return SimpleResult(
                success=False,
                error=f"Failed to get app list: {str(e)}"
            )

    def list_windows(self, session_id: str) -> SimpleResult:
        """
        List windows using AgentBay native API

        Args:
            session_id: Session ID

        Returns:
            SimpleResult: Window list
        """
        try:
            # Check if session exists first
            session_info = self.get_session_info(session_id)
            if not session_info.success:
                return session_info

            # Directly get Session instance using session_id
            session = self.client.get(session_id).session

            result = session.window.list_windows()

            return SimpleResult(
                success=result.success,
                data={
                    'windows': result.data,
                    'count': len(result.data) if result.data else 0
                } if result.success else None,
                error=result.error_message if not result.success else None
            )

        except Exception as e:
            return SimpleResult(
                success=False,
                error=f"Failed to list windows: {str(e)}"
            )


def get_agentbay_client(credentials: Dict[str, Any]) -> LightweightAgentBayClient:
    """
    Factory function: Get AgentBay client instance
    
    Args:
        credentials: Credentials dictionary
        
    Returns:
        LightweightAgentBayClient: Client instance
    """
    return LightweightAgentBayClient(credentials)
