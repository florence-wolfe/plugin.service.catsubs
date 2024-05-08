import xbmc
import datetime
from typing import List
from .player import player
from .constants import addon
from .logger import log


def is_video_excluded_by(setting_id: str):
    excluded_items = addon.getSettings().getStringList(setting_id)
    if excluded_items is None or len(excluded_items) <= 0:
        return True

    video_source = player.getVideoInfoTag().getPath()
    is_excluded = any(excluded_item in video_source for excluded_item in excluded_items)
    if is_excluded:
        log(
            f"The video is excluded {video_source} - Exclusions: {excluded_items}",
            level=xbmc.LOGDEBUG,
        )
        return False
    else:
        return True


def is_short_video_excluded():
    time = player.getTotalTime()
    formatted_time = str(datetime.timedelta(seconds=round(time)))
    log(f"Total time: {formatted_time}", level=xbmc.LOGDEBUG)
    excluded_time = addon.getSettings().getInt("excluded_time")
    if time > excluded_time:
        return True
    else:
        log("The content time is shorter than the excluded time.", level=xbmc.LOGDEBUG)
        return False


# def audioexclusion():
#     if boolsetting("excludeaudio"):
#         langs = []
#         langs.append(utils.langdict[setting("excludeaudiolang1")])
#         if not setting("excludeaudiolang2") == "-----":
#             langs.append(utils.langdict[setting("excludeaudiolang2")])
#         if not setting("excludeaudiolang3") == "-----":
#             langs.append(utils.langdict[setting("excludeaudiolang3")])
#         availableaudio = xbmc.Player().getAvailableAudioStreams()
#         debug("Available audio streams: %s" % availableaudio)
#         availableaudio = " ".join(availableaudio)
#         if any(x in availableaudio for x in langs):
#             debug("Excluded: the audio language is excluded")
#             return False
#         if "und" in availableaudio and not boolsetting("audiound"):
#             debug("Excluded: undertermined audio")
#             return False
#         return True
#     return True


# def subexclusion():
#     if boolsetting("excludesub"):
#         langs = []
#         langs.append(utils.langdict[setting("excludesublang1")])
#         if not setting("excludesublang2") == "-----":
#             langs.append(utils.langdict[setting("excludesublang2")])
#         if not setting("excludesublang3") == "-----":
#             langs.append(utils.langdict[setting("excludesublang3")])
#         availablesubs = xbmc.Player().getAvailableSubtitleStreams()
#         debug("Available sub languages: %s" % availablesubs)
#         availablesubs = " ".join(availablesubs)
#         if any(x in availablesubs for x in langs):
#             debug("Subtitle is already present")
#             return False
#         return True
#     return True


def is_live_tv_excluded():
    is_excluded = addon.getSettings().getBool("exclude_live_tv")
    if "pvr://" in player.getPlayingFile() and is_excluded:
        log(
            "Video is playing via Live TV, which is currently set as excluded.",
            level=xbmc.LOGDEBUG,
        )
        return False
    return True


def is_http_excluded():
    is_excluded = addon.getSettings().getBool("exclude_http")
    if (
        "http://" in player.getPlayingFile() or "https://" in player.getPlayingFile()
    ) and is_excluded:
        log(
            "Video is playing via HTTP or HTTPS source, which is currently set as excluded.",
            level=xbmc.LOGDEBUG,
        )
        return False


#
# def has_global_exclusion():
#     if (
#         is_video_excluded_by("excluded_video_addons")
#         and is_video_excluded_by("excluded_words")
#         and is_video_excluded_by("excluded_paths")
#         and is_live_tv_excluded()
#         and is_http_excluded()
#         and is_short_video_excluded()
#         and subexclusion()
#         and audioexclusion()
#     ):
#         return True
#     return False


# TODO: add global subtitle filters
def apply_global_filters(
    subtitles: list, release_type: str, release_variants: List[str]
):
    return subtitles
