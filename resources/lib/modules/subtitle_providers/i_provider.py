from abc import ABC, abstractmethod
from typing import List, Dict, Optional, TypedDict
from ..constants import addon


# TODO: Define a stricter type that the providers should adhere to
class Subtitle(TypedDict):
    # Provider-specific fields
    name: str
    release_name: Optional[str]
    lang: str
    season: int
    episode: int
    metadata: Dict[str, str]


class Downloadable(TypedDict):
    file_name: str
    link: str


class MediaInfo(TypedDict):
    episode_id: str
    season_id: str


class Query(TypedDict):
    id: str
    languages: List[str]
    media_type: str
    media_info: Optional[MediaInfo]
    search: Optional[str]


# PROVIDERS
# subdl
# addic7ed
# subscene
# isubtitles
# Bazarr --- winner winner chicken dinner
# :point_up: requires checking _which_ services are enabled and using those instead of the configured ones from the add-on


class ISubtitleProvider(ABC):
    """
    Interface for a subtitle provider. Implementations should be able to search and download subtitles.
    """

    base_url: str
    provider_name: str
    token: Optional[str]

    def __init__(self):
        """
        Initialize the subtitle provider with the base URL and authentication credentials.
        """
        self.username = addon.getSetting(f"{self.provider_name}_username")
        self.password = addon.getSetting(f"{self.provider_name}_password")
        self.api_key = addon.getSetting(f"{self.provider_name}_api_key")

        if not self.username and not self.password and not self.api_key:
            raise Exception(f"Missing credentials for {self.provider_name} provider")

    def is_enabled(self) -> bool:
        """
        Check if the provider is enabled in the add-on settings.
        :return: True if enabled, False otherwise.
        """
        return addon.getSettings().getBool(f"{self.provider_name}_enabled")

    @abstractmethod
    def is_authenticated(self, status_code: Optional[int] = None) -> bool:
        """
        Check if the provider is currently authenticated.
        :return: True if authenticated, False otherwise.
        """
        pass

    @abstractmethod
    async def login(self) -> None:
        """
        Authenticate with the subtitle provider using the provided credentials.
        """
        pass

    @abstractmethod
    async def search_subtitles(self, query: Query) -> List[Subtitle]:
        """
        Search the provider for subtitles based on the given query.
        :param query: The search query for subtitles.
        :return: List of found subtitles. If no results are found, return an empty list.
        """
        pass

    @abstractmethod
    async def download_subtitle(self, subtitle: Subtitle) -> Optional[Downloadable]:
        """
        Download the specified subtitle from the provider.
        :param subtitle: The subtitle to download.
        :return: Path to the downloaded subtitle file. If the download fails, return None.
        """
        pass
