import xbmcgui
from modules.gui_components.custom_list import handle_custom_list_dialog


def exclude_audio_languages():
    handle_custom_list_dialog(
        title="Add words to Exclude",
        setting_id="excluded_words",
        add_callback=lambda: xbmcgui.Dialog().input(
            heading="Enter word to exclude from subtitle search results."
        ),
        edit_callback=lambda label: xbmcgui.Dialog().input(
            heading="Edit word to exclude from subtitle search results.",
            defaultt=label,
        ),
    )
