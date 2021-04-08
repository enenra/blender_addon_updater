import bpy
import sys

from bpy.types  import Operator
from bpy.props  import StringProperty, IntProperty, BoolProperty

from .bau_check_update  import check_update
from .bau_update_addon  import update_addon
from .bau_preferences   import save_config

class BAU_OT_RegisterAddon(Operator):
    """Registers the Addon with Blender Addon Updater"""
    bl_idname = "wm.bau_register_addon"
    bl_label = "Register Addon"
    bl_options = {'REGISTER', 'UNDO'}


    name: StringProperty()

    display_changelog: BoolProperty(
        default = False
    )
    dev_mode: BoolProperty(
        default = False
    )


    def execute(self, context):

        wm = context.window_manager
        addon = sys.modules.get(self.name)

        if self.name in wm.bau.addons:
            return {'FINISHED'}

        elif addon:
            entry = wm.bau.addons.add()
            entry.name = self.name
            entry.display_changelog = self.display_changelog
            entry.dev_mode = self.dev_mode

            check_update(entry, addon.bl_info['version'])

        else:
            return {'CANCELLED'}

        return {'FINISHED'}


class BAU_OT_UnregisterAddon(Operator):
    """Unregisters the addon from Blender Addon Updater"""
    bl_idname = "wm.bau_unregister_addon"
    bl_label = "Unregister Addon"
    bl_options = {'REGISTER', 'UNDO'}


    name: StringProperty()


    def execute(self, context):

        wm = context.window_manager

        for idx in range(0, len(wm.bau.addons)):
            if wm.bau.addons[idx].name == self.name:
                wm.bau.addons.remove(idx)
                break

        return {'FINISHED'}


class BAU_OT_CheckUpdates(Operator):
    """Checks whether the addon has updates available"""
    bl_idname = "wm.bau_check_updates"
    bl_label = "Check for Updates"
    bl_options = {'REGISTER', 'UNDO'}


    name: StringProperty()


    def execute(self, context):

        wm = context.window_manager
        addon = sys.modules.get(self.name)
        
        result = {'CANCELLED'}
        if self.name in wm.bau.addons and addon:
            addon_entry = wm.bau.addons[self.name]
            result = check_update(addon_entry, addon.bl_info['version'])

        return result


class BAU_OT_CheckAllUpdates(Operator):
    """Checks whether any registered addon has updates available"""
    bl_idname = "wm.bau_check_all_updates"
    bl_label = "Check All for Updates"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        wm = context.window_manager
        
        for addon_entry in wm.bau.addons:
            addon = sys.modules.get(addon_entry.name)
            result = check_update(addon_entry, addon.bl_info['version'])
            if result == {'FINISHED'}:
                print("BAU: Checked " + addon_entry.name + " for updates.")
            else:
                print("BAU: Unable to check " + addon_entry.name + " for updates.")

        return {'FINISHED'}


class BAU_OT_UpdateAddon(Operator):
    """Updates the addon"""
    bl_idname = "wm.bau_update_addon"
    bl_label = "Update"
    bl_options = {'REGISTER', 'UNDO'}


    name: StringProperty()

    config: StringProperty()


    def execute(self, context):

        wm = context.window_manager
        
        result = {'CANCELLED'}
        if self.name in wm.bau.addons:
            addon_entry = wm.bau.addons[self.name]
            addon_entry.config = self.config

            if not addon_entry.dev_mode or addon_entry.dev_mode and addon_entry.rel_ver_needs_update:
                result = update_addon(addon_entry, "v" + addon_entry.latest_rel_ver_name)
            else:
                result = update_addon(addon_entry, "v" + addon_entry.latest_dev_ver_name)
                
        return result


class BAU_OT_SaveConfig(Operator):
    """Saves the current config"""
    bl_idname = "wm.bau_save_config"
    bl_label = "Save Config"
    bl_options = {'REGISTER', 'UNDO'}


    name: StringProperty()
    
    config: StringProperty()


    def execute(self, context):

        wm = context.window_manager
        
        if self.name in wm.bau.addons:
            addon_entry = wm.bau.addons[self.name]
            addon_entry.config = self.config

        save_config()

        return {'FINISHED'}