"""
Input Validation Tool for Security
"""
import re
from typing import List, Optional


# Dangerous command patterns (security check)
DANGEROUS_PATTERNS = [
    r'rm\s+-rf\s+/',      # Delete root directory
    r'mkfs\.',            # Format command
    r'dd\s+if=.*of=',     # Disk clone
    r':(){ :|:& };:',     # Fork bomb
    r'curl.*\|\s*sh',     # Download and execute script
    r'wget.*\|\s*sh',     # Download and execute script
    r'sudo\s+rm',         # Sudo delete
    r'chmod\s+777',       # Dangerous permission setting
]

# Allowed image types
ALLOWED_IMAGE_IDS = [
    'linux_latest',
    'browser_latest', 
    'code_latest',
    'windows_latest',
    'mobile_latest'
]

# Safe file path patterns
SAFE_PATH_PATTERNS = [
    r'^/tmp/.*',          # tmp directory
    r'^/home/.*',         # User directory
    r'^\./',              # Relative path
    r'^[^/].*',           # Relative path not starting with /
]


def validate_command(command: str) -> bool:
    """
    Validate command safety
    
    Args:
        command: Command to validate
        
    Returns:
        bool: Whether it's safe
    """
    if not command or not isinstance(command, str):
        return False
    
    # Check dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False
    
    return True


def validate_image_id(image_id: str) -> bool:
    """
    Validate image ID validity
    
    Args:
        image_id: Image ID
        
    Returns:
        bool: Whether it's valid
    """
    return image_id in ALLOWED_IMAGE_IDS


def validate_file_path(path: str) -> bool:
    """
    Validate file path safety
    
    Args:
        path: File path
        
    Returns:
        bool: Whether it's safe
    """
    if not path or not isinstance(path, str):
        return False
    
    # Check for path traversal attack
    if '..' in path:
        return False
    
    # Check if it matches safe path pattern
    for pattern in SAFE_PATH_PATTERNS:
        if re.match(pattern, path):
            return True
    
    return False


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format
    
    Args:
        session_id: Session ID
        
    Returns:
        bool: Whether it's valid
    """
    if not session_id or not isinstance(session_id, str):
        return False
    
    # Basic format check (can be adjusted based on actual AgentBay session ID format)
    return len(session_id) > 5 and session_id.replace('-', '').replace('_', '').isalnum()


def validate_timeout(timeout_ms: int) -> bool:
    """
    Validate timeout validity
    
    Args:
        timeout_ms: Timeout in milliseconds
        
    Returns:
        bool: Whether it's valid
    """
    if not isinstance(timeout_ms, (int, float)):
        return False
    
    # Timeout should be within reasonable range (1 second to 5 minutes)
    return 1000 <= timeout_ms <= 300000


def sanitize_content(content: str) -> str:
    """
    Sanitize file content
    
    Args:
        content: Original content
        
    Returns:
        str: Sanitized content
    """
    if not isinstance(content, str):
        return ""
    
    # Remove potential malicious script tags
    content = re.sub(r'<script.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
    
    return content
