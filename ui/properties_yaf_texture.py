# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
import bpy
from rna_prop_ui import PropertyPanel
from bpy.props import *
Texture = bpy.types.Texture

#narrowui = bpy.context.user_preferences.view.properties_width_check
narrowui = 300

Texture.yaf_tex_type = EnumProperty(attr="yaf_tex_type",
        items = (
                ("TEXTURE_TYPE","Texture Type",""),
                ("NONE","None",""),
                ("BLEND","Blend",""),
                ("CLOUDS","Clouds",""),
                ("WOOD","Wood",""),
                ("MARBLE","Marble",""),
                ("VORONOI","Voronoi",""),
                ("MUSGRAVE","Musgrave",""),
                ("DISTORTED_NOISE","Distorted Noise",""),
                ("IMAGE","Image",""),
),default="NONE")

Texture.yaf_texture_coordinates = EnumProperty(attr="yaf_texture_coordinates",
        items = (
                ("TEXTURE_COORDINATES","Texture Co-Ordinates",""),
                ("GLOBAL","Global",""),
                ("ORCO","Orco",""),
                ("WINDOW","Window",""),
                ("NORMAL","Normal",""),
                ("REFLECTION","Reflection",""),
                ("STICKY","Sticky",""),
                ("STRESS","Stress",""),
                ("TANGENT","Tangent",""),
                ("OBJECT","Object",""),
                ("UV","UV",""),
),default="GLOBAL")

Texture.tex_file_name = StringProperty(attr='tex_file_name', subtype = 'FILE_PATH')

from properties_material import active_node_mat


def context_tex_datablock(context):
    idblock = context.material
    if idblock:
        return active_node_mat(idblock)

    idblock = context.lamp
    if idblock:
        return idblock

    idblock = context.world
    if idblock:
        return idblock

    idblock = context.brush
    return idblock

class YAF_TextureButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"
    COMPAT_ENGINES = {'YAFA_RENDER'}

    @classmethod #no 2.53
    def poll(self, context):
        tex = context.texture
        engine = context.scene.render.engine

        return tex and (tex.type != 'NONE') and (engine in self.COMPAT_ENGINES)



class YAF_TEXTURE_PT_context_texture(YAF_TextureButtonsPanel, bpy.types.Panel):
    bl_label = "YafaRay Textures"
    bl_show_header = True # False orig.
    COMPAT_ENGINES = {'YAFA_RENDER'}
    count = 0

    @classmethod
    def poll(self, context):
        engine = context.scene.render.engine
        if not hasattr(context, "texture_slot"):
            return False
        ##

        import properties_world

        import properties_texture

        if (context.world  and  (engine in self.COMPAT_ENGINES) ) :
            try :
                properties_world.unregister()
            except:
                pass
        else:
            try:
                properties_world.register()
            except:
                pass
        if (context.texture and  (engine in self.COMPAT_ENGINES) ) :
            try :
                properties_texture.unregister()
            except:
                pass
        else:
            try:
                properties_texture.register()
            except:
                pass
        #return (context.texture  or context.world and  (engine in self.COMPAT_ENGINES) )
        return ((context.material or context.world or context.lamp or context.brush or context.texture)
            and (engine in self.COMPAT_ENGINES))


    def draw(self, context):
        layout = self.layout
        slot = context.texture_slot
        node = context.texture_node
        space = context.space_data
        tex = context.texture
        idblock = context_tex_datablock(context)
        pin_id = space.pin_id

        if not isinstance(pin_id, bpy.types.Material): # isinstance, recen change  for beta 2.56
            pin_id = None

        tex_collection = (pin_id is None) and (node is None) and (not isinstance(idblock, bpy.types.Brush))

        wide_ui = context.region.width > narrowui

        if tex_collection:
            row = layout.row()

            row.template_list(idblock, "texture_slots", idblock, "active_texture_index", rows=2)

            #col = row.column(align=True)
            #col.operator("texture.slot_move", text="", icon='TRIA_UP').type = 'UP'
            #col.operator("texture.slot_move", text="", icon='TRIA_DOWN').type = 'DOWN'
            #col.menu("TEXTURE_MT_specials", icon='DOWNARROW_HLT', text="")

        if wide_ui:
            split = layout.split(percentage=0.65)
            col = split.column()
        else:
            col = layout.column()

        if tex_collection:
            col.template_ID(idblock, "active_texture", new="texture.new")
        elif node:
            col.template_ID(node, "texture", new="texture.new")
        elif idblock:
            col.template_ID(idblock, "texture", new="texture.new")

        if space.pin_id:
            col.template_ID(space, "pin_id")

        if wide_ui:
            col = split.column()

        #if not space.pin_id:
        #    col.prop(space, "brush_texture", text="Brush", toggle=True)

        if tex:
            split = layout.split(percentage=0.2)

            if tex.use_nodes:

                if slot:
                    split.label(text="Output:")
                    split.prop(slot, "output_node", text="")

            else:
                if wide_ui:
                    split.label(text="Type:")
                    split.prop(tex, "type", text="")

                else:
                    layout.prop(tex, "type", text="", icon= "TEXTURE")



class YAF_TEXTURE_PT_preview(YAF_TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Preview"
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        slot = getattr(context, "texture_slot", None)
        idblock = context_tex_datablock(context)

        if idblock:
            layout.template_preview(tex, parent=idblock, slot=slot)
        else:
            layout.template_preview(tex, slot=slot)

# Texture Slot Panels #

class YAF_TextureSlotPanel(YAF_TextureButtonsPanel):
    #bl_label = "Slots Textures"
    COMPAT_ENGINES = {'YAFA_RENDER'}

    @classmethod
    def poll(self, context):
        if not hasattr(context, "texture_slot"):
            return False

        engine = context.scene.render.engine
        return TextureButtonsPanel.poll(self, context) and (engine in self.COMPAT_ENGINES)


class YAF_TEXTURE_PT_mapping(YAF_TextureSlotPanel, bpy.types.Panel):
    bl_label = "YafaRay Mapping (Map Input)"
    COMPAT_ENGINES = {'YAFA_RENDER'}

    @classmethod
    def poll(self, context):
        idblock = context_tex_datablock(context)
        if isinstance(idblock, bpy.types.Brush) and not context.sculpt_object:
            return False

        if not getattr(context, "texture_slot", None):
            return False

        engine = context.scene.render.engine
        return (engine in self.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        idblock = context_tex_datablock(context)

        #yaf_tex_type = context.texture_slot

        tex = context.texture_slot
        wide_ui = context.region.width > narrowui

        if not isinstance(idblock, bpy.types.Brush):
            split = layout.split(percentage=0.3)
            col = split.column()
            col.label(text="Coordinates:")
            col = split.column()
            col.prop(tex, "texture_coords", text="") # 2.55
            # change to same type of blender mapping, for make stable

            if tex.texture_coords == 'ORCO': # 2.55
            #    """
                ob = context.object
                if ob and ob.type == 'MESH':
                    split = layout.split(percentage=0.3)
                    split.label(text="Mesh:")
                    split.prop(ob.data, "texco_mesh", text="")
            #    """
            elif tex.texture_coords == 'UV':

                split = layout.split(percentage=0.3)
                split.label(text="Layer:")
                ob = context.object
                if ob and ob.type == 'MESH':
                    split.prop_search(tex, "uv_layer", ob.data, "uv_textures", text="")
                else:
                    split.prop(tex, "uv_layer", text="")

            elif tex.texture_coords == 'OBJECT':
                split = layout.split(percentage=0.3)
                split.label(text="Object:")
                split.prop(tex, "object", text="")

        if isinstance(idblock, bpy.types.Brush): # recent change for beta 2.56
            if context.sculpt_object:
                layout.label(text="Brush Mapping:")
                layout.prop(tex, "map_mode", expand=True)

                row = layout.row()
                row.active = tex.map_mode in ('FIXED', 'TILED')
                row.prop(tex, "angle")
        else:
            if isinstance(idblock, bpy.types.Material):
                split = layout.split(percentage=0.3)
                split.label(text="Projection:")
                split.prop(tex, "mapping", text="")

                split = layout.split()

                col = split.column()
                if tex.texture_coords in ('ORCO', 'UV'):
                  col.prop(tex, "use_from_dupli")
                elif tex.texture_coords == 'OBJECT':
                  col.prop(tex, "use_from_original")
                elif wide_ui:
                    col.label()

                if wide_ui:
                    col = split.column()
                row = col.row()
                row.prop(tex, "mapping_x", text="")
                row.prop(tex, "mapping_y", text="")
                row.prop(tex, "mapping_z", text="")

        split = layout.split()

        col = split.column()
        col.prop(tex, "offset")

        if wide_ui:
            col = split.column()
        else:
            col.separator()

        col.prop(tex, "scale")


class YAF_TEXTURE_PT_influence(YAF_TextureSlotPanel, bpy.types.Panel):
    bl_label = "YafaRay Influence (Map To)"
    COMPAT_ENGINES = {'YAFA_RENDER'}

    @classmethod
    def poll(self, context):
        idblock = context_tex_datablock(context)
        if isinstance(idblock, bpy.types.Brush): # recent change
            return False

        if not getattr(context, "texture_slot", None):
            return False

        engine = context.scene.render.engine
        return (engine in self.COMPAT_ENGINES)

    def draw(self, context):

        layout = self.layout

        idblock = context_tex_datablock(context)

        #textype = context.texture
        tex = context.texture_slot
        wide_ui = context.region.width > narrowui

        def factor_but(layout, toggle, factor, name): # new in last rev. of Blender
            row = layout.row(align=True)
            row.prop(tex, toggle, text="")
            sub = row.row()
            sub.active = getattr(tex, toggle)
            sub.prop(tex, factor, text=name, slider=True)
            return sub # XXX, temp. use_map_normal needs to override.


        if isinstance(idblock, bpy.types.Material): # new type in last rev.
            if idblock.type in ('SURFACE', 'WIRE'): # TODO: lots of todo...
        #if type(idblock) == bpy.types.Material:
            #if idblock.type in ('SURFACE', 'HALO', 'WIRE'):
                split = layout.split()

                col = split.column()
                col.label(text="Diffuse:")
                factor_but(col, "use_map_diffuse", "diffuse_factor", "Intensity")
                factor_but(col, "use_map_color_diffuse", "diffuse_color_factor", "Color")
                #col.prop(tex,"use_map_color_diffuse", text = 'Color Diffuse')# if is need, add 'factor but' to use factor value
                #factor_but(col, "use_map_alpha", "alpha_factor", "Alpha")
                col.prop(tex,"use_map_alpha", text = 'Map Alpha')
                #factor_but(col, "use_map_translucency", "translucency_factor", "Translucency")
                col.prop(tex,"use_map_translucency", text = 'Map Translucency')

                col.separator()
                col.label(text="Specular:")
                #factor_but(col, "use_map_specular", "specular_factor", "Intensity")
                col.prop(tex,"use_map_specular", text = 'Map Specular')# use map color specular ?
                #factor_but(col, "use_map_color_spec", "specular_color_factor", "Color")
                #factor_but(col, "use_map_hardness", "hardness_factor", "Hardness")
                col.prop(tex,"specular_color_factor", text = 'Color', slider = True)
                col.prop(tex,"hardness_factor", text = 'Hardness', slider = True)

                #if wide_ui:
                #    col = split.column()
                col.separator()
                col.label(text="Shading:")
                #factor_but(col, "use_map_ambient", "ambient_factor", "Ambient")
                #factor_but(col, "use_map_emit", "emit_factor", "Emit")
                #factor_but(col, "use_map_mirror", "mirror_factor", "Mirror")
                col.prop(tex,"use_map_mirror", text = 'Mirror')
                #factor_but(col, "use_map_raymir", "raymir_factor", "Ray Mirror")
                col.prop(tex,"use_map_raymir", text = 'Ray Mirror')

                #col.separator()
                col.label(text="Geometry:")
                # XXX replace 'or' when displacement is fixed to not rely on normal influence value.
                sub_tmp = factor_but(col, "use_map_normal", "normal_factor", "Normal")
                sub_tmp.active = (tex.use_map_normal or tex.use_map_displacement)
                # END XXX

                col.separator()
                col.label(text="Others:")
                col.prop(tex, "blend_type", text="Blend")
                col.prop(tex, "use_rgb_to_intensity")
                sub = col.column()
                sub.active = tex.use_rgb_to_intensity
                sub.prop(tex, "color", text="")

                #if wide_ui:
                #    col = split.column()
                col.prop(tex, "invert", text="Negative")
                col.prop(tex, "use_stencil")

                #sub = col.column()
                #sub.active = tex.map_translucency or tex.map_emit or tex.map_alpha or tex.map_raymir or tex.map_hardness or tex.map_ambient or tex.map_specularity or tex.map_reflection or tex.map_mirror
                #sub.prop(tex, "default_value", text="Amount", slider=True)
            #elif idblock.type == 'VOLUME':
            #    split = layout.split()
            #
            #    col = split.column()
            #    factor_but(col, "use_map_density", "density_factor", "Density")
            #    factor_but(col, "use_map_emission", "emission_factor", "Emission")
            #    factor_but(col, "use_map_scatter", "scattering_factor", "Scattering")
            #    factor_but(col, "use_map_reflect", "reflection_factor", "Reflection")
            #
            #    col = split.column()
            #    col.label(text=" ")
            #    factor_but(col, "use_map_color_emission", "emission_color_factor", "Emission Color")
            #    factor_but(col, "use_map_color_transmission", "transmission_color_factor", "Transmission Color")
            #    factor_but(col, "use_map_color_reflection", "reflection_color_factor", "Reflection Color")
        #elif isinstance(idblock, bpy.types.Lamp): # not yet revised
        #    split = layout.split()
        #    col = split.column()
        #    factor_but(col, tex.map_color, "map_color", "color_factor", "Color")

        #    if wide_ui:
        #        col = split.column()
        #    factor_but(col, tex.map_shadow, "map_shadow", "shadow_factor", "Shadow")

        elif isinstance(idblock, bpy.types.World): # for setup world texture
            split = layout.split()

            col = split.column()
            factor_but(col, "use_map_blend", "blend_factor", "Blend")
            factor_but(col, "use_map_horizon", "horizon_factor", "Horizon")
            col = split.column()
            factor_but(col, "use_map_zenith_up", "zenith_up_factor", "Zenith Up")
            factor_but(col, "use_map_zenith_down", "zenith_down_factor", "Zenith Down")

        #layout.separator()

        #split = layout.split()

        #col = split.column()
        #col.prop(tex, "blend_type", text="Blend")
        #col.prop(tex, "use_rgb_to_intensity")
        # color is used on grayscale textures even when use_rgb_to_intensity is disabled.
        #col.prop(tex, "color", text="")


        if isinstance(idblock, bpy.types.Material) or isinstance(idblock, bpy.types.World):
            split = layout.split()
            col = split.column()
            col.prop(tex, "default_value", text="Default Value", slider=True)

# Texture Type Panels #

class YAF_TextureTypePanel(YAF_TextureButtonsPanel):
    bl_label = "Texture Type "
    COMPAT_ENGINES = {'YAFA_RENDER'}

    @classmethod
    def poll(self, context):
        tex = context.texture
        engine = context.scene.render.engine

        #next definition
        return tex and ((tex.type == self.tex_type and not tex.use_nodes) and (engine in self.COMPAT_ENGINES))

        #if var: # not work correct, remove
        #        if context.texture.type != self.tex_type:
        #                context.texture.type = self.tex_type
        #return var


class YAF_TEXTURE_PT_clouds(YAF_TextureTypePanel, bpy.types.Panel):
    bl_label = "Clouds"
    tex_type = 'CLOUDS'
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        wide_ui = context.region.width > narrowui
        layout.prop(tex, "cloud_type", text="Cloud", expand=True)

        layout.label(text="Noise:")
        layout.prop(tex, "noise_type", text="Type", expand=True)
        if wide_ui:
            layout.prop(tex, "noise_basis", text="Basis")
        else:
            layout.prop(tex, "noise_basis", text="")

        split = layout.split()

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")
        col.prop(tex, "noise_depth", text="Depth")



class YAF_TEXTURE_PT_wood(YAF_TextureTypePanel, bpy.types.Panel):
    bl_label = "Wood"
    tex_type = 'WOOD'
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        wide_ui = context.region.width > narrowui

        layout.prop(tex, "noisebasis_2", expand=True)
        if wide_ui:
            layout.prop(tex, "wood_type", expand=True)
        else:
            layout.prop(tex, "wood_type", text="")

        col = layout.column()
        col.active = tex.wood_type in ('RINGNOISE', 'BANDNOISE')
        col.label(text="Noise:")
        col.row().prop(tex, "noise_type", text="Type", expand=True)
        if wide_ui:
            layout.prop(tex, "noise_basis", text="Basis")
        else:
            layout.prop(tex, "noise_basis", text="")

        split = layout.split()
        split.active = tex.wood_type in ('RINGNOISE', 'BANDNOISE')

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")
        col.prop(tex, "turbulence")



class YAF_TEXTURE_PT_marble(YAF_TextureTypePanel, bpy.types.Panel):
    bl_label = "Marble"
    tex_type = 'MARBLE'
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        wide_ui = context.region.width > narrowui

        layout.prop(tex, "marble_type", expand=True)
        layout.prop(tex, "noisebasis_2", expand=True)
        layout.label(text="Noise:")
        layout.prop(tex, "noise_type", text="Type", expand=True)
        if wide_ui:
            layout.prop(tex, "noise_basis", text="Basis")
        else:
            layout.prop(tex, "noise_basis", text="")

        split = layout.split()

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")
        col.prop(tex, "noise_depth", text="Depth")

        if wide_ui:
            col = split.column()
        col.prop(tex, "turbulence", text="Turbulence")


class YAF_TEXTURE_PT_blend(YAF_TextureTypePanel, bpy.types.Panel):
    bl_label = "Blend"
    tex_type = 'BLEND'
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        wide_ui = context.region.width > narrowui

        if wide_ui:
            layout.prop(tex, "progression")
        else:
            layout.prop(tex, "progression", text="")
        #
        sub = layout.row()
        #
        sub.active = (tex.progression in ('LINEAR', 'QUADRATIC', 'EASING', 'RADIAL'))
        sub.prop(tex, "use_flip_axis", expand=True)



class YAF_TEXTURE_PT_image(YAF_TextureTypePanel, bpy.types.Panel):
    bl_label = "Map Image"
    tex_type = 'IMAGE'
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.template_image(tex, "image", tex.image_user)



def texture_filter_common(tex, layout):
    layout.label(text="Filter:")
    layout.prop(tex, "filter_type", text="")
    if tex.use_mipmap and tex.filter_type in ('AREA', 'EWA', 'FELINE'):
        if tex.filter_type == 'FELINE':
            layout.prop(tex, "filter_probes", text="Probes")
        else:
            layout.prop(tex, "filter_eccentricity", text="Eccentricity")

    layout.prop(tex, "filter_size")
    layout.prop(tex, "use_filter_size_min")


class YAF_TEXTURE_PT_image_sampling(YAF_TextureTypePanel, bpy.types.Panel):
    bl_label = "Image Sampling"
    bl_options = {'DEFAULT_CLOSED'}
    tex_type = 'IMAGE'
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        # slot = context.texture_slot
        wide_ui = context.region.width > narrowui

        split = layout.split()

        col = split.column()
        col.label(text="Alpha:")
        col.prop(tex, "use_alpha", text="Use")
        col.prop(tex, "use_calculate_alpha", text="Calculate")
        #col.prop(tex, "invert_alpha", text="Invert")
        #col.separator()
        col.prop(tex, "use_flip_axis", text="Flip X/Y Axis")

        if wide_ui:
            col = split.column()
        else:
            col.separator()

        col.prop(tex, "use_normal_map")
        row = col.row()
        row.active = tex.use_normal_map
        #row.prop(tex, "normal_map_space", text="")

        col.prop(tex, "use_mipmap")
        row = col.row()
        row.active = tex.use_mipmap
        row.prop(tex, "use_mipmap_gauss")
        col.prop(tex, "use_interpolation")

        texture_filter_common(tex, col)



class YAF_TEXTURE_PT_image_mapping(YAF_TextureTypePanel, bpy.types.Panel):
    bl_label = "Image Mapping"
    bl_options = {'DEFAULT_CLOSED'}
    tex_type = 'IMAGE'
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        wide_ui = context.region.width > narrowui

        if wide_ui:
            layout.prop(tex, "extension")
        else:
            layout.prop(tex, "extension", text="")

        split = layout.split()

        if tex.extension == 'REPEAT':
            col = split.column(align=True)
            col.label(text="Repeat:")
            col.prop(tex, "repeat_x", text="X")
            col.prop(tex, "repeat_y", text="Y")
            # """ # des-activate in 2.53
            #if wide_ui:
            #    col = split.column(align=True)
            #col.label(text="Mirror:")
            #col.prop(tex, "use_mirror_x", text="X")
            #col.prop(tex, "use_mirror_y", text="Y")
            layout.separator()
            # """ # end
        elif tex.extension == 'CHECKER':
            col = split.column(align=True)
            row = col.row()
            row.prop(tex, "use_checker_even", text="Even")
            row.prop(tex, "use_checker_odd", text="Odd")

            #if wide_ui:
            #    col = split.column()
            col.prop(tex, "checker_distance", text="Distance") # des-activate in 2.53

            layout.separator()

        split = layout.split()

        col = split.column(align=True)
        #col.prop(tex, "crop_rectangle")
        col.label(text="Crop Minimum:")
        col.prop(tex, "crop_min_x", text="X")
        col.prop(tex, "crop_min_y", text="Y")

        if wide_ui:
            col = split.column(align=True)
        col.label(text="Crop Maximum:")
        col.prop(tex, "crop_max_x", text="X")
        col.prop(tex, "crop_max_y", text="Y")


class YAF_TEXTURE_PT_musgrave(YAF_TextureTypePanel, bpy.types.Panel):
    bl_label = "Musgrave"
    tex_type = 'MUSGRAVE'
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        wide_ui = context.region.width > narrowui

        if wide_ui:
            layout.prop(tex, "musgrave_type")
        else:
            layout.prop(tex, "musgrave_type", text="")

        split = layout.split()

        col = split.column()
        col.prop(tex, "dimension_max", text="Dimension")
        col.prop(tex, "lacunarity", text="Lacunarity")
        col.prop(tex, "octaves", text="Octaves")

        if wide_ui:
            col = split.column()
        if (tex.musgrave_type in ('HETERO_TERRAIN', 'RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL')):
            col.prop(tex, "offset")
        if (tex.musgrave_type in ('RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL')):
            col.prop(tex, "gain")
            col.prop(tex, "noise_intensity", text="Intensity")

        layout.label(text="Noise:")

        if wide_ui:
            layout.prop(tex, "noise_basis", text="Basis")
        else:
            layout.prop(tex, "noise_basis", text="")

        split = layout.split()

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")

        #if wide_ui:
        #    col = split.column()
        #col.prop(tex, "nabla")


class YAF_TEXTURE_PT_voronoi(YAF_TextureTypePanel, bpy.types.Panel):
    bl_label = "Voronoi"
    tex_type = 'VORONOI'
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        wide_ui = context.region.width > narrowui

        split = layout.split()

        col = split.column()
        col.label(text="Distance Metric:")
        col.prop(tex, "distance_metric", text="")
        sub = col.column()
        sub.active = tex.distance_metric == 'MINKOVSKY'
        sub.prop(tex, "minkovsky_exponent", text="Exponent")
        col.label(text="Coloring:")
        col.prop(tex, "color_mode", text="")
        col.prop(tex, "noise_intensity", text="Intensity")

        if wide_ui:
            col = split.column()
        sub = col.column(align=True)
        sub.label(text="Feature Weights:")
        sub.prop(tex, "weight_1", text="1", slider=True)
        sub.prop(tex, "weight_2", text="2", slider=True)
        sub.prop(tex, "weight_3", text="3", slider=True)
        sub.prop(tex, "weight_4", text="4", slider=True)

        layout.label(text="Noise:")

        split = layout.split()

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")


class YAF_TEXTURE_PT_distortednoise(YAF_TextureTypePanel, bpy.types.Panel):
    bl_label = "Distorted Noise"
    tex_type = 'DISTORTED_NOISE'
    COMPAT_ENGINES = {'YAFA_RENDER'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        wide_ui = context.region.width > narrowui

        if wide_ui:
            layout.prop(tex, "noise_distortion")
            layout.prop(tex, "noise_basis", text="Basis")
        else:
            layout.prop(tex, "noise_distortion", text="")
            layout.prop(tex, "noise_basis", text="")

        split = layout.split()

        col = split.column()
        col.prop(tex, "distortion", text="Distortion")
        col.prop(tex, "noise_scale", text="Size")


#from properties_texture import TEXTURE_PT_preview

classes = [
    #TEXTURE_MT_specials,
    #TEXTURE_MT_envmap_specials,
    YAF_TEXTURE_PT_context_texture,
    YAF_TEXTURE_PT_preview,
    #TEXTURE_PT_preview,

    YAF_TEXTURE_PT_clouds, # Texture Type Panels
    YAF_TEXTURE_PT_wood,
    YAF_TEXTURE_PT_marble,
    #TEXTURE_PT_magic,
    YAF_TEXTURE_PT_blend,
    #YAF_TEXTURE_PT_stucci,
    YAF_TEXTURE_PT_image,
    YAF_TEXTURE_PT_image_sampling,
    YAF_TEXTURE_PT_image_mapping,
    #YAF_TEXTURE_PT_plugin,
    #YAF_TEXTURE_PT_envmap,
    #TEXTURE_PT_envmap_sampling,
    YAF_TEXTURE_PT_musgrave,
    YAF_TEXTURE_PT_voronoi,
    YAF_TEXTURE_PT_distortednoise,
    #TEXTURE_PT_voxeldata,
    #TEXTURE_PT_pointdensity,
    #TEXTURE_PT_pointdensity_turbulence,

    #YAF_TEXTURE_PT_colors, # activate in 2.53
    YAF_TEXTURE_PT_mapping,
    YAF_TEXTURE_PT_influence,

    ]


def register():
    #bpy.types.YAF_TextureButtonsPanel.prepend(TEXTURE_PT_preview.draw)
    register = bpy.types.register
    for cls in classes:
        register(cls)


def unregister():
    #bpy.types.YAF_TextureButtonsPanel.remove(TEXTURE_PT_preview.draw)
    unregister = bpy.types.unregister
    for cls in classes:
        unregister(cls)

if __name__ == "__main__":
    register()
