from ..gui_components.multiselect import (
    handle_multiselect_dialog,
)
from ..constants import languages

language_keys = list(languages.keys())


def exclude_subtitle_languages():
    handle_multiselect_dialog(
        heading="Select Subtitle Languages to Exclude",
        options=language_keys,
        setting_id="excluded_subtitle_languages",
    )
