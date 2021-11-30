import bpy
import os
import sys
import requests
import json
import tempfile
import shutil
import zipfile
import glob


def update_addon(addon_entry, tag):

    wm = bpy.context.window_manager
    addon = sys.modules.get(addon_entry.name)
    
    git_url = addon.bl_info['git_url'].replace("github.com/", "api.github.com/repos/")
    response_releases = requests.get(git_url + "/releases")

    addon_entry.connection_status = "Connected."

    try:
        if response_releases.status_code == 200:
            json_releases = response_releases.json()
            
            found = False
            for release in json_releases:
                if release['tag_name'] == tag:

                    if addon_entry.download_method == 'zipball':
                        download_url = release['zipball_url']
                        found = True
                        break

                    elif addon_entry.download_method == 'asset' and 'assets' in release:
                        for asset in release['assets']:
                            if asset['name'].endswith(f"{addon_entry.name}_{tag}.zip"):
                                download_url = release['browser_download_url']
                                found = True
                                break
                        break
            
            if found:
                print("FOUND")
                return {'FINISHED'}
                directory = tempfile.mkdtemp()
                download_path = os.path.join(directory, addon_entry.name + "_" + tag + ".zip")

                try:
                    addon_zip = download_repackage_zip(download_url, directory, download_path)
                except Exception as e:
                    print(e)
                    shutil.rmtree(directory)
                    return {'CANCELLED'}
                
                new_name = os.path.splitext(os.path.basename(addon_zip))[0]

                try:
                    bpy.ops.preferences.addon_remove(module=addon_entry.name)
                    bpy.ops.preferences.addon_install(overwrite=True, target='DEFAULT', filepath=addon_zip)

                    bpy.ops.preferences.addon_enable(module=new_name)
                    bpy.ops.preferences.addon_show(module=new_name)
                    
                except Exception as e:
                    print(e)
                    return {'CANCELLED'}

                shutil.rmtree(directory)

                return {'FINISHED'}

            else:
                addon_entry.connection_status = "Release could not be found."
                return {'CANCELLED'}
            

        elif response_releases.status_code == 403:
            addon_entry.connection_status = "Rate limit exceeded!"
            return {'CANCELLED'}

    except Exception as e:
        print(e)
        addon_entry.connection_status = "Connection Failed!"
        return {'CANCELLED'}


def download_repackage_zip(url, directory, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        extracted_dir = zip_ref.extractall(directory)
    
    os.remove(save_path)

    init = glob.glob(directory + "/**/__init__.py", recursive = True)[0]
    addon_dir = os.path.dirname(init)
    addon_name = os.path.basename(addon_dir)

    shutil.copytree(addon_dir, os.path.join(directory, 'temp', addon_name))
    temp_folder = os.path.join(directory, 'temp')

    new_zip = shutil.make_archive(os.path.join(directory, addon_name), 'zip', temp_folder)
    
    return new_zip