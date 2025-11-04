"""
AgentBay Provider Validation Logic
"""
from typing import Any, Dict

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from utils.agentbay_client import LightweightAgentBayClient


class AgentbayProvider(ToolProvider):
    """AgentBay Provider Class"""

    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        """
        Validate provider credentials
        
        Args:
            credentials: Credentials dictionary
            
        Raises:
            ToolProviderCredentialValidationError: Credential validation failed
        """
        try:
            # Get API key
            api_key = credentials.get('api_key')
            if not api_key:
                raise ToolProviderCredentialValidationError('API Key is required')
            
            # Basic format check
            if len(api_key.strip()) < 10:
                raise ToolProviderCredentialValidationError('API Key format appears to be invalid')
            
            # Create lightweight client for connection test
            try:
                client = LightweightAgentBayClient(credentials)
                # Try listing sessions to test API connectivity
                test_result = client.list_sessions()
                
                # Check if successful or authentication error
                if not test_result.success:
                    if 'auth' in test_result.error.lower() or 'key' in test_result.error.lower():
                        raise ToolProviderCredentialValidationError(f'API Key validation failed: {test_result.error}')
                    # Other errors may be network issues, but API Key might be valid
                    # More detailed error handling will be done in actual use
                
            except Exception as e:
                # More detailed error handling
                error_msg = str(e).lower()
                if 'auth' in error_msg or 'unauthorized' in error_msg or 'forbidden' in error_msg:
                    raise ToolProviderCredentialValidationError('API Key validation failed, please check if the key is correct')
                elif 'network' in error_msg or 'connection' in error_msg:
                    raise ToolProviderCredentialValidationError('Network connection failed, please check network settings')
                else:
                    raise ToolProviderCredentialValidationError(f'Credential validation failed: {str(e)}')
                
        except ToolProviderCredentialValidationError:
            # Re-raise known validation errors
            raise
        except Exception as e:
            # Catch other unexpected errors
            raise ToolProviderCredentialValidationError(f'Error occurred during credential validation: {str(e)}')

    #########################################################################################
    # If OAuth is supported, uncomment the following functions.
    # Warning: please make sure that the sdk version is 0.4.2 or higher.
    #########################################################################################
    # def _oauth_get_authorization_url(self, redirect_uri: str, system_credentials: Mapping[str, Any]) -> str:
    #     """
    #     Generate the authorization URL for agentbay OAuth.
    #     """
    #     try:
    #         """
    #         IMPLEMENT YOUR AUTHORIZATION URL GENERATION HERE
    #         """
    #     except Exception as e:
    #         raise ToolProviderOAuthError(str(e))
    #     return ""
        
    # def _oauth_get_credentials(
    #     self, redirect_uri: str, system_credentials: Mapping[str, Any], request: Request
    # ) -> Mapping[str, Any]:
    #     """
    #     Exchange code for access_token.
    #     """
    #     try:
    #         """
    #         IMPLEMENT YOUR CREDENTIALS EXCHANGE HERE
    #         """
    #     except Exception as e:
    #         raise ToolProviderOAuthError(str(e))
    #     return dict()

    # def _oauth_refresh_credentials(
    #     self, redirect_uri: str, system_credentials: Mapping[str, Any], credentials: Mapping[str, Any]
    # ) -> OAuthCredentials:
    #     """
    #     Refresh the credentials
    #     """
    #     return OAuthCredentials(credentials=credentials, expires_at=-1)
