bl_info = {
    "name": "Equalize Edge Lengths",
    "author": "ChatGPT (for Олександр)",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Edit Mode > W (Context Menu) / Mesh > Edge",
    "description": "Make all selected edges the same length (average or custom) while preserving each edge direction",
    "category": "Mesh",
}

import bpy
import bmesh
from mathutils import Vector

def ensure_edit_bmesh(context):
    obj = context.edit_object
    if not obj or obj.type != 'MESH':
        raise RuntimeError("Switch to Edit Mode on a mesh object")
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    return bm, me

class MESH_OT_equalize_edge_lengths(bpy.types.Operator):
    """Set all selected edges to the same length (average or custom)"""
    bl_idname = "mesh.equalize_edge_lengths"
    bl_label = "Equalize Edge Lengths"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Length Mode",
        description="How to pick the target length",
        items=[
            ('AVERAGE', "Average of Selection", "Use average length of selected edges"),
            ('CUSTOM',  "Custom Value",        "Use the length specified below"),
        ],
        default='AVERAGE'
    )

    target_length: bpy.props.FloatProperty(
        name="Target Length",
        description="Edge length to apply when mode is Custom",
        default=0.1,
        min=0.0, soft_min=0.0
    )

    preserve_midpoint: bpy.props.BoolProperty(
        name="Preserve Midpoint",
        description="Move both endpoints around the edge midpoint (keeps edge center in place)",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "mode", expand=True)
        if self.mode == 'CUSTOM':
            layout.prop(self, "target_length")
        layout.prop(self, "preserve_midpoint")

    def execute(self, context):
        try:
            bm, me = ensure_edit_bmesh(context)
        except RuntimeError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        edges = [e for e in bm.edges if e.select]
        if not edges:
            self.report({'WARNING'}, "Select at least one edge")
            return {'CANCELLED'}

        # compute target length
        if self.mode == 'AVERAGE':
            total = 0.0
            count = 0
            for e in edges:
                L = e.calc_length()
                if L > 1e-12:
                    total += L
                    count += 1
            if count == 0:
                self.report({'WARNING'}, "All selected edges have zero length")
                return {'CANCELLED'}
            target = total / count
        else:
            target = max(self.target_length, 0.0)

        # apply per-edge
        moved = 0
        for e in edges:
            v1, v2 = e.verts
            vec = v2.co - v1.co
            L = vec.length
            if L < 1e-12:
                # If degenerate, try to infer a direction from connected geometry
                # Fallback: skip
                continue
            dirn = vec / L

            if self.preserve_midpoint:
                mid = (v1.co + v2.co) * 0.5
                half = dirn * (target * 0.5)
                v1.co = mid - half
                v2.co = mid + half
            else:
                # keep v1 fixed, move v2 along edge direction
                v2.co = v1.co + dirn * target

            moved += 1

        bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)
        self.report({'INFO'}, f"Equalized {moved} edges to length {target:.6f}")
        return {'FINISHED'}

# --- Menus ---

def menu_func_context(self, context):
    # W menu in Edit Mesh (Context Menu)
    layout = self.layout
    layout.separator()
    layout.operator(MESH_OT_equalize_edge_lengths.bl_idname, icon='MOD_LENGTH', text="Equalize Edge Lengths")

def menu_func_edge(self, context):
    # Mesh > Edge menu
    self.layout.separator()
    self.layout.operator(MESH_OT_equalize_edge_lengths.bl_idname, icon='MOD_LENGTH')

classes = (MESH_OT_equalize_edge_lengths,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func_context)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(menu_func_edge)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(menu_func_edge)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func_context)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
