"""
Utility functions for channel name management.
Handles custom channel names, formatting, and validation.
"""

def get_channel_name(channel_id: int, custom_names: dict) -> str:
    """
    Get the display name for a channel.
    Returns "CustomName (Ch1)" if custom name exists, otherwise "Channel 1".
    
    Args:
        channel_id: Zero-based channel index
        custom_names: Dictionary mapping channel IDs to custom names
        
    Returns:
        Formatted channel name string
    """
    custom_name = custom_names.get(str(channel_id), None)
    if custom_name:
        return f"{custom_name} (Ch{channel_id + 1})"
    return f"Channel {channel_id + 1}"


def get_channel_short_name(channel_id: int, custom_names: dict) -> str:
    """
    Get the short display name for a channel.
    Returns "CustomName (Ch1)" if custom name exists, otherwise "Ch 1".
    
    Args:
        channel_id: Zero-based channel index
        custom_names: Dictionary mapping channel IDs to custom names
        
    Returns:
        Formatted short channel name string
    """
    custom_name = custom_names.get(str(channel_id), None)
    if custom_name:
        return f"{custom_name} (Ch{channel_id + 1})"
    return f"Ch {channel_id + 1}"


def get_channel_name_parts(channel_id: int, custom_names: dict) -> tuple:
    """
    Get the custom and default parts of a channel name separately.
    Useful for rendering with different styles or truncation.
    
    Args:
        channel_id: Zero-based channel index
        custom_names: Dictionary mapping channel IDs to custom names
        
    Returns:
        Tuple of (custom_part, default_part) where:
        - custom_part: Custom name if exists, empty string otherwise
        - default_part: " (Ch1)" if custom name exists, "Channel 1" otherwise
    """
    custom_name = custom_names.get(str(channel_id), None)
    if custom_name:
        return (custom_name, f" (Ch{channel_id + 1})")
    return ("", f"Channel {channel_id + 1}")


def validate_channel_name(name: str) -> bool:
    """
    Validate a custom channel name.
    
    Args:
        name: The custom channel name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name:
        return False
    if len(name) > 50:
        return False
    return True


def sanitize_channel_name(name: str) -> str:
    """
    Sanitize a channel name for use in filenames.
    Replaces invalid characters with safe alternatives.
    
    Args:
        name: The channel name to sanitize
        
    Returns:
        Sanitized channel name safe for use in filenames
    """
    import re
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Replace invalid filename characters with dashes
    name = re.sub(r'[/\\:*?"<>|]', '-', name)
    # Replace any other non-alphanumeric characters (except _ and -) with underscores
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    return name

