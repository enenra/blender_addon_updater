import bpy
import sys
import re
import requests
import json
import time


rel_ver = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+$")
dev_ver = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+\-\w+\.[0-9]{1,}$")

tags = {
    'dev': 0,
    'alpha': 1,
    'beta': 2,
    'rc': 3
}

def check_update(addon_entry):

    addon = sys.modules.get(addon_entry.name)
    git_url = addon.bl_info['git_url'].replace("github.com/", "api.github.com/repos/")
    current_version = addon.bl_info['version']

    try:
        response_tags = requests.get(git_url + "/tags")
        response_releases = requests.get(git_url + "/releases")
    except Exception as e:
        print(e)
        addon_entry.connection_status = "Connection Failed!"
        return {'CANCELLED'}

    addon_entry.connection_status = "Connected."

    try:
        if response_tags.status_code == 200 and response_releases.status_code == 200:
            json_tags = response_tags.json()
            json_releases = response_releases.json()

            rel_versions = list()
            dev_versions = list()

            for tag in json_tags:
                name_tag = tag['name']

                for release in json_releases:
                    name_release = release['tag_name']
                    prerelease = release['prerelease']

                    if name_tag == name_release:

                        if prerelease and dev_ver.match(name_tag):
                            dev_versions.append(name_tag)

                        elif not prerelease and rel_ver.match(name_tag):
                            rel_versions.append(name_tag)
            
            if len(rel_versions) > 0:
                latest_rel_ver_name = sorted(rel_versions, reverse=True)[0]
                latest_rel_version = tuple(map(int, latest_rel_ver_name[1:].split('.')))

                if current_version < latest_rel_version:
                    addon_entry.rel_ver_needs_update = True
                else:
                    addon_entry.rel_ver_needs_update = False
                    
                addon_entry.latest_rel_ver_name = latest_rel_ver_name[1:]

            if len(dev_versions) > 0:
                latest_dev_ver_name = sorted(dev_versions, reverse=True)[0]
                base_version = latest_dev_ver_name[:latest_dev_ver_name.find("-")]
                latest_dev_version = tuple(map(int, base_version[1:].split('.')))

                dev_tag = latest_dev_ver_name[latest_dev_ver_name.find("-") + 1:]
                dev_tag = dev_tag[:dev_tag.find(".")]

                if dev_tag not in tags:
                    addon_entry.dev_ver_needs_update = False
                
                else:
                    dev_version = latest_dev_ver_name[latest_dev_ver_name.find("-") + 1:]
                    dev_version = dev_version[dev_version.find(".") + 1:]

                    if current_version < latest_dev_version or len(rel_versions) > 0 and current_version < latest_rel_version:
                        addon_entry.dev_ver_needs_update = True
                    elif current_version == latest_dev_version and tags[addon.bl_info['dev_tag']] < tags[dev_tag]:
                        addon_entry.dev_ver_needs_update = True
                    elif current_version == latest_dev_version and tags[addon.bl_info['dev_tag']] == tags[dev_tag] and addon.bl_info['dev_version'] < int(dev_version):
                        addon_entry.dev_ver_needs_update = True
                    else:
                        addon_entry.dev_ver_needs_update = False
                        
                    addon_entry.latest_dev_ver_name = latest_dev_ver_name[1:]
            
            # Special case where there is a newer release version than the installed dev version
            if len(rel_versions) > 0 and len(dev_versions) < 1 and current_version < latest_rel_version:
                addon_entry.dev_ver_needs_update = True
                addon_entry.latest_dev_ver_name = latest_rel_ver_name[1:]

                
            for release in json_releases:
                if len(rel_versions) > 0 and release['tag_name'] == latest_rel_ver_name:
                    rel_changelog = release['body']
                    if rel_changelog.find("# Changelog") != -1:
                        addon_entry.rel_changelog = json.dumps(parse_release_notes(rel_changelog))

                        # Special case again
                        if current_version < latest_rel_version:
                            addon_entry.dev_changelog = json.dumps(parse_release_notes(rel_changelog))

                elif len(dev_versions) > 0 and release['tag_name'] == latest_dev_ver_name:
                    dev_changelog = release['body']
                    if dev_changelog.find("# Changelog") != -1:
                        addon_entry.dev_changelog = json.dumps(parse_release_notes(dev_changelog))


            addon_entry.last_check = time.time()
            return {'FINISHED'}

        elif response_tags.status_code == 403 or response_releases.status_code == 403:
            addon_entry.connection_status = "Rate limit exceeded!"
            return {'CANCELLED'}
    
    except Exception as e:
        print(e)
        addon_entry.connection_status = "Connection Failed!"
        return {'CANCELLED'}


def parse_release_notes(body):
    body = body.replace("\r", "")
    body = body.replace("`", "")
    body = body[body.find("Changelog"):]
    body = body[:body.find("\n# ")]

    array = body.split("\n")
    array.remove(array[0])

    return array