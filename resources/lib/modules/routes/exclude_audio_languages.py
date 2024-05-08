from modules.gui_components.multiselect import (
    handle_multiselect_dialog,
)
from modules.constants import languages

language_keys = list(languages.keys())


def exclude_audio_languages():
    handle_multiselect_dialog(
        heading="Select audio Languages to Exclude",
        options=language_keys,
        setting_id="excluded_audio_languages",
    )
