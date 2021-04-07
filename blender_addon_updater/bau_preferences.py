import bpy
import sys
import os
import json
import time
import addon_utils

from bpy.types  import Operator, AddonPreferences
from bpy.props  import BoolProperty, StringProperty, EnumProperty, IntProperty


def get_addon():
    return sys.modules.get(__package__)


class BAU_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__

    dev_mode: BoolProperty(
        default = get_addon().bl_info['dev_version'] > 0
    )
    dev_ver: IntProperty(
        default = get_addon().bl_info['dev_version']
    )

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        bau = get_addon()

        self.dev_mode = get_addon().bl_info['dev_version'] > 0
        self.dev_ver = bau.bl_info['dev_version']

        addon_version = str(bau.bl_info['version']).replace("(","").replace(")","").replace(", ", ".")

        if self.dev_mode:
            row = layout.row()
            row.label(text="")
            
            col = row.column(align=True)
            col.alert = True
            col.alignment = 'RIGHT'
            col.label(text= "Development Version: " + str(addon_version) + "-dev." + str(self.dev_ver), icon='SETTINGS')

        layout.label(text="Registered Addons:", icon='FILE')

        for entry in wm.bau.addons:
            try:
                addon = sys.modules.get(entry.name)
            except KeyError:
                for idx in range(0, len(wm.bau.addons)):
                    if wm.bau.addons[idx].name not in sys.modules:
                        wm.bau.addons.remove(idx)
                continue

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
