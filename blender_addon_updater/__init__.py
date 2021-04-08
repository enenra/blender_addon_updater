bl_info = {
    "name": "Blender Addon Updater",
    "description": "",
    "author": "enenra",
    "version": (0, 1, 0),
    "dev_version": 3,
    "dev_tag": 'alpha',
    "blender": (2, 92, 0),
    "location": "Add-ons",
    "warning": "",
    "wiki_url": "https://github.com/enenra/blender_addon_updater/wiki",
    "tracker_url": "https://github.com/enenra/blender_addon_updater/issues",
    "git_url": "https://github.com/enenra/blender_addon_updater",
    "support": "COMMUNITY",
    "category": "Utility"
}

import bpy
import sys
import addon_utils

from bpy.app.handlers   import persistent
from bpy.props          import PointerProperty

from .bau_preferences           import BAU_AddonPreferences
from .bau_preferences           import save_config
from .bau_preferences           import load_config
from .bau_window_manager        import BAU_Addon
from .bau_window_manager        import BAU_WindowManager
from .bau_operators             import BAU_OT_RegisterAddon
from .bau_operators             import BAU_OT_UnregisterAddon
from .bau_operators             import BAU_OT_CheckUpdates
from .bau_operators             import BAU_OT_CheckAllUpdates
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
    BAU_OT_CheckAllUpdates,
    BAU_OT_UpdateAddon,
    BAU_OT_SaveConfig
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.bau = PointerProperty(type=BAU_WindowManager)
    bpy.app.timers.register(bau_loop)
    bpy.app.timers.register(bau_self_register)


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
    
    load_config()


def bau_self_register():
    wm = bpy.context.window_manager

    try:
        if __package__ not in wm.bau.addons:
            result = bpy.ops.wm.bau_register_addon(name = __package__, display_changelog=True, dev_mode=bl_info['dev_version'] > 0)
            if not result == {'FINISHED'}:
                return 5.0
        bpy.app.timers.unregister(bau_self_register)
    except:
        return 5.0


def bau_loop():
    wm = bpy.context.window_manager

    try:
        for idx in range(0, len(wm.bau.addons)):
            if addon_utils.check(wm.bau.addons[idx].name) == (False, False):
                wm.bau.addons.remove(idx)
                return 1

        for entry in wm.bau.addons:
            addon = sys.modules.get(entry.name)
            check_update(entry, addon.bl_info['version'])

        save_config()

        return 600

    except Exception as e:
        print(e)
        return 600


if __name__ == "__main__":
    register()
