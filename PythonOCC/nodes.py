from NENV import *

from OCC.Core.gp import \
    gp_Pnt, \
    gp_Vec, \
    gp_Dir, \
    gp_Ax2, \
    gp_Pln, \
    gp_Trsf, \
    gp_Pnt

from OCC.Core.BRepBuilderAPI import \
    BRepBuilderAPI_Transform

from OCC.Core.BRepPrimAPI import \
    BRepPrimAPI_MakeBox, \
    BRepPrimAPI_MakeSphere, \
    BRepPrimAPI_MakeCylinder

from OCC.Core.BRepAlgoAPI import \
    BRepAlgoAPI_Fuse, \
    BRepAlgoAPI_Common, \
    BRepAlgoAPI_Cut

from OCC.Core.STEPControl import \
    STEPControl_Writer, \
    STEPControl_AsIs

from OCC.Extend.DataExchange import \
    write_stl_file

from OCC.Core.BRepFilletAPI import \
    BRepFilletAPI_MakeFillet

from OCC.Extend.TopologyUtils import \
    TopologyExplorer


from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()


class PythonOCCNodeBase(Node):

    def get_inputs(self):
        return (self.input(i) for i in range(len(self.inputs)))


class PythonOCCNodeBase_DynamicInputs(PythonOCCNodeBase):

    def __init__(self, params):
        super().__init__(params)

        self.num_inputs = 0
        self.actions['add input'] = {'method': self.add_operand_input}

    def place_event(self):
        for i in range(len(self.inputs)):
            self.register_new_operand_input(i)

    def add_operand_input(self):
        self.create_input_dt(dtype=dtypes.Data(size='s'))
        self.register_new_operand_input(self.num_inputs)
        self.update()

    def remove_operand_input(self, index):
        self.delete_input(index)
        self.num_inputs -= 1
        del self.actions[f'remove input {self.num_inputs}']
        self.update()

    def register_new_operand_input(self, index):
        self.actions[f'remove input {index}'] = {
            'method': self.remove_operand_input,
            'data': index
        }
        self.num_inputs += 1

    def update_event(self, inp=-1):
        self.set_output_val(0, self.apply_op([self.input(i) for i in range(len(self.inputs))]))

    def apply_op(self, elements: list):
        return None

# -------------------------------------------

# GP ----------------------------------------

class GpNodeBase(PythonOCCNodeBase):
    color = '#5e0a91'

class Pnt_Node(GpNodeBase):
    """
    Generates Point_______-
    o_X___________________-
    o_Y___________________-
    o_Z___________________-
    """

    title = 'point'

    init_inputs = [
        NodeInputBP('x', dtype=dtypes.Data(size='s')),
        NodeInputBP('y', dtype=dtypes.Data(size='s')),
        NodeInputBP('z', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        x, y, z = self.clean(self.get_inputs())
        self.set_output_val(0, gp_Pnt(x, y, z))

    def clean(self, coords):
        cleaned = []
        for c in coords:
            if c is None:
                cleaned.append(0)
            else:
                cleaned.append(c)
        return tuple(cleaned)


class Vec_Node(GpNodeBase):
    """
    Generates Vector______-
    o_X___________________-
    o_Y___________________-
    o_Z___________________-
    """

    title = 'Vector'

    init_inputs = [
        NodeInputBP('x', dtype=dtypes.Data(size='s')),
        NodeInputBP('y', dtype=dtypes.Data(size='s')),
        NodeInputBP('z', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        x, y, z = self.get_inputs()
        self.set_output_val(0, gp_Vec(x, y, z))


class Dir_Node(GpNodeBase):
    """
    Generates Dir_______-
    o_X___________________-
    o_Y___________________-
    o_Z___________________-
    """

    title = 'dir'

    init_inputs = [
        NodeInputBP('x', dtype=dtypes.Data(size='s')),
        NodeInputBP('y', dtype=dtypes.Data(size='s')),
        NodeInputBP('z', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        x, y, z = self.get_inputs()
        self.set_output_val(0, gp_Dir(x, y, z))


class Ax2_Node(GpNodeBase):
    """
    Generates Ax2_________-
    o_Point_______________-
    o_Dir_________________-
    """

    title = 'Ax2'

    init_inputs = [
        NodeInputBP('point', dtype=dtypes.Data(size='s')),
        NodeInputBP('dir', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        point, dir_ = self.get_inputs()
        self.set_output_val(0, gp_Ax2(point, dir_))


class Pln_Node(GpNodeBase):
    """
    Generates Plane_______-
    o_Point_______________-
    o_Dir_________________-
    """

    title = 'Plane'

    init_inputs = [
        NodeInputBP('point', dtype=dtypes.Data(size='s')),
        NodeInputBP('dir', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        point, dir_ = self.get_inputs()
        self.set_output_val(0, gp_Pln(point, dir_))


class Trsf_Node(GpNodeBase):
    """
    Generates transform___-
    o_[Shapes]____________-
    o_[Vectors]___________-
    """

    title = 'Transform'

    init_inputs = [
        NodeInputBP('shapes', dtype=dtypes.Data(size='s')),
        NodeInputBP('vectors', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        shapes, vectors = self.get_inputs()
        result = []
        if shapes is list:
            for sh, v in zip(shapes, vectors):
                trns = gp_Trsf()
                trns.SetTranslation(v)
                translated = BRepBuilderAPI_Transform(sh, trns).Shape()
                result.append(translated)
            self.set_output_val(0, result)
        else:
            trns = gp_Trsf()
            trns.SetTranslation(vectors)
            translated = BRepBuilderAPI_Transform(shapes, trns).Shape()
            self.set_output_val(0, translated)


Gp_nodes = [
    Pnt_Node,
    Dir_Node,
    Vec_Node,
    Ax2_Node,
    Pln_Node,
    Trsf_Node,
]

# -------------------------------------------


# BREPPRIMAPI --------------------------------

class BrepPrimAPINodeBase(PythonOCCNodeBase):
    color = '#aabb44'

class Box_Node(BrepPrimAPINodeBase):
    """
    Generates box_________-
    o_Width_______________-
    o_Length______________-
    o_Height______________-
    """

    title = 'box'

    init_inputs = [
        NodeInputBP('w', dtype=dtypes.Data(size='s')),
        NodeInputBP('l', dtype=dtypes.Data(size='s')),
        NodeInputBP('h', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        width, length, height = self.get_inputs()
        box = BRepPrimAPI_MakeBox(gp_Pnt(), width, length, height).Shape()
        self.set_output_val(0, box)


class Sphere_Node(BrepPrimAPINodeBase):
    """
    Generates sphere_________-
    o_Center point/ax2_______-
    o_Radius_________________-
    """

    title = 'sphere'

    init_inputs = [
        NodeInputBP('point', dtype=dtypes.Data(size='s')),
        NodeInputBP('r', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        point, radius = self.get_inputs()
        sphere = BRepPrimAPI_MakeSphere(point, radius).Shape()
        self.set_output_val(0, sphere)


class Cylinder_Node(BrepPrimAPINodeBase):
    """
    Generates cylinder_______-
    o_Axe____________________-
    o_Radius_________________-
    o_Length_________________-
    """

    title = 'cylinder'

    init_inputs = [
        NodeInputBP('axe', dtype=dtypes.Data(size='s')),
        NodeInputBP('r', dtype=dtypes.Data(size='s')),
        NodeInputBP('len', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        axe, radius, length = self.get_inputs()
        cylinder = BRepPrimAPI_MakeCylinder(axe, radius, length).Shape()
        self.set_output_val(0, cylinder)


BRepPrimAPI_nodes = [
    Box_Node,
    Sphere_Node,
    Cylinder_Node,
]
# -------------------------------------------


# BREPALGOAPI --------------------------------

class BrepAlgoAPINodeBase(PythonOCCNodeBase):
    color = '#ab0c36'

class Fuse_Node(BrepAlgoAPINodeBase):
    """
    Generates fusion_________-
    o_Part 1_________________-
    o_Part 2_________________-
    """

    title = 'fuse'

    init_inputs = [
        NodeInputBP('a', dtype=dtypes.Data(size='s')),
        NodeInputBP('b', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        a, b = self.get_inputs()
        fuse_shp = BRepAlgoAPI_Fuse(a, b).Shape()
        self.set_output_val(0, fuse_shp)


class Common_Node(BrepAlgoAPINodeBase):
    """
    Generates common_________-
    o_Part 1_________________-
    o_Part 2_________________-
    """

    title = 'common'

    init_inputs = [
        NodeInputBP('a', dtype=dtypes.Data(size='s')),
        NodeInputBP('b', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        a, b = self.get_inputs()
        common_shp = BRepAlgoAPI_Common(a, b).Shape()
        self.set_output_val(0, common_shp)


class Cut_Node(BrepAlgoAPINodeBase):
    """
    Generates cutting________-
    o_Basis__________________-
    o_Cutter_________________-
    """

    title = 'cut'

    init_inputs = [
        NodeInputBP('a', dtype=dtypes.Data(size='s')),
        NodeInputBP('b', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        a, b = self.get_inputs()
        cut_shp = BRepAlgoAPI_Cut(a, b).Shape()
        self.set_output_val(0, cut_shp)


BRepAlgoAPI_nodes = [
    Fuse_Node,
    Common_Node,
    Cut_Node,
]

# -------------------------------------------


# BREPFILLETAPI --------------------------------

class BrepFilletAPINodeBase(PythonOCCNodeBase):
    color = '#e0149c'

class Fillet_Node(BrepFilletAPINodeBase):
    """
    Generates fillet_________-
    o_Part___________________-
    o_Radius_________________-
    """

    title = 'fillet'

    init_inputs = [
        NodeInputBP('fused', dtype=dtypes.Data(size='s')),
        NodeInputBP('r', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        fused_shape, radius = self.get_inputs()
        fill = BRepFilletAPI_MakeFillet(fused_shape)

        for e in TopologyExplorer(fused_shape).edges():
            fill.Add(e)

        for i in range(1, fill.NbContours() + 1):
            length = fill.Length(i)
            fill.SetRadius(radius, i, 1)

        blended_fused_solids = fill.Shape()

        self.set_output_val(0, blended_fused_solids)


BRepFilletAPI_nodes = [
    Fillet_Node,
]
# -------------------------------------------


# DISPLAY --------------------------------

class DisplayNodeBase(PythonOCCNodeBase):
    color = '#3355dd'

class Display_Node(DisplayNodeBase):
    """display shapes"""

    title = 'display'

    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    def update_event(self, inp=-1):
        display.EraseAll()
        for v in self.get_inputs():
            if v == None :
                pass
            elif v is list :
                for el in v :
                    display.DisplayShape(el)
            else :
                display.DisplayShape(v)

        display.FitAll()


Display_nodes = [
    Display_Node,
]

# -------------------------------------------


# TOOLS----- --------------------------------
# class ToolsNodeBase(PythonOCCNodeBase):
#     color = '#000000'

class List_Node(PythonOCCNodeBase_DynamicInputs):
    """
    Generates List_______-
    o_A__________________-
    o_B__________________-
    """

    title = 'List'
    color = '#000000'

    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def apply_op(self, elements: list):
        return elements


class ExportStep_Node(PythonOCCNodeBase):
    """
    Generates Step_______-
    o_Shape______________-
    o_Name_______________-
    """

    title = 'ExportStep'
    color = '#000000'

    init_inputs = [
        NodeInputBP('shape', dtype=dtypes.Data(size='s')),
        NodeInputBP('fname', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        shape, filename = self.get_inputs()
        step_writer = STEPControl_Writer()
        step_writer.Transfer(shape, STEPControl_AsIs)
        status = step_writer.Write(str(filename))


class ExportStl_Node(PythonOCCNodeBase):
    """
    Generates Stl________-
    o_Shape______________-
    o_Name_______________-
    """

    title = 'ExportStl'
    color = '#000000'

    init_inputs = [
        NodeInputBP('shape', dtype=dtypes.Data(size='s')),
        NodeInputBP('fname', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        shape, filename = self.get_inputs()
        status = write_stl_file(shape, filename, mode="ascii", linear_deflection=0.9, angular_deflection=0.5)


Tools_nodes = [
    List_Node,
    ExportStep_Node,
    ExportStl_Node,
]

# -------------------------------------------


export_nodes(
    *Gp_nodes,
    *BRepPrimAPI_nodes,
    *BRepAlgoAPI_nodes,
    *BRepFilletAPI_nodes,
    *Display_nodes,
    *Tools_nodes,
)