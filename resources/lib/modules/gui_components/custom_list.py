import xbmcgui
from typing import Optional, Callable
from modules.constants import addon

AddCallback = Callable[[], Optional[str]]
EditCallback = Callable[[str], Optional[str]]


class CustomListDialog(xbmcgui.WindowDialog):
    def __init__(self, title="", setting_id="", add_callback=None, edit_callback=None):
        super().__init__()
        self.setting_id = setting_id
        self.ok_button: Optional[xbmcgui.ControlButton] = None
        self.remove_button: Optional[xbmcgui.ControlButton] = None
        self.add_button: Optional[xbmcgui.ControlButton] = None
        # The list visually displayed in the dialog
        self.list_control: Optional[xbmcgui.ControlList] = None
        self.cancel_button: Optional[xbmcgui.ControlButton] = None
        self.title = title
        self.edit_callback: EditCallback = edit_callback
        self.add_callback: AddCallback = add_callback
        self.create_controls()

    def create_controls(self):
        # Create the Title
        self.addControl(
            xbmcgui.ControlLabel(
                x=400,
                y=20,
                width=800,
                height=40,
                label=self.title,
                alignment=0x00000002,
            )
        )

        self.list_control = xbmcgui.ControlList(x=50, y=80, width=700, height=400)
        self.addControl(self.list_control)

        items = addon.getSettings().getStringList(self.setting_id)
        self.list_control.addItems(items)

        self.add_button = xbmcgui.ControlButton(
            x=50, y=500, width=200, height=40, label="Add"
        )
        self.addControl(self.add_button)

        self.remove_button = xbmcgui.ControlButton(
            x=300, y=500, width=200, height=40, label="Remove"
        )
        self.addControl(self.remove_button)

        self.ok_button = xbmcgui.ControlButton(
            x=550, y=500, width=200, height=40, label="OK"
        )
        self.addControl(self.ok_button)

        self.cancel_button = xbmcgui.ControlButton(
            x=550, y=560, width=200, height=40, label="Cancel"
        )
        self.addControl(self.cancel_button)

    def onControl(self, control):
        if control == self.add_button:
            if callable(self.add_callback):
                item = self.add_callback()
                if item is not None:
                    self.list_control.addItem(item)
        elif control == self.remove_button:
            selected_index = self.list_control.getSelectedPosition()
            self.list_control.removeItem(selected_index)
        elif control == self.ok_button:
            selected_items = [
                self.list_control.getListItem(i).getLabel()
                for i in range(self.list_control.size())
            ]
            addon.getSettings().setStringList(self.setting_id, selected_items)
            self.close()
        elif control == self.cancel_button:
            self.close()
        elif control == self.list_control:
            selected_index = self.list_control.getSelectedPosition()
            if callable(self.edit_callback):
                item_label = self.list_control.getListItem(selected_index).getLabel()
                edited_item = self.edit_callback(item_label)
                if edited_item is not None:
                    self.list_control.getListItem(selected_index).setLabel(edited_item)


def handle_custom_list_dialog(
    title: str = "",
    setting_id: str = "",
    add_callback: AddCallback = None,
    edit_callback: EditCallback = None,
):
    dialog = CustomListDialog(
        title=title,
        setting_id=setting_id,
        add_callback=add_callback,
        edit_callback=edit_callback,
    )
    dialog.doModal()
    del dialog
