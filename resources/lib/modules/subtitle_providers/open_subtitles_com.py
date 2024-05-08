import httpx
from typing import Dict, Any, List
from ..subtitle_providers.i_provider import (
    ISubtitleProvider,
    Subtitle,
)
from ..subtitle_providers.auth_decorator import auth_required

BASE_URL = "https://api.opensubtitles.com/api/v1"
PROVIDER_NAME = "open_subtitles_com"


def parse_subtitle(subtitle_data: Dict[str, Any]) -> Subtitle:
    attributes = subtitle_data["attributes"]
    subtitle: Subtitle = {
        "release_name": attributes["release"],
        "name": attributes["files"][0]["file_name"],
        "lang": attributes["language"],
        "season": attributes["feature_details"]["season_number"],
        "episode": attributes["feature_details"]["episode_number"],
        "metadata": {"file_id": attributes["files"][0]["file_id"]},
    }
    return subtitle


class OpenSubtitlesCom(ISubtitleProvider):
    base_url = BASE_URL
    provider_name = PROVIDER_NAME

    def __init__(self):
        super().__init__()
        self.token = None
        if not self.api_key and not self.username and not self.password:
            raise Exception(f"Missing credentials for {self.provider_name} provider")

    async def login(self):
        url = "self.base_url/login"
        headers = {
            "Content-Type": "application/json",
            "Api-Key": self.api_key,
        }
        data = {
            "username": self.username,
            "password": self.password,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = await response.json()
                self.token = result["token"]
                return True
            else:
                print(f"Login failed with status code: {response.status_code}")
                return False

    def is_authenticated(self, status_code):
        return hasattr(self, "token") and self.token is not None and status_code != 401

    @auth_required
    async def search_subtitles(self, query):
        url = f"{self.base_url}/subtitles"
        headers = {
            "Api-Key": self.api_key,
        }
        params = {
            "languages": ",".join(query["languages"]),
            # TODO: Keep in mind there may be a mapping needed
            "type": query["media_type"],
        }

        if query.get("id"):
            params["id"] = query["id"]
        if query.get("search"):
            params["query"] = query["search"]
        if query.get("media_info"):
            if query["media_info"].get("episode_id"):
                params["episode_number"] = query["media_info"]["episode_id"]
            if query["media_info"].get("season_id"):
                params["season_number"] = query["media_info"]["season_id"]

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = await response.json()
            # Process the response data and return the list of subtitles
            subtitles: List[Subtitle] = []
            for subtitle_data in data.get("data", []):
                subtitle = parse_subtitle(subtitle_data)
                subtitles.append(subtitle)

            return subtitles

    @auth_required
    async def download_subtitle(self, subtitle):
        url = f"{self.base_url}/download"
        headers = {
            "Api-Key": self.api_key,
        }
        file_id = subtitle["metadata"]["file_id"]
        params = {
            # TODO: Keep in mind there may be a mapping needed
            "file_id": file_id,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = await response.json()
            return {
                "link": data["link"],
                "file_name": data["file_name"],
            }
