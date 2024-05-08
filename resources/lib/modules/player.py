import xbmc
import asyncio
import threading
from typing import Callable, Optional
from .logger import log
from .constants import addon
from .subtitle_handler import load_background_subtitles

CancelCallback = Optional[Callable[[], None]]


class CatSubsPlayer(xbmc.Player):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.subtitle_task: Optional[asyncio.Task] = None
        self.current_video_id: Optional[str] = None
        log("Initialized CatSubs Player", xbmc.LOGDEBUG)

    def onAVStarted(self):
        delay = addon.getSettings().getInt("delay") * 1000
        video_id = self.getVideoInfoTag().getUniqueID("tmbd")
        xbmc.sleep(delay)

        if video_id != self.current_video_id:
            log(f"New video - {video_id}. Cancelling previous requests", xbmc.LOGDEBUG)
            if (
                hasattr(self, "subtitle_task")
                and self.subtitle_task
                and not self.subtitle_task.done()
            ):
                self.subtitle_task.cancel()
            self.current_video_id = video_id

        # Use the lock to avoid calling this while the previous one is still running.
        # In theory, if this works as expected, it should prevent unnecessary API calls.
        if self.lock.acquire(blocking=False):
            try:
                asyncio.run(self.handle_subs())
            finally:
                self.lock.release()

    async def handle_subs(self):
        log("Handling subs...", xbmc.LOGDEBUG)
        # TODO: Revisit the global exclusion
        if not self.isPlayingVideo():
            # this shouldn't even be a possible state
            log("How did we get here. We're not playing video.", xbmc.LOGERROR)
            return
        action = addon.getSettings().getInt("primary_subtitle_action")
        if action == 0:
            log("Downloading subtitles in background", xbmc.LOGDEBUG)
            self.subtitle_task = asyncio.create_task(load_background_subtitles())
        elif action == 1:
            log("Opening subtitle dialog", xbmc.LOGDEBUG)
            xbmc.executebuiltin("ActivateWindow(SubtitleSearch)")


player = CatSubsPlayer()
