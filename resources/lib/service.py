import xbmc  # type: ignore
import sys

sys.modules["_asyncio"] = None  # type: ignore
from modules.monitor import CatSubsMonitor  # noqa: E402
from modules.player import CatSubsPlayer  # noqa: E402
from modules.logger import log  # noqa: E402
from modules.constants import ADDON_NAME, ADDON_VERSION  # noqa: E402


monitor = CatSubsMonitor()
player = CatSubsPlayer()

while not monitor.abortRequested():
    log(f"Starting {ADDON_NAME} v{ADDON_VERSION}")

    if monitor.waitForAbort(10):
        log("Shutdown requested", level=xbmc.LOGDEBUG)
        log("Player monitor stopped", level=xbmc.LOGDEBUG)
        log("Main monitor stopped", level=xbmc.LOGDEBUG)
        # If we're exiting, and we're still downloading a subtitle, cancel it
        if (
            hasattr(player, "subtitle_task")
            and player.subtitle_task
            and not player.subtitle_task.done()
        ):
            player.subtitle_task.cancel()
        del player
        del monitor
        break
