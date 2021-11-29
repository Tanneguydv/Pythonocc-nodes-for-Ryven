from NENV import *

widgets = import_widgets(__file__)

from OCC.Core.ChFi2d import \
    ChFi2d_AnaFilletAlgo

from OCC.Core.gp import \
    gp_Pnt, \
    gp_Vec, \
    gp_Dir, \
    gp_Ax2, \
    gp_Pln, \
    gp_Trsf, \
    gp_DX, \
    gp_DY, \
    gp_DZ, \
    gp_Circ, \
    gp_XOY, \
    gp_YOZ, \
    gp_ZOX

from OCC.Core.BRep import \
    BRep_Tool

from OCC.Core.BRepBuilderAPI import \
    BRepBuilderAPI_Transform, \
    BRepBuilderAPI_MakeEdge, \
    BRepBuilderAPI_MakeWire, \
    BRepBuilderAPI_MakeFace

from OCC.Core.BRepPrimAPI import \
    BRepPrimAPI_MakeBox, \
    BRepPrimAPI_MakeSphere, \
    BRepPrimAPI_MakeCylinder, \
    BRepPrimAPI_MakeTorus

from OCC.Core.BRepAdaptor import \
    BRepAdaptor_CompCurve

from OCC.Core.BRepAlgoAPI import \
    BRepAlgoAPI_Fuse, \
    BRepAlgoAPI_Common, \
    BRepAlgoAPI_Cut, \
    BRepAlgoAPI_Section

from OCC.Core.BRepOffsetAPI import \
    BRepOffsetAPI_MakePipe

from OCC.Core.Geom import \
    Geom_Circle

from OCC.Core.GeomAbs import \
    GeomAbs_C2

from OCC.Core.GCPnts import \
    GCPnts_UniformAbscissa

from OCC.Core.GeomAPI import \
    GeomAPI_PointsToBSplineSurface

from OCC.Core.STEPControl import \
    STEPControl_Writer, \
    STEPControl_AsIs

from OCC.Core.TColgp import \
    TColgp_Array1OfPnt, \
    TColgp_Array2OfPnt

from OCC.Core.TopAbs import \
    TopAbs_EDGE, \
    TopAbs_FACE, \
    TopAbs_SHELL, \
    TopAbs_VERTEX, \
    TopAbs_WIRE, \
    TopAbs_SOLID, \
    TopAbs_COMPOUND, \
    TopAbs_COMPSOLID

from OCC.Core.TopExp import \
    TopExp_Explorer

from OCC.Core.TopoDS import \
    topods_Edge, \
    TopoDS_Edge, \
    topods_Face, \
    topods_Shell, \
    topods_Vertex, \
    topods_Wire, \
    TopoDS_Wire, \
    topods_Solid, \
    topods_Compound, \
    topods_CompSolid

from OCC.Extend.DataExchange import \
    write_stl_file, \
    read_stl_file, \
    read_step_file

from OCC.Core.BRepFilletAPI import \
    BRepFilletAPI_MakeFillet

from OCC.Extend.TopologyUtils import \
    TopologyExplorer

from OCCUtils.Common import \
    filter_points_by_distance, \
    curve_length

# 3D Viewer ------------------------------------------

from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()
add_menu('View')

def Fit_All():
    display.FitAll()

def Iso_View():
    display.View_Iso()
    display.FitAll()

def Top_View():
    display.View_Top()
    display.FitAll()

def Left_View():
    display.View_Left()
    display.FitAll()

def Front_View():
    display.View_Front()
    display.FitAll()

def Right_View():
    display.View_Right()
    display.FitAll()

def Bottom_View():
    display.View_Bottom()
    display.FitAll()

def Rear_View():
    display.View_Rear()
    display.FitAll()


add_function_to_menu('View', Fit_All)
add_function_to_menu('View', Iso_View)
add_function_to_menu('View', Top_View)
add_function_to_menu('View', Left_View)
add_function_to_menu('View', Front_View)
add_function_to_menu('View', Right_View)
add_function_to_menu('View', Bottom_View)
add_function_to_menu('View', Rear_View)

# -----------------------------------------------------


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

class PointZero_Node(GpNodeBase):
    """
    Generates Point Zero__-
    """

    title = 'Point0'

    init_outputs = [
        NodeOutputBP(),
    ]

    def place_event(self):
        point = gp_Pnt(0,0,0)
        self.set_output_val(0, point)

class DeconstructPnt_Node(GpNodeBase):
    """
    Deconstruct Point_____-
    o_Point_______________-
    """

    title = 'deconstruct point'

    init_inputs = [
        NodeInputBP('point', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP('X'),
        NodeOutputBP('Y'),
        NodeOutputBP('Z'),
    ]

    def update_event(self, inp=-1):
        for point in self.get_inputs():
            self.set_output_val(0,point.X())
            self.set_output_val(1, point.Y())
            self.set_output_val(2, point.Z())

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

class DX_Node(GpNodeBase):
    """
    Generates Dir X____-
    """

    title = 'DirX'

    init_outputs = [
        NodeOutputBP(),
    ]

    def place_event(self):
        dx = gp_DX()
        self.set_output_val(0, dx)

class DY_Node(GpNodeBase):
    """
    Generates Dir Y____-
    """

    title = 'DirY'

    init_outputs = [
        NodeOutputBP(),
    ]

    def place_event(self):
        dy = gp_DY()
        self.set_output_val(0, dy)

class DZ_Node(GpNodeBase):
    """
    Generates Dir Z____-
    """

    title = 'DirZ'

    init_outputs = [
        NodeOutputBP(),
    ]

    def place_event(self):
        dz = gp_DZ()
        self.set_output_val(0, dz)


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

class XOY_Node(GpNodeBase):
    """
    Generates Ax Z____-
    """

    title = 'AxZ'

    init_outputs = [
        NodeOutputBP(),
    ]

    def place_event(self):
        axz = gp_XOY()
        self.set_output_val(0, axz)

class YOZ_Node(GpNodeBase):
    """
    Generates Ax X____-
    """

    title = 'AxX'

    init_outputs = [
        NodeOutputBP(),
    ]

    def place_event(self):
        axx = gp_YOZ()
        self.set_output_val(0, axx)

class ZOX_Node(GpNodeBase):
    """
    Generates Ax Y____-
    """

    title = 'AxY'

    init_outputs = [
        NodeOutputBP(),
    ]

    def place_event(self):
        axy = gp_ZOX()
        self.set_output_val(0, axy)

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
        if type(shapes) is list and type(vectors) is list:
            for sh, v in zip(shapes, vectors):
                trns = gp_Trsf()
                trns.SetTranslation(v)
                if isinstance(sh, gp_Pnt):
                    sh2 = sh
                    sh2.Transform(trns)
                    translated = sh2
                else:
                    translated = BRepBuilderAPI_Transform(sh, trns).Shape()
                result.append(translated)
            self.set_output_val(0, result)
        elif type(shapes) is list and type(vectors) is not list:
            for sh in (shapes):
                trns = gp_Trsf()
                trns.SetTranslation(vectors)
                if isinstance(sh, gp_Pnt):
                    sh2 = sh
                    sh2.Transform(trns)
                    translated = sh2
                else:
                    translated = BRepBuilderAPI_Transform(sh, trns).Shape()
                result.append(translated)
            self.set_output_val(0, result)
        elif type(shapes) is not list and type(vectors) is list:
            for v in (vectors):
                trns = gp_Trsf()
                trns.SetTranslation(v)
                if isinstance(shapes, gp_Pnt):
                    sh2 = shapes
                    sh2.Transform(trns)
                    translated = sh2
                else:
                    translated = BRepBuilderAPI_Transform(shapes, trns).Shape()
                result.append(translated)
            self.set_output_val(0, result)
        else:
            trns = gp_Trsf()
            trns.SetTranslation(vectors)
            if isinstance(shapes, gp_Pnt):
                sh2 = shapes
                sh2.Transform(trns)
                translated = sh2
            else:
                translated = BRepBuilderAPI_Transform(shapes, trns).Shape()
            self.set_output_val(0, translated)

class Move2pts_Node(GpNodeBase):
    """
    Move 2 points_________-
    o_from pnt____________-
    o_to pnt______________-
    """

    title = 'Move2pnts'

    init_inputs = [
        NodeInputBP('shapes', dtype=dtypes.Data(size='s')),
        NodeInputBP('from', dtype=dtypes.Data(size='s')),
        NodeInputBP('to', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        shapes, from_pnt, to_pnt = self.get_inputs()
        vectors = []
        result = []
        if type(from_pnt) is list:
            for f, t in zip(from_pnt, to_pnt):
                v = gp_Vec()
                x = t.X() - f.X()
                y = t.Y() - f.Y()
                z = t.Z() - f.Z()
                v.SetCoord(x, y, z)
                vectors.append(v)
            for sh, v, in zip(shapes, vectors):
                trns = gp_Trsf()
                trns.SetTranslation(v.Reversed())
                translated = BRepBuilderAPI_Transform(sh, trns).Shape()
                result.append(translated)
            self.set_output_val(0, result)
        else:
            v = gp_Vec()
            x = to_pnt.X() - from_pnt.X()
            y = to_pnt.Y() - from_pnt.Y()
            z = to_pnt.Z() - from_pnt.Z()
            v.SetCoord(x, y, z)
            trns = gp_Trsf()
            trns.SetTranslation(v.Reversed())
            translated = BRepBuilderAPI_Transform(shapes, trns).Shape()
            self.set_output_val(0, translated)

class MidPoint_Node(GpNodeBase):
    """
    MidPoint_____________-
    o_Point A____________-
    o_Point B______________-
    """

    title = 'MidPoint'

    init_inputs = [
        NodeInputBP('pointA', dtype=dtypes.Data(size='s')),
        NodeInputBP('pointB', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        pointA, pointB = self.get_inputs()
        vec1 = gp_Vec(pointA.XYZ())
        vec2 = gp_Vec(pointB.XYZ())
        midvec = (vec1 + vec2) / 2.
        midpoint = gp_Pnt(midvec.XYZ())
        self.set_output_val(0, midpoint)


Gp_nodes = [
    Pnt_Node,
    DeconstructPnt_Node,
    PointZero_Node,
    Dir_Node,
    Vec_Node,
    DX_Node,
    DY_Node,
    DZ_Node,
    Ax2_Node,
    XOY_Node,
    YOZ_Node,
    ZOX_Node,
    Pln_Node,
    Trsf_Node,
    Move2pts_Node,
    MidPoint_Node,
]

# -------------------------------------------

# BREPBUILDERAPI-----------------------------

class BrepBuilderAPINodeBase(PythonOCCNodeBase):
    color = '#DAA520'

class TwoPtsEdge_Node(BrepBuilderAPINodeBase):
    """
    Generates 2 pts Edge__-
    o_Point_______________-
    o_Point_______________-
    """

    title = '2ptsEdge'

    init_inputs = [
        NodeInputBP('pnt1', dtype=dtypes.Data(size='s')),
        NodeInputBP('Pnt2', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        pnt1, pnt2 = self.get_inputs()
        if type(pnt1) is list:
            edges = []
            for p1, p2 in zip(pnt1, pnt2):
                edge = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
                edges.append(edge)
            self.set_output_val(0, edges)
        else:
            edge = BRepBuilderAPI_MakeEdge(pnt1, pnt2).Edge()
            self.set_output_val(0, edge)

class Wire_Node(BrepBuilderAPINodeBase):
    """
    Generates Wire________-
    o_List of Points______-
    """

    title = 'Wire'

    init_inputs = [
        NodeInputBP('pntslist', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        for pointlist in self.get_inputs():
            pointsarray = TColgp_Array1OfPnt(1, len(pointlist))
            for n, i in enumerate(pointlist):
                pointsarray.SetValue(n + 1, i)
            wirebuild = BRepBuilderAPI_MakeWire()
            for i in range(1, len(pointlist)):
                edgepoint = BRepBuilderAPI_MakeEdge(pointsarray.Value(i), pointsarray.Value(i + 1)).Edge()
                wirebuild.Add(edgepoint)
        self.set_output_val(0, wirebuild.Shape())

class WireFillet2d_Node(BrepBuilderAPINodeBase):
    """
    Generates 2dWireFillet_-
    o_List of Points______-
    o_Fillet Radius_______-
    """

    title = '2dWireFillet'

    init_inputs = [
        NodeInputBP('pntslist', dtype=dtypes.Data(size='s')),
        NodeInputBP('radius', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        pointlist, radius = self.get_inputs()
        if radius == 0:
            radius = 0.01
        pointsarray = TColgp_Array1OfPnt(1, len(pointlist))
        for n, i in enumerate(pointlist):
            pointsarray.SetValue(n + 1, i)
        edges = {}
        ijk = 0
        for i in range(1, len(pointlist)):
            edges[ijk] = BRepBuilderAPI_MakeEdge(pointsarray.Value(i), pointsarray.Value(i + 1)).Edge()
            ijk += 1
        edges_list = list(edges.values())
        wirebuild = BRepBuilderAPI_MakeWire()
        for index, edge in enumerate(edges_list[:-1]):
            f = ChFi2d_AnaFilletAlgo()
            f.Init(edges_list[index], edges_list[index+ 1], gp_Pln())
            f.Perform(radius)
            fillet = f.Result(edges_list[index], edges_list[index + 1])
            wirebuild.Add(edge)
            wirebuild.Add(fillet)

        wirebuild.Add(edges_list[-1])
        self.set_output_val(0, wirebuild.Shape())

class DiscretizeWire_Node(BrepBuilderAPINodeBase):
    """
    Discretize Wire_______-
    o_Wire________________-
    o_Nb of points________-
    """

    title = 'DiscretizeWire'

    init_inputs = [
        NodeInputBP('Wire', dtype=dtypes.Data(size='s')),
        NodeInputBP('Nb', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        wire, nbpts = self.get_inputs()
        pnts = []  # points to create bsplines
        if isinstance(wire, TopoDS_Edge):
            wire = BRepBuilderAPI_MakeWire(wire).Wire()
        curve_adapt = BRepAdaptor_CompCurve(wire)
        # print(curve_adapt)
        _lbound, _ubound = curve_adapt.FirstParameter(), curve_adapt.LastParameter()
        npts = GCPnts_UniformAbscissa(curve_adapt, nbpts, _lbound, _ubound)
        if npts.IsDone():
            for i in range(1, npts.NbPoints() + 1):
                pnts.append(curve_adapt.Value(npts.Parameter(i)))
        self.set_output_val(0, pnts)
        # print(tmp)

class CurveLength_Node(BrepBuilderAPINodeBase):
    """
    Curve Length__________-
    o_Wire/Edge(L)________-
    """

    title = 'CurveLength'

    init_inputs = [
        NodeInputBP('Wire/Edge', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        lengths = []
        for curve in self.get_inputs():
            lengths.append(curve_length(curve))
        self.set_output_val(0, lengths)
        # print(tmp)


BRepBuilderAPI_nodes = [
    TwoPtsEdge_Node,
    Wire_Node,
    WireFillet2d_Node,
    DiscretizeWire_Node,
    CurveLength_Node,
]
# -------------------------------------------


# BREPOFFSETAPI------------------------------

class BrepOffsetAPINodeBase(PythonOCCNodeBase):
    color = '#aabb44'

class Pipe_Node(BrepOffsetAPINodeBase):
    """
    Generates pipe________-
    o_Wire________________-
    o_Radius______________-
    """

    title = 'pipe'

    init_inputs = [
        NodeInputBP('wire', dtype=dtypes.Data(size='s')),
        NodeInputBP('radius', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        wire, radius = self.get_inputs()
        if type(wire) is list:
            pipes = []
            for w in wire:
                if isinstance(w, TopoDS_Edge):
                    w = BRepBuilderAPI_MakeWire(w).Wire()
                topexp_vertex = TopExp_Explorer()
                topexp_vertex.Init(w, TopAbs_VERTEX)
                vertices = []
                while topexp_vertex.More():
                    vert = topods_Vertex(topexp_vertex.Current())
                    point = BRep_Tool.Pnt(vert)
                    vertices.append(point)
                    topexp_vertex.Next()
                dir_ = gp_Dir(vertices[1].X()-vertices[0].X(), vertices[1].Y()-vertices[0].Y(), vertices[1].Z()-vertices[0].Z())
                if radius == 0:
                    radius = 0.01
                circle = gp_Circ(gp_Ax2(vertices[0], dir_), radius)
                profile_edge = BRepBuilderAPI_MakeEdge(circle).Edge()
                profile_wire = BRepBuilderAPI_MakeWire(profile_edge).Wire()
                profile_face = BRepBuilderAPI_MakeFace(profile_wire).Face()
                pipe = BRepOffsetAPI_MakePipe(w, profile_face).Shape()
                pipes.append(pipe)
            self.set_output_val(0, pipes)
        else:
            if isinstance(wire, TopoDS_Edge):
                wire = BRepBuilderAPI_MakeWire(wire).Wire()
            topexp_vertex = TopExp_Explorer()
            topexp_vertex.Init(wire, TopAbs_VERTEX)
            vertices = []
            while topexp_vertex.More():
                vert = topods_Vertex(topexp_vertex.Current())
                point = BRep_Tool.Pnt(vert)
                vertices.append(point)
                topexp_vertex.Next()
            dir_ = gp_Dir(vertices[1].X() - vertices[0].X(), vertices[1].Y() - vertices[0].Y(), vertices[1].Z() - vertices[0].Z())
            if radius == 0:
                radius = 0.01
            circle = gp_Circ(gp_Ax2(vertices[0], dir_), radius)
            profile_edge = BRepBuilderAPI_MakeEdge(circle).Edge()
            profile_wire = BRepBuilderAPI_MakeWire(profile_edge).Wire()
            profile_face = BRepBuilderAPI_MakeFace(profile_wire).Face()
            pipe = BRepOffsetAPI_MakePipe(wire, profile_face).Shape()
            self.set_output_val(0, pipe)

BRepOffsetAPI_nodes = [
    Pipe_Node,
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
        NodeInputBP('radius', dtype=dtypes.Data(size='s')),
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
        NodeInputBP('radius', dtype=dtypes.Data(size='s')),
        NodeInputBP('len', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        axe, radius, length = self.get_inputs()
        cylinder = BRepPrimAPI_MakeCylinder(axe, radius, length).Shape()
        self.set_output_val(0, cylinder)

class Torus_Node(BrepPrimAPINodeBase):
    """
    Generates torus__________-
    o_Ax2____________________-
    o_Distance center/center_-
    o_Radius_________________-
    """

    title = 'torus'

    init_inputs = [
        NodeInputBP('axe', dtype=dtypes.Data(size='s')),
        NodeInputBP('distance', dtype=dtypes.Data(size='s')),
        NodeInputBP('radius', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        axe, distance, radius = self.get_inputs()
        torus = BRepPrimAPI_MakeTorus(axe, distance, radius).Shape()
        self.set_output_val(0, torus)


BRepPrimAPI_nodes = [
    Box_Node,
    Sphere_Node,
    Cylinder_Node,
    Torus_Node,
]
# -------------------------------------------


# BREPALGOAPI --------------------------------

class BrepAlgoAPINodeBase(PythonOCCNodeBase):
    color = '#ab0c36'

class Fuse_Node(BrepAlgoAPINodeBase):
    """
    Generates fusion_________-
    o_Part 1 (or list)_______-
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
        if type(a) is list:
            count = len(a)
            fuse_shps = {}
            ijk = 0
            fuse_shps[ijk] = BRepAlgoAPI_Fuse(a[0], a[1]).Shape()
            for i in range(2, count):
                ijk += 1
                fuse_shps[ijk] = BRepAlgoAPI_Fuse(fuse_shps[ijk-1], a[i]).Shape()
            self.set_output_val(0, fuse_shps[ijk])
        else:
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
    o_Cutter (or list)_______-
    """

    title = 'cut'

    init_inputs = [
        NodeInputBP('Basis', dtype=dtypes.Data(size='s')),
        NodeInputBP('Cutter', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        basis, cutter = self.get_inputs()
        if type(cutter) is list and type(basis) is not list:
            count = len(cutter)
            cut_shps = {}
            ijk = 0
            cut_shps[ijk] = BRepAlgoAPI_Cut(basis, cutter[0]).Shape()
            for i in range(1, count):
                ijk += 1
                cut_shps[ijk] = BRepAlgoAPI_Cut(cut_shps[ijk - 1], cutter[i]).Shape()
            self.set_output_val(0, cut_shps[ijk])
        elif type(basis) is list and type(cutter) is not list:
            cut_shps = []
            for b in basis:
                cut_shps.append(BRepAlgoAPI_Cut(b, cutter).Shape())
            self.set_output_val(0, cut_shps)
        else:
            cut_shp = BRepAlgoAPI_Cut(basis, cutter).Shape()
            self.set_output_val(0, cut_shp)

class Section_Node(BrepAlgoAPINodeBase):
    """
    Generates Sections_______-
    o_Basis__________________-
    o_Cutter (or list)_______-
    """

    title = 'section'

    init_inputs = [
        NodeInputBP('Basis', dtype=dtypes.Data(size='s')),
        NodeInputBP('Cutter', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        basis, cutter = self.get_inputs()
        if type(cutter) is list and type(basis) is not list:
            count = len(cutter)
            cut_shps = {}
            ijk = 0
            cut_shps[ijk] = BRepAlgoAPI_Section(basis, cutter[0]).Shape()
            for i in range(1, count):
                ijk += 1
                cut_shps[ijk] = BRepAlgoAPI_Section(cut_shps[ijk - 1], cutter[i]).Shape()
            self.set_output_val(0, cut_shps[ijk])
        elif type(basis) is list and type(cutter) is not list:
            cut_shps = []
            for b in basis:
                cut_shps.append(BRepAlgoAPI_Section(b, cutter).Shape())
            self.set_output_val(0, cut_shps)
        else:
            cut_shp = BRepAlgoAPI_Section(basis, cutter).Shape()
            self.set_output_val(0, cut_shp)


BRepAlgoAPI_nodes = [
    Fuse_Node,
    Common_Node,
    Cut_Node,
    Section_Node,
]

# -------------------------------------------


# BREPFILLETAPI --------------------------------

class BrepFilletAPINodeBase(PythonOCCNodeBase):
    color = '#e0149c'

class Fillet_Node(BrepFilletAPINodeBase):
    """
    Generates fillet_________-
    o_Shape__________________-
    o_Radius_________________-
    """

    title = 'fillet'

    init_inputs = [
        NodeInputBP('shape', dtype=dtypes.Data(size='s')),
        NodeInputBP('radius', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        shape, radius = self.get_inputs()
        fill = BRepFilletAPI_MakeFillet(shape)

        for e in TopologyExplorer(shape).edges():
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

# GEOMAPI------------------------------------

class GeomNodeBase(PythonOCCNodeBase):
    color = '#c91604'

class Circle_Node(GeomNodeBase):
    """
    Draw circle______________-
    o_Ax2____________________-
    o_Radius_________________-
    """

    title = 'Circle'

    init_inputs = [
        NodeInputBP('Ax2', dtype=dtypes.Data(size='s')),
        NodeInputBP('Radius', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        axis, radius  = self.get_inputs()
        circle = Geom_Circle(axis, radius)
        self.set_output_val(0, circle)

Geom_nodes = [
    Circle_Node,
]

# -------------------------------------------

# GEOMAPI------------------------------------

class GeomAPINodeBase(PythonOCCNodeBase):
    color = '#ff4633'

class PointsSurface_Node(GeomAPINodeBase):
    """
    Generates surface________-
    o_List of points_________-
    """

    title = 'PointsSurface'

    init_inputs = [
        NodeInputBP('points', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        count = 0
        pts = {}
        for l in self.get_inputs():
            pts[count] = l
            nbpts = len(l)
            count += 1
        pts_list = list(pts.values())
        array = TColgp_Array2OfPnt(1, nbpts, 1, len(pts_list))  # nbrow, nbcol
        for c in range(count):
            for n in range(nbpts):
                print(pts[c][n])
                array.SetValue(n + 1, c + 1, pts[c][n])
        nurbs = GeomAPI_PointsToBSplineSurface(array, 2, 2, GeomAbs_C2, 0.001).Surface()
        self.set_output_val(0, nurbs)

GeomAPI_nodes = [
    PointsSurface_Node,
]

# -------------------------------------------


# TOPOLOGY EXPLORER--------------------------

class TopExplorer_Node(PythonOCCNodeBase):
    """
    Topology Explorer________-
    o_Shape__________________-
    """

    title = 'topexp'
    color = '#FF00FF'

    init_inputs = [
        NodeInputBP('shape', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP('vertex'),
        NodeOutputBP('edges'),
        NodeOutputBP('wires'),
        NodeOutputBP('faces'),
        NodeOutputBP('shells'),
        NodeOutputBP('solids'),
        NodeOutputBP('compounds'),
        NodeOutputBP('compsolids'),
    ]

    def update_event(self, inp=-1):
        for shape in self.get_inputs():
            #find vertices
            topexp_vertex = TopExp_Explorer()
            topexp_vertex.Init(shape, TopAbs_VERTEX)
            vertices = []
            while topexp_vertex.More():
                vert = topods_Vertex(topexp_vertex.Current())
                point = BRep_Tool.Pnt(vert)
                vertices.append(point)
                topexp_vertex.Next()
            vertices_red = filter_points_by_distance(vertices, 0.01)
            #find edges
            topexp_edge = TopExp_Explorer()
            topexp_edge.Init(shape, TopAbs_EDGE)
            edges = []
            while topexp_edge.More():
                edge = topods_Edge(topexp_edge.Current())
                edges.append(edge)
                topexp_edge.Next()
            # find wires
            topexp_wire = TopExp_Explorer()
            topexp_wire.Init(shape, TopAbs_WIRE)
            wires = []
            while topexp_wire.More():
                wire = topods_Wire(topexp_wire.Current())
                wires.append(wire)
                topexp_wire.Next()
            #find faces
            topexp_face = TopExp_Explorer()
            topexp_face.Init(shape, TopAbs_FACE)
            faces = []
            while topexp_face.More():
                face = topods_Face(topexp_face.Current())
                faces.append(face)
                topexp_face.Next()
            #find shells
            topexp_shell = TopExp_Explorer()
            topexp_shell.Init(shape, TopAbs_SHELL)
            shells = []
            while topexp_shell.More():
                shell = topods_Shell(topexp_shell.Current())
                shells.append(shell)
                topexp_shell.Next()
            # find solids
            topexp_solid = TopExp_Explorer()
            topexp_solid.Init(shape, TopAbs_SOLID)
            solids = []
            while topexp_solid.More():
                solid = topods_Solid(topexp_solid.Current())
                solids.append(solid)
                topexp_solid.Next()
            # find compounds
            topexp_compound = TopExp_Explorer()
            topexp_compound.Init(shape, TopAbs_COMPOUND)
            compounds = []
            while topexp_compound.More():
                compound = topods_Compound(topexp_compound.Current())
                compounds.append(compound)
                topexp_compound.Next()
            # find compsolids
            topexp_compsolid = TopExp_Explorer()
            topexp_compsolid.Init(shape, TopAbs_COMPSOLID)
            compsolids = []
            while topexp_compsolid.More():
                compsolid = topods_CompSolid(topexp_compsolid.Current())
                compsolids.append(compsolid)
                topexp_compsolid.Next()

        self.set_output_val(0, vertices_red)
        self.set_output_val(1, edges)
        self.set_output_val(2, wires)
        self.set_output_val(3, faces)
        self.set_output_val(4, shells)
        self.set_output_val(5, solids)
        self.set_output_val(6, compounds)
        self.set_output_val(7, compsolids)


TopExplorer_nodes = [
    TopExplorer_Node,
]


# -------------------------------------------


# DISPLAY --------------------------------

class DisplayNodeBase(PythonOCCNodeBase):
    color = '#3355dd'

class Display_Node(DisplayNodeBase):
    """
    display shapes
    o_Shapes__________________-
    """

    title = 'display'

    init_inputs = [
        NodeInputBP('shapes', dtype=dtypes.Data(size='s')),
    ]

    def update_event(self, inp=-1):
        display.EraseAll()
        for v in self.get_inputs():
            if v is None:
                pass
            elif type(v) is list :
                for el in v:
                    if type(el) is list :
                        for e in el:
                            if type(e) is list:
                                shape = e[0]
                                colore = e[1]
                                display.DisplayShape(shape, color=colore)
                            else:
                                if isinstance(e, int):
                                    shape = el[0]
                                    colore = el[1]
                                    display.DisplayShape(shape, color=colore)
                                else:
                                    display.DisplayShape(e)
                    else:
                        if isinstance(el, int):
                            shape = v[0]
                            colore = v[1]
                            display.DisplayShape(shape, color=colore)
                        else:
                            display.DisplayShape(el)
            else :
                display.DisplayShape(v)
        display.FitAll()

class Color_Node(DisplayNodeBase):
    """
    Choose Color_____________-
    o_Shape__________________-
    o_QuantityColor(int)_____-
    """

    title = 'color'

    init_inputs = [
        NodeInputBP('shape', dtype=dtypes.Data(size='s')),
        NodeInputBP('Int', dtype=dtypes.Data(size='s')),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        shapecolored = []
        shape, colore = self.get_inputs()
        if type(shape) is list:
            for shp in shape:
                shapecolored.append([shp, colore])
                self.set_output_val(0, shapecolored)
        else:
            shapecolored.append(shape)
            shapecolored.append(colore)
            self.set_output_val(0, shapecolored)


Display_nodes = [
    Display_Node,
    Color_Node,
]

# -------------------------------------------


# TOOLS--------------------------------------


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


class ListLength_Node(PythonOCCNodeBase):
    """
    List Length__________-
    o_List_______________-
    """

    title = 'ListLength'
    color = '#000000'

    init_inputs = [
        NodeInputBP('list', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        for el in self.get_inputs():
            if type(el) is list:
                length = len(el)
                self.set_output_val(0, length)
            else :
                pass


class FlattenList_Node(PythonOCCNodeBase):
    """
    Flatten list_________-
    o_List_______________-
    """

    title = 'FlattenList'
    color = '#000000'

    init_inputs = [
        NodeInputBP('list', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        newlist = []
        for el in self.get_inputs():
            if type(el) is list:
                for e in el:
                    if type(e) is list:
                        for a in e:
                            newlist.append(a)
                    else:
                        newlist.append(e)
            else:
                newlist.append(el)
        self.set_output_val(0,newlist)


class ListItem_Node(PythonOCCNodeBase):
    """
    Item list____________-
    o_List_______________-
    o_Indec______________-
    """

    title = 'ListItem'
    color = '#000000'

    init_inputs = [
        NodeInputBP('list', dtype=dtypes.Data(size='s')),
        NodeInputBP('index', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        reflist, index = self.get_inputs()
        self.set_output_val(0, reflist[index])


class RepeatData_Node(PythonOCCNodeBase):
    """
    Repeat Data__________-
    o_Data as List_______-
    o_Length of repeat___-
    """

    title = 'RepeatData'
    color = '#000000'

    init_inputs = [
        NodeInputBP('Data', dtype=dtypes.Data(size='s')),
        NodeInputBP('Length', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        Data, Length = self.get_inputs()
        repeat = []
        for l in range(Length):
            if type(Data) is list:
                for d in Data:
                    repeat.append(d)
            else:
                repeat.append(Data)
        self.set_output_val(0, repeat)


class Serie_Node(PythonOCCNodeBase):
    """
    Create Serie_________-
    o_Start______________-
    o_Step_______________-
    o_Length_____________-
    """

    title = 'Serie'
    color = '#000000'

    init_inputs = [
        NodeInputBP('Start', dtype=dtypes.Data(size='s')),
        NodeInputBP('Step', dtype=dtypes.Data(size='s')),
        NodeInputBP('Length', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        Start, Step, Length = self.get_inputs()
        serie = []
        count = Start
        serie.append(Start)
        for l in range(Length-1):
            count += Step
            serie.append(count)
        self.set_output_val(0, serie)

class ShiftList_Node(PythonOCCNodeBase):
    """
    Shift List___________-
    o_List_______________-
    o_Shift value________-
    """

    title = 'ShiftLIst'
    color = '#000000'

    init_inputs = [
        NodeInputBP('List', dtype=dtypes.Data(size='s')),
        NodeInputBP('ShiftValue', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        list_, value = self.get_inputs()
        shifted_list = []
        if value < 0:
            for i in range(len(list_) - value):
                shifted_list.append(list_[i])
        elif value > 0:
            for i in range(value, len(list_)):
                shifted_list.append(list_[i])
        self.set_output_val(0, shifted_list)


Tools_nodes = [
    List_Node,
    ListLength_Node,
    FlattenList_Node,
    ListItem_Node,
    RepeatData_Node,
    Serie_Node,
    ShiftList_Node,
]

# --------------------------------------------------------


# DATA EXCHANGE------------------------------------------
class DataExchangeNodeBase(PythonOCCNodeBase):
     color = '#6b6767'

class ExportStep_Node(DataExchangeNodeBase):
    """
    Generates Step_______-
    o_Shape______________-
    o_Name_______________-
    """

    title = 'ExportStep'

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
        status = step_writer.Write(str(filename)+'.stp')

class ImportStep_Node(DataExchangeNodeBase):
    """
    Import Step__________-
    o_Filename___________-
    """

    title = 'ImportStep'
    doc = 'returns the evaluated text that is typed into the input field'
    init_outputs = [
        NodeOutputBP(),
    ]
    main_widget_class = widgets.ImportFileNode_MainWidget
    main_widget_pos = 'between ports'
    style = 'normal'

    def __init__(self, params):
        super().__init__(params)

        self.actions['edit string via dialog'] = {'method': self.action_edit_via_dialog}
        self.string = None


    def place_event(self):
        self.update()

    def view_place_event(self):
        self.main_widget().value_changed.connect(self.main_widget_string_changed)

    def main_widget_string_changed(self, string):
        self.string = string
        self.update()

    def update_event(self, input_called=-1):
        shape = read_step_file(self.string)
        self.set_output_val(0, shape)

    def action_edit_via_dialog(self):
        return

        # from ..EditVal_Dialog import EditVal_Dialog
        #
        # val_dialog = EditVal_Dialog(parent=None, init_val=self.val)
        # accepted = val_dialog.exec_()
        # if accepted:
        #	 self.main_widget().setText(str(val_dialog.get_val()))
        #	 self.update()


    def get_current_var_name(self):
        return self.input(0)


    def get_state(self):
        return {
            'string': self.string  # self.main_widget().get_val()
        }

    def set_state(self, data):
        self.string = data['string']

class ExportStl_Node(DataExchangeNodeBase):
    """
    Generates Stl________-
    o_Shape______________-
    o_Name_______________-
    """

    title = 'ExportStl'

    init_inputs = [
        NodeInputBP('shape', dtype=dtypes.Data(size='s')),
        NodeInputBP('name', dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def update_event(self, inp=-1):
        shape, filename = self.get_inputs()
        status = write_stl_file(shape, str(filename)+'.stl', mode="ascii", linear_deflection=0.9, angular_deflection=0.5)


class ImportStl_Node(DataExchangeNodeBase):
    """
    Import Stl___________-
    o_Filename___________-
    """

    title = 'ImportStl'
    doc = 'returns the evaluated text that is typed into the input field'
    init_outputs = [
        NodeOutputBP(),
    ]
    main_widget_class = widgets.ImportFileNode_MainWidget
    main_widget_pos = 'between ports'
    style = 'normal'

    def __init__(self, params):
        super().__init__(params)

        self.actions['edit string via dialog'] = {'method': self.action_edit_via_dialog}
        self.string = None


    def place_event(self):
        self.update()

    def view_place_event(self):
        self.main_widget().value_changed.connect(self.main_widget_string_changed)

    def main_widget_string_changed(self, string):
        self.string = string
        self.update()

    def update_event(self, input_called=-1):
        shape = read_stl_file(self.string)
        self.set_output_val(0, shape)

    def action_edit_via_dialog(self):
        return

        # from ..EditVal_Dialog import EditVal_Dialog
        #
        # val_dialog = EditVal_Dialog(parent=None, init_val=self.val)
        # accepted = val_dialog.exec_()
        # if accepted:
        #	 self.main_widget().setText(str(val_dialog.get_val()))
        #	 self.update()


    def get_current_var_name(self):
        return self.input(0)


    def get_state(self):
        return {
            'string': self.string  # self.main_widget().get_val()
        }

    def set_state(self, data):
        self.string = data['string']

DataExchange_nodes = [
    ExportStep_Node,
    ImportStep_Node,
    ExportStl_Node,
    ImportStl_Node,
]

# -------------------------------------------


export_nodes(
    *Gp_nodes,
    *BRepBuilderAPI_nodes,
    *BRepOffsetAPI_nodes,
    *BRepPrimAPI_nodes,
    *BRepAlgoAPI_nodes,
    *BRepFilletAPI_nodes,
    *Geom_nodes,
    *GeomAPI_nodes,
    *TopExplorer_nodes,
    *Display_nodes,
    *Tools_nodes,
    *DataExchange_nodes,
)
