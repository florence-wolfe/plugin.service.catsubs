# Module: default
# Author: jurialmunkey & FloWolfe
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import xbmc

from importlib import import_module
from .logger import log


def importmodule(module_name, import_attr=None):
    module = import_module(module_name)
    if not import_attr:
        return module
    return getattr(module, import_attr)


class Script(object):
    def __init__(self, *args):
        self.params = {}
        for arg in args:
            self.params[arg] = True

    routing_table = {
        "exclude_subtitle_languages": lambda: importmodule(
            module_name="modules.routes.exclude_subtitle_languages",
            import_attr="exclude_subtitle_languages",
        )(),
        "exclude_audio_languages": lambda: importmodule(
            module_name="modules.routes.exclude_audio_languages",
            import_attr="exclude_audio_languages",
        )(),
        "exclude_words": lambda: importmodule(
            module_name="modules.routes.exclude_words",
            import_attr="exclude_words",
        )(),
    }

    def router(self):
        if not self.params:
            return
        routes_available = set(self.routing_table.keys())
        params_given = set(self.params.keys())
        route_taken = set.intersection(routes_available, params_given).pop()
        log(f"lib.modules.router - route_taken\t{route_taken}", level=xbmc.LOGDEBUG)
        return self.routing_table[route_taken](**self.params)
