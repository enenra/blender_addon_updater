import bpy
import sys
import os
import json
import time
import addon_utils

from bpy.types  import Operator, AddonPreferences
from bpy.props  import BoolProperty, StringProperty, EnumProperty, IntProperty

from .bau_ui    import draw_bau_ui, get_config_json, set_config_from_json


def get_addon():
    return sys.modules.get(__package__)


class BAU_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__

    dev_mode: BoolProperty(
        default = get_addon().bl_info['dev_version'] > 0
    )

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        bau = get_addon()

        self.dev_mode = get_addon().bl_info['dev_version'] > 0

        addon_version = str(bau.bl_info['version']).replace("(","").replace(")","").replace(", ", ".")

        if __package__ in wm.bau.addons:
            draw_bau_ui(self, context, layout)

        top_box = layout.box()
        row = top_box.row()
        row.label(text="Registered Addons:", icon='FILE')

        col = row.column(align=True)
        row = col.row()
        row.scale_y = 1.5
        row.scale_x = 1.5
        row.alignment = 'RIGHT'
        if len(wm.bau.addons) < 1:
            row.enabled = False
        row.operator('wm.bau_check_all_updates', text="", icon='FILE_REFRESH')

        for entry in wm.bau.addons:
            try:
                addon = sys.modules.get(entry.name)
            except KeyError:
                for idx in range(0, len(wm.bau.addons)):
                    if addon_utils.check(wm.bau.addons[idx].name) == (False, False):
                        wm.bau.addons.remove(idx)
                        break
                continue
            
            if entry.name == __package__:
                continue

            box = top_box.box()
            row = box.row()
            version = str(addon.bl_info['version']).replace("(", "").replace(")", "").replace(", ", ".")
            row.label(text= addon.bl_info['category'] + ": " + addon.bl_info['name'] + " " + version, icon=addon.bl_info['support'])

            if self.dev_mode:
                col = row.column(align=True)
                row = col.row(align=True)
                row.alignment = 'RIGHT'


                op = row.operator('wm.bau_update_addon', text="", icon='IMPORT')
                op.name = entry.name
                row.alert = False
                op = row.operator('wm.bau_check_updates', text="", icon='FILE_REFRESH')
                op.name = entry.name
                row.prop(entry, 'dev_mode', text="", icon='SETTINGS')
                op = row.operator('wm.url_open', text="", icon='URL')
                op.url = addon.bl_info['git_url'] + "/releases"
                op = row.operator('wm.bau_unregister_addon', text="", icon='UNLINKED')
                op.name = entry.name

            col = box.column(align=True)
            row = col.row(align=True)

            split = row.split()
            if entry.connection_status != "Connected.":
                split.alert = True
                split.label(text=entry.connection_status, icon='CANCEL')
            else:
                if not entry.dev_mode and entry.rel_ver_needs_update or entry.dev_mode and entry.dev_ver_needs_update:
                    split.alert = True
                    split.label(text="Update available", icon='ERROR')
                else:
                    split.label(text="Up to date", icon='CHECKMARK')
            
                split = row.split()
                split.alignment = 'RIGHT'
                split.label(text= "Last check: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry.last_check)))


def save_config():

    path = os.path.join(bpy.utils.user_resource('CONFIG'), 'blender_addon_updater.cfg')

    data = get_config_json()
    
    with open(path, 'w') as cfg_file:
        json.dump(data, cfg_file, indent = 4)


def load_config():

    path = os.path.join(bpy.utils.user_resource('CONFIG'), 'blender_addon_updater.cfg')

    if os.path.exists(path):
        with open(path) as cfg_file:
            data = json.load(cfg_file)
            set_config_from_json(data)