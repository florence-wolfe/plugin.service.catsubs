import xbmc
from .logger import log


class CatSubsMonitor(xbmc.Monitor):
    def __init__(self):
        super().__init__()
        log("Initialized CatSubs Monitor", xbmc.LOGDEBUG)

    def onSettingsChanged(self):
        pass


monitor = CatSubsMonitor()
