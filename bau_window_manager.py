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


class BAU_Addon(PropertyGroup):

    name: StringProperty()

    config: StringProperty()

    display_changelog: BoolProperty(
        default = False
    )

    latest_rel_ver_name: StringProperty()
    rel_changelog: StringProperty()
    rel_ver_needs_update: BoolProperty(
        default = False
    )

    latest_dev_ver_name: StringProperty()
    dev_changelog: StringProperty()
    dev_ver_needs_update: BoolProperty(
        default = False
    )

    connection_status: StringProperty()
    last_check: FloatProperty(
        subtype='TIME',
        unit='TIME'
    )

    dev_mode: BoolProperty(
        name = "Dev Mode",
        description = "Whether to include development version",
        default = False
    )


class BAU_WindowManager(PropertyGroup):

    addons: CollectionProperty(
        type = BAU_Addon
    )

    connection_status: StringProperty()