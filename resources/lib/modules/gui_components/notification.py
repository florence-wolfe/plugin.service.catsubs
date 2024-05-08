import xbmcgui
from modules.constants import addon


def notification(heading: str, message: str, time=5000):
    """Show a Notification alert."""
    is_notifications_enabled = addon.getSettings().getBool("enable_notifications")

    if not is_notifications_enabled:
        return

    xbmcgui.Dialog().notification(heading=heading, message=message, time=time)
