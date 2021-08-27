from NENV import *

from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_functionto_menu = init_display()


class PythonOCCNodeBase(Node):


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
        # del self.actions[f'remove input {index}']
        self.rebuild_remove_actions()
        self.update()

    def register_new_operand_input(self, index):
        self.actions[f'remove input {index}'] = {
            'method': self.remove_operand_input,
            'data': index
        }
        self.num_inputs += 1

    def rebuild_remove_actions(self):

        remove_keys = []
        for k, v in self.actions.items():
            if k.startswith('remove input'):
                remove_keys.append(k)

        for k in remove_keys:
            del self.actions[k]

        for i in range(self.num_inputs):
            self.actions[f'remove input {i}'] = {'method': self.remove_operand_input, 'data': i}

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
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'point'


    def apply_op(self, elements: list):
        x = elements[0]
        y = elements[1]
        z = elements[2]
        if type(x) is None:
            x = 0
        if type(y) is None:
            y = 0
        if type(z) is None:
            z = 1
        from OCC.Core.gp import gp_Pnt
        point = gp_Pnt(x,y,z)
        return point

class Vec_Node(GpNodeBase):
    """
    Generates Vector______-
    o_X___________________-
    o_Y___________________-
    o_Z___________________-
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'Vector'


    def apply_op(self, elements: list):
        x = elements[0]
        y = elements[1]
        z = elements[2]
        from OCC.Core.gp import gp_Vec
        vec = gp_Vec(x,y,z)
        return vec

class Dir_Node(GpNodeBase):
    """
    Generates Dir_______-
    o_X___________________-
    o_Y___________________-
    o_Z___________________-
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'dir'


    def apply_op(self, elements: list):
        x = elements[0]
        y = elements[1]
        z = elements[2]
        from OCC.Core.gp import gp_Dir
        dir = gp_Dir(x,y,z)
        return dir

class Ax2_Node(GpNodeBase):
    """
    Generates Ax2_________-
    o_Point_______________-
    o_Dir_________________-
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'Ax2'


    def apply_op(self, elements: list):
        point = elements[0]
        dir = elements[1]
        from OCC.Core.gp import gp_Ax2
        dir = gp_Ax2(point, dir)
        return dir

class Pln_Node(GpNodeBase):
    """
    Generates Plane_______-
    o_Point_______________-
    o_Dir_________________-
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'Plane'


    def apply_op(self, elements: list):
        point = elements[0]
        dir = elements[1]
        from OCC.Core.gp import gp_Pln
        plane = gp_Pln(point, dir)
        return plane


class Trsf_Node(GpNodeBase):
    """
    Generates transform___-
    o_[Shapes]____________-
    o_[Vectors]___________-
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'Transform'


    def apply_op(self, elements: list):
        shapes = elements[0]
        vectors = elements[1]
        from OCC.Core.gp import gp_Trsf
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
        result = []
        if shapes is list :
            for sh, v in zip(shapes, vectors):
                trns = gp_Trsf()
                trns.SetTranslation(v)
                translated = BRepBuilderAPI_Transform(sh, trns).Shape()
                result.append(translated)
            return result
        else :
            trns = gp_Trsf()
            trns.SetTranslation(vectors)
            translated = BRepBuilderAPI_Transform(shapes, trns).Shape()
        return translated

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
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'box'


    def apply_op(self, elements: list):
        width = elements[0]
        length = elements[1]
        height = elements[2]
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
        from OCC.Core.gp import gp_Pnt
        box = BRepPrimAPI_MakeBox(gp_Pnt(), width, length, height).Shape()

        return box



class Sphere_Node(BrepPrimAPINodeBase):
    """
    Generates sphere_________-
    o_Center point/ax2_______-
    o_Radius_________________-
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'sphere'


    def apply_op(self, elements: list):
        point = elements[0]
        radius = elements[1]
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
        sphere = BRepPrimAPI_MakeSphere(point, radius).Shape()
        return sphere

class Cylinder_Node(BrepPrimAPINodeBase):
    """
    Generates cylinder_______-
    o_Axe____________________-
    o_Radius_________________-
    o_Length_________________-
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'cylinder'


    def apply_op(self, elements: list):
        axe = elements[0]
        radius = elements[1]
        length = elements[2]
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        cylinder = BRepPrimAPI_MakeCylinder(axe, radius,length).Shape()
        return cylinder

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
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def apply_op(self, elements: list):
        from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
        a = elements[0]
        b = elements[1]
        fuse_shp = BRepAlgoAPI_Fuse(a, b).Shape()


        return fuse_shp

class Common_Node(BrepAlgoAPINodeBase):
    """
    Generates common_________-
    o_Part 1_________________-
    o_Part 2_________________-
    """

    title = 'common'

    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def apply_op(self, elements: list):
        from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Common
        a = elements[0]
        b = elements[1]
        common_shp = BRepAlgoAPI_Common(a, b).Shape()


        return common_shp

class Cut_Node(BrepAlgoAPINodeBase):
    """
    Generates cutting________-
    o_Basis__________________-
    o_Cutter_________________-
    """

    title = 'cut'

    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def apply_op(self, elements: list):
        from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
        a = elements[0]
        b = elements[1]
        cut_shp = BRepAlgoAPI_Cut(a, b).Shape()


        return cut_shp


BRepAlgoAPI_nodes = [
    Fuse_Node,
    Common_Node,
    Cut_Node,
]

# -------------------------------------------


# BREPFILLETAPI --------------------------------

class BrepFilletAPINodeBase(PythonOCCNodeBase):
    color = '#e0149c'

class fillet_Node(BrepFilletAPINodeBase):
    """
    Generates fillet_________-
    o_Part___________________-
    o_Radius_________________-
    """

    title = 'fillet'

    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def apply_op(self, elements: list):
        from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
        from OCC.Extend.TopologyUtils import TopologyExplorer
        fused_shape = elements[0]
        radius = elements[1]
        fill = BRepFilletAPI_MakeFillet(fused_shape)
        for e in TopologyExplorer(fused_shape).edges():
            fill.Add(e)

        for i in range(1, fill.NbContours() + 1):
            length = fill.Length(i)
            fill.SetRadius(radius, i, 1)

        blended_fused_solids = fill.Shape()


        return blended_fused_solids

BRepFilletAPI_nodes = [
    fillet_Node,
]
# -------------------------------------------


# DISPLAY --------------------------------

class DisplayNodeBase(PythonOCCNodeBase):
    color = '#3355dd'

class display_Node(DisplayNodeBase):
    """display shapes"""

    title = 'display'

    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]


    def apply_op(self, elements: list):
        display.EraseAll()
        for e in elements:
            if e == None :
                pass
            elif e is list :
                for el in e :
                    display.DisplayShape(el)
            else :
                display.DisplayShape(e)

        display.FitAll()
        start_display()




Display_nodes = [
    display_Node,
]

# -------------------------------------------


# TOOLS----- --------------------------------
class ToolsNodeBase(PythonOCCNodeBase):
    color = '#000000'

class List_Node(ToolsNodeBase):
    """
    Generates List_______-
    o_A__________________-
    o_B__________________-
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'List'


    def apply_op(self, elements: list):
        list = []
        for e in elements:
            list.append(e)
        return list

class ExportStep_Node(ToolsNodeBase):
    """
    Generates Step_______-
    o_Shape______________-
    o_Name_______________-
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'ExportStep'


    def apply_op(self, elements: list):
        shape = elements[0]
        filename = elements[1]
        from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
        step_writer = STEPControl_Writer()
        step_writer.Transfer(shape, STEPControl_AsIs)
        status = step_writer.Write(str(filename))
        return None

class ExportStl_Node(ToolsNodeBase):
    """
    Generates Stl________-
    o_Shape______________-
    o_Name_______________-
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    title = 'ExportStl'


    def apply_op(self, elements: list):
        shape = elements[0]
        filename = elements[1]
        from OCC.Extend.DataExchange import write_stl_file
        status = write_stl_file(shape, filename, mode="ascii", linear_deflection=0.9, angular_deflection=0.5)
        return None

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