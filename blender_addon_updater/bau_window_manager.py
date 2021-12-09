import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       IntVectorProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       CollectionProperty,
                       )

from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )


def update_rel_ver_needs_update(self, context):
    if not self.rel_ver_needs_update and not self.dev_ver_needs_update:
        if self.display_instructions:
            self.display_instructions = False


def update_dev_ver_needs_update(self, context):
    if not self.rel_ver_needs_update and not self.dev_ver_needs_update:
        if self.display_instructions:
            self.display_instructions = False


class BAU_Addon(PropertyGroup):

    name: StringProperty()

    config: StringProperty()

    display_changelog: BoolProperty(
        default = False
    )

    display_instructions: BoolProperty(
        default = False
    )

    latest_rel_ver_name: StringProperty()
    rel_changelog: StringProperty()
    rel_ver_needs_update: BoolProperty(
        default = False,
        update = update_rel_ver_needs_update
    )

    latest_dev_ver_name: StringProperty()
    dev_changelog: StringProperty()
    dev_ver_needs_update: BoolProperty(
        default = False,
        update = update_dev_ver_needs_update
    )

    connection_status: StringProperty()
    last_check: FloatProperty(
        subtype='TIME',
        unit='TIME'
    )

    download_method: EnumProperty(
        name='Download Method',
        items=(
            ('zipball', 'Zipball', ''),
            ('asset', 'Asset', '')
            ),
        default='zipball'
    )

    dev_mode: BoolProperty(
        name = "Dev Mode",
        description = "Whether to include development versions",
        default = False
    )


class BAU_WindowManager(PropertyGroup):

    addons: CollectionProperty(
        type = BAU_Addon
    )

    connection_status: StringProperty()