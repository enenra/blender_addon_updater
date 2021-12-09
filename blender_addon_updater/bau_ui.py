import bpy
import sys
import json
import addon_utils
import time


def draw_bau_ui(self, context, element=None):
    wm = context.window_manager
    preferences = context.preferences.addons.get(__package__).preferences

    if element is None:
        layout = self.layout
    else:
        layout = element
    
    box = layout.box()
    row = box.row()
    row.label(text="Update Status", icon='FILE_REFRESH')

    addon = sys.modules.get(__package__)
    current_version_name = str(addon.bl_info['version']).replace("(","").replace(")","").replace(", ", ".")
    bau_entry = wm.bau.addons[__package__]

    col = row.column(align=True)
    row = col.row()
    row.alignment = 'RIGHT'

    row = row.row(align=True)
    op = row.operator('wm.bau_save_config', text="", icon='FILE_TICK')
    op.name = __package__
    op.config = str(get_config_json())
    op = row.operator('wm.url_open', text="Releases", icon='URL')
    op.url = addon.bl_info['git_url'] + "/releases"
    
    row = box.row(align=True)
    row.scale_y = 2.0
    split = row.split(align=True)

    if not bau_entry.dev_mode and bau_entry.rel_ver_needs_update:
        split.alert = True
        op = split.operator('wm.url_open', text=f"Update available: {bau_entry.latest_rel_ver_name}", icon='URL')
        op.url = addon.bl_info['git_url'] + "/releases/tag/v" + bau_entry.latest_rel_ver_name

    elif bau_entry.dev_mode and bau_entry.dev_ver_needs_update:
        split.alert = True
        op = split.operator('wm.url_open', text=f"Update available: {bau_entry.latest_dev_ver_name}", icon='URL')
        op.url = addon.bl_info['git_url'] + "/releases/tag/v" + bau_entry.latest_dev_ver_name

    else:
        if not preferences.dev_mode:
            split.operator('wm.bau_update_addon', text=f"Up to date: {current_version_name}", icon='CHECKMARK')
        else:
            split.operator('wm.bau_update_addon', text=f"Up to date: {current_version_name}-{addon.bl_info['dev_tag']}.{addon.bl_info['dev_version']}", icon='CHECKMARK')
        split.enabled = False

    split = row.split(align=True)
    op = split.operator('wm.bau_check_updates', text="", icon='FILE_REFRESH')
    op.name = __package__
    
    split = row.split(align=True)
    split.prop(bau_entry, 'dev_mode', text="", icon='SETTINGS')

    row = box.row(align=True)
    row.alignment = 'RIGHT'
    if bau_entry.connection_status != "Connected.":
        row.alert = True
        row.label(text=bau_entry.connection_status, icon='CANCEL')
    else:
        row.label(text= "Last check: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bau_entry.last_check)))

    if not bau_entry.dev_mode and bau_entry.rel_ver_needs_update:
        show_changelog(addon, box, bau_entry.rel_changelog, bau_entry.latest_rel_ver_name)

    elif bau_entry.dev_mode and bau_entry.dev_ver_needs_update:
        show_changelog(addon, box, bau_entry.dev_changelog, bau_entry.latest_dev_ver_name)


def show_changelog(addon, box, changelog, latest_ver_name):

    if changelog != "":
        text = json.loads(changelog)

        row = box.row(align=True)
        row.label(text="Changelog", icon='FILE_TEXT')

        counter = 0
        for item in text:
            if counter > 10:
                split = box.split(factor=0.75)
                split.label(text="...")

                op = split.operator('wm.url_open', text="More", emboss=False)
                op.url = addon.bl_info['git_url'] + "/releases/" + "v" + latest_ver_name
                break

            row = box.row()
            row.scale_y = 0.5
            row.label(text=item)
            counter += 1


def get_config_json():
    wm = bpy.context.window_manager

    data = {}
    data['blender_addon_updater'] = []

    for addon_entry in wm.bau.addons:
        if addon_entry.name == __package__:
            continue
        
        addon_info = {}
        addon_info['display_changelog'] = addon_entry.display_changelog
        addon_info['dev_mode'] = addon_entry.dev_mode
        addon_info['config'] = addon_entry.config

        data['blender_addon_updater'].append({
            addon_entry.name: addon_info
        })
    
    return data


def set_config_from_json(data):
    wm = bpy.context.window_manager

    if 'blender_addon_updater' in data:
        cfg = data['blender_addon_updater'][0]

        for key, value in cfg.items():
            if key in wm.bau.addons:
                wm.bau.addons[key].display_changelog = cfg[key]['display_changelog']
                wm.bau.addons[key].dev_mode = cfg[key]['dev_mode']
                wm.bau.addons[key].cfg = cfg[key]['config']

            elif addon_utils.check(key) == (True, True):
                bpy.ops.wm.bau_register_addon(name=key)
                wm.bau.addons[key].display_changelog = cfg[key]['display_changelog']
                wm.bau.addons[key].dev_mode = cfg[key]['dev_mode']
                wm.bau.addons[key].config = cfg[key]['config']