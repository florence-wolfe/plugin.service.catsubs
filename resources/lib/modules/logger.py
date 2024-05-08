import xbmc
from modules.constants import ADDON_NAME, addon


def log(message: str, level=xbmc.LOGINFO):
    if level == xbmc.LOGDEBUG and not addon.getSettings().getBool("debug"):
        return
    xbmc.log(f"[{ADDON_NAME}]: {message}", level)
