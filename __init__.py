bl_info = {
    "name": "Blender Addon Updater",
    "description": "",
    "author": "enenra",
    "version": (0, 1, 0),
    "dev_version": 1,
    "blender": (2, 91, 0),
    "location": "Add-ons",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Utility"
}

import bpy
import sys

from bpy.app.handlers   import persistent
from bpy.props          import PointerProperty

from .bau_preferences           import BAU_AddonPreferences
from .bau_window_manager        import BAU_Addon
from .bau_window_manager        import BAU_WindowManager
from .bau_operators             import BAU_OT_RegisterAddon
from .bau_operators             import BAU_OT_UnregisterAddon
from .bau_operators             import BAU_OT_CheckUpdates
from .bau_operators             import BAU_OT_UpdateAddon
from .bau_operators             import BAU_OT_SaveConfig
from .bau_check_update          import check_update


classes = (
    BAU_AddonPreferences,
    BAU_Addon,
    BAU_WindowManager,
    BAU_OT_RegisterAddon,
    BAU_OT_UnregisterAddon,
    BAU_OT_CheckUpdates,
    BAU_OT_UpdateAddon,
    BAU_OT_SaveConfig
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.bau = PointerProperty(type=BAU_WindowManager)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.bau


def menu_func(self, context):
    for cls in classes:
        if str(cls).find("BAU_OT_") != -1:
            self.layout.operator(cls.bl_idname)


@persistent
def load_handler(dummy):
    wm = bpy.context.window_manager
    
    for entry in wm.bau.addons:
        addon = sys.modules.get(entry.name)
        check_update(entry, addon.bl_info['version'])
    
    # TODO: Add functionality to purge addon entries of addons that aren't installed anymore.


if __name__ == "__main__":
    register()
