import xbmc
import xbmcvfs
import os
import gzip
import httpx
from typing import List, Dict
from service import player
from modules.constants import addon
from modules.subtitle_providers import get_providers
from modules.subtitle_providers.i_provider import (
    Subtitle,
    Downloadable,
)
from modules.gui_components.notification import notification
from modules.global_filters import apply_global_filters


def get_release_type():
    release_types = {
        "cam": ["cam-rip", "cam.rip", "cam rip", "cam", "camrip"],
        "telesync": ["telesync", "ts", "hdts", "hc", "hcrip", "pdvd", "predvdrip"],
        "telecine": ["telecine", "tc", "hdtc"],
        "ppv": ["ppv", "ppvrip"],
        "screener": ["screener", "scr", "dvdscr", "dvdcreener", "bdscr"],
        "dvd": [
            "dvd",
            "dvd-r",
            "dvdrip",
            "dvdr",
            "dvdmux",
            "dvdfull",
            "dvd5",
            "dvd9",
            "dvd-rip",
            "dvd.rip",
            "dvd-mux",
            "dvd.mux",
            "dvd-5",
            "dvd-9",
        ],
        "hdtv": [
            "hdtv",
            "dsr",
            "dsrip",
            "satrip",
            "dthrip",
            "dvbrip",
            "pdtv",
            "dtvrip",
            "tvrip",
            "hdtvrip",
            "hdtv-rip",
            "hdtv.rip",
            "hdtv rip",
        ],
        "vob": ["vob", "vodrip", "vod rip", "vod.rip", "vod-rip", "vodr"],
        "webdl": ["web-dl", "webdl", "web.dl", "web dl", "webdlrip"],
        "webrip": [
            "webrip",
            "web-rip",
            "web.rip",
            "web rip",
            "webr",
            "web",
            "webcap",
            "web-cap",
            "web.cap",
            "web cap",
        ],
        "bluray": ["blu", "ray", "bluray", "blu-ray", "blu.ray", "blu ray"],
        "bdrip": [
            "bdrip",
            "bd-rip",
            "bd.rip",
            "bd rip",
            "brrip",
            "br-rip",
            "br.rip",
            "br rip",
            "brip",
            "b-rip",
            "b.rip",
            "b rip",
            "bdmv",
        ],
        "hdrip": ["hdrip", "hd-rip", "hd rip", "hd.rip"],
    }

    video_path = xbmc.Player().getPlayingFile().lower()
    for release_type, variants in release_types.items():
        if any(variant in video_path for variant in variants):
            return release_type, variants

    return None, None


# TODO: Actually implement this
def filter_subtitles(
    subtitles: List[Subtitle],
    languages: List[str],
    release_type: str,
    release_variants: List[str],
):
    if addon.getSettings().getBool("allow_any_subtitle"):
        return subtitles

    return apply_global_filters(subtitles, release_type, release_variants)


async def save_subtitles(subtitles: Dict[str, List[Downloadable]]):
    temp_dir = xbmcvfs.translatePath("special://temp/")
    saved_subtitles = []

    async with httpx.AsyncClient() as client:
        for provider, download_links in subtitles.items():
            for downloadable in download_links:
                try:
                    # Download the subtitle from the link
                    response = await client.get(downloadable["link"])
                    if response.status_code != 200:
                        raise Exception("Failed to download subtitle")
                    # get the subtitle content from the response
                    subtitle_content = response.text
                    # TODO: handle zip archives like from subdl
                    # TODO: Consider adding a setting to keep track of base64 encoded subtitles
                    # Create a unique filename for the subtitle
                    filename = f"{downloadable['file_name']}_{provider}.srt"
                    temp_path = os.path.join(temp_dir, filename)

                    # Compress the subtitle content using gzip
                    with gzip.open(temp_path, "wt", encoding="utf-8") as gzip_file:
                        gzip_file.write(subtitle_content)
                    saved_subtitles.append(temp_path)
                except Exception as e:
                    xbmc.log(
                        f"Error saving subtitle: {downloadable['file_name']}. Error: {str(e)}",
                        xbmc.LOGERROR,
                    )
    if saved_subtitles:
        player.setSubtitles(saved_subtitles[0])


async def load_background_subtitles():
    media = xbmc.Player().getVideoInfoTag().getMediaType()
    languages = addon.getSettings().getStringList("subtitle_languages")
    release_type, release_variants = get_release_type()

    if not release_type and not addon.getSettings().getBool("allow_any_subtitle"):
        # This is sketchy
        raise Exception("No suitable release type found.")

    file = xbmc.Player().getPlayingFile()
    notification(heading=release_type, message=file, time=4000)

    tmdb_id = player.getVideoInfoTag().getUniqueID("tmdb")
    season = player.getVideoInfoTag().getSeason()
    episode = player.getVideoInfoTag().getEpisode()
    subtitle_providers = get_providers()
    search_query = ""

    if media == "episode" and not tmdb_id:
        search_query = player.getVideoInfoTag().getTVShowTitle().lower()
    if media != "episode" and not tmdb_id:
        title = player.getVideoInfoTag().getOriginalTitle().lower()
        year = str(player.getVideoInfoTag().getYear())
        search_query = f"{title} {year}"

    handler_action = addon.getSettings().getInt("subtitle_handler_action")
    # TODO: Rewrite this because it needs to handle the filtering _before_ the download.
    # The question becomes - Do we try to get all the results from all providers?
    # Get all the results from all providers
    results_by_provider: Dict[str, List[Subtitle]] = {}
    for provider in subtitle_providers:
        results = await provider.search_subtitles(
            {
                "id": tmdb_id,
                "languages": languages,
                "media_type": media,
                "media_info": {"season": season, "episode": episode},
                "search": search_query,
            }
        )
        filtered_subtitles = filter_subtitles(
            results, languages, release_type, release_variants
        )
        if filtered_subtitles:
            results_by_provider[provider.__class__.__name__] = filtered_subtitles
            if not addon.getSettings().getBool(
                "exhaustive_search"
            ):  # Stop after the first set of results
                break

    download_links_by_provider: Dict[str, List[Downloadable]] = {}
    for provider in subtitle_providers:
        results = results_by_provider[provider.__class__.__name__]
        subtitle = provider.download_subtitle(results[0])
        if (
            handler_action == 0
        ):  # Use the first subtitle from the first provider that returned results
            if subtitle:
                download_links_by_provider[provider.__class__.__name__] = [subtitle]
                break
        elif (
            handler_action == 1
        ):  # Use the first subtitle from each provider that returns results
            subtitle = provider.download_subtitle(results[0])
            if subtitle:
                download_links_by_provider[provider.__class__.__name__] = [subtitle]
        else:  # Use all subtitles from each provider that returns results
            subtitles = [provider.download_subtitle(result) for result in results]
            subtitles = [subtitle for subtitle in subtitles if subtitle]
            download_links_by_provider[provider.__class__.__name__] = subtitles

    # TODO: This will require a custom modal that displays the results in a list but allows you to click to download the ones you want
    # elif handler_action == 4: # Manual Download

    if not download_links_by_provider:
        raise Exception("No suitable subtitles found.")
    # TODO: Handle multiple scenarios like - Download first, download all, etc.
    await save_subtitles(download_links_by_provider)
    notification(heading="Downloaded", message="Downloaded subtitles", time=3000)
