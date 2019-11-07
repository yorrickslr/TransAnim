import bpy
import json
from bpy_extras.io_utils import ExportHelper, axis_conversion
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import Operator


bl_info = {
    "name": "Export TransAnim",
    "category": "Import-Export",
    "location": "File > Export > TransAnim (.json)",
    "author": "yorrickslr",
}


def appendMatToList(list, mat):
    matrix1d = []
    ogltransform = axis_conversion(from_forward="-Y", from_up="Z", to_forward="-Z", to_up="Y").to_4x4();
    oglmat = ogltransform * mat;
    for row in range(0,4):
        for column in range(0,4):
            matrix1d.append(oglmat[row][column])
    list.append(matrix1d)


class ExportTransAnim(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_trans_anim.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export TransAnim"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    samplerate = FloatProperty(
            name="Samplerate",
            description="Sample every nth transformation of the selected object",
            min=1,soft_min=1,
            default=1,
            precision=0,
            step=1
            )

    def execute(self, context):
        if len(bpy.context.selected_objects) < 1:
            self.report({'ERROR_INVALID_INPUT'}, "Please select one object!");
            return {'CANCELLED'}
        samplerate = int(round(self.samplerate))
        start = bpy.context.scene.frame_start
        end = bpy.context.scene.frame_end
        for obj in bpy.context.selected_objects:
            transformations = []
            for frame in range(start, end + 1, samplerate):
                bpy.context.scene.frame_set(frame)
                appendMatToList(transformations, obj.matrix_world)
            if len(bpy.context.selected_objects) == 1:
                f = open(self.filepath, 'w', encoding='utf-8')
            else:
                f = open(self.filepath[:-5] + "." + obj.name + ".json", 'w', encoding='utf-8')
            json.dump({
                "length": (end - start) + 1,
                "samplerate": samplerate,
                "frames": transformations
            }, f, indent=2)
            f.close()
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportTransAnim.bl_idname, text="TransAnim (.json)")


def register():
    bpy.utils.register_class(ExportTransAnim)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportTransAnim)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
