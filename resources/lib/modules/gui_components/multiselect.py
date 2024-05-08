import xbmcgui
from typing import List, Optional, Sequence
from ..constants import addon


def get_multiselect_setting(setting_id: str) -> List[str]:
    return addon.getSettings().getStringList(setting_id)


def set_multiselect_setting(setting_id: str, selected_values: List[str]):
    addon.getSettings().setStringList(id=setting_id, values=selected_values)


def get_index_from_value(options: List[str], value: str) -> int:
    return options.index(value)


def get_value_from_index(options: List[str], index: int) -> str:
    return options[index]


def handle_multiselect_dialog(
    heading: str,
    options: List[str],
    setting_id: str,
    preselect: Optional[List[str]] = None,
) -> None:
    if preselect is None:
        preselect = get_multiselect_setting(setting_id)
    selected_values = show_multiselect(
        heading=heading,
        options=options,
        preselect=[get_index_from_value(options, value) for value in preselect],
    )
    if selected_values is not None:
        set_multiselect_setting(
            setting_id,
            [get_value_from_index(options, index) for index in selected_values],
        )


def show_multiselect(
    heading: str = "",
    options: Optional[Sequence[Optional[str]]] = None,
    preselect: Optional[Sequence[Optional[int]]] = None,
) -> List[int]:
    if options is None:
        options = []
    if preselect is None:
        preselect = []
    dialog = xbmcgui.Dialog()
    return dialog.multiselect(heading, options, preselect=preselect)
