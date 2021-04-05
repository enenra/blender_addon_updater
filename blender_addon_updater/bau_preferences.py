import bpy
import sys
import os
import json
import time
import addon_utils

from bpy.types  import Operator, AddonPreferences
from bpy.props  import BoolProperty, StringProperty, EnumProperty, IntProperty


DEV_MODE = True


class BAU_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__

    dev_mode: BoolProperty(
        default = DEV_MODE
    )
    dev_ver: IntProperty(
        default = sys.modules.get(__package__).bl_info['dev_version']
    )

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        bau = sys.modules.get(__package__)

        self.dev_mode = DEV_MODE
        self.dev_ver = bau.bl_info['dev_version']

        addon_version = str(bau.bl_info['version']).replace("(","").replace(")","").replace(", ", ".")

        if self.dev_mode:
            row = layout.row()
            row.label(text="")
            
            col = row.column(align=True)
            col.alert = True
            col.alignment = 'RIGHT'
            col.label(text= str(addon_version) + "-alpha." + str(self.dev_ver), icon='CANCEL')

        layout.label(text="Registered Addons:", icon='FILE')

        for entry in wm.bau.addons:
            addon = sys.modules.get(entry.name)

            if addon is None:
                return

            box = layout.box()
            row = box.row()
            version = str(addon.bl_info['version']).replace("(", "").replace(")", "").replace(", ", ".")
            row.label(text= addon.bl_info['category'] + ": " + addon.bl_info['name'] + " " + version)

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


def get_addon():
    return bpy.context.preferences.addons.get(__package__)


def save_addon_prefs():

    addon = get_addon()
    path = os.path.join(addon_utils.paths()[1], addon + '.cfg')
    preferences = addon.preferences

    data = {}
    data[addon] = []
    data[addon].append({
        'materials_path': preferences.materials_path,
        'mwmb_path': preferences.mwmb_path,
        'fbx_importer_path': preferences.fbx_importer_path,
        'havok_path': preferences.havok_path
    })
    
    with open(path, 'w') as cfg_file:
        json.dump(data, cfg_file, indent = 4)


def load_addon_prefs():

    addon = get_addon()
    path = os.path.join(addon_utils.paths()[1], addon + '.cfg')
    preferences = addon.preferences

    if os.path.exists(path):
        with open(path) as cfg_file:
            data = json.load(cfg_file)

            if addon in data:
                cfg = data[addon]
                preferences.materials_path = cfg['materials_path']
                preferences.mwmb_path = cfg['mwmb_path']
                preferences.fbx_importer_path = cfg['fbx_importer_path']
                preferences.havok_path = cfg['havok_path']