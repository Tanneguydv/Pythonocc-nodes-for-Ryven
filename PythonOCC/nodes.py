from ryven.node_env import *

guis = import_guis(__file__)

# if ryven is runnign headless, there are no gui imports
attach_input_widgets = \
    guis.GuiBuilder.attach_input_widgets \
    if guis.GuiBuilder is not None else \
    lambda _: lambda cls: cls


# 
# PythonOCC imports
# 


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

from OCC.Extend.ShapeFactory import \
    get_oriented_boundingbox

from OCCUtils.Common import \
    filter_points_by_distance, \
    curve_length

# TODO: Edge import causes crash
# from OCCUtils.edge import Edge


# 
# 3D Viewer
# 


from datetime import datetime
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

add_menu('Screenshot')


def Save_Screenshot():
    screenshot_OCC_name = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + '_screenshot.jpg'
    display.ExportToImage(screenshot_OCC_name)


add_function_to_menu('Screenshot', Save_Screenshot)


# 
# Data types
# 


class OCCData(Data):
    """
    Base class for all OCC data types passed between nodes.
    """

    # TODO: discuss data serialization approach

    # PythonOCC doesn't support pickling, so we need to
    # come up with a serialization approach.
    # There are who options for data serialization here:
    # 1. Explicitly define serialization of all OCC types passed
    #   between nodes, to the point where it can be serialized
    #   by pickele (e.g. dict). This is a lot of work.
    # 2. Violate correct graph reconstruction by simply loading
    #   any data into a placeholder e.g. `None`.
    #   This means the graph is not reconstructed exactly as it 
    #   was saved, all OCCData objects will lose their payload,
    #   in particular all node output values will be useless.
    #   But if the nodes are designed correctly and do not store
    #   any state, by very few manual well chosen updates
    #   the user can effectively reconstruct the graph.
    #   For simplicity, this is the approach taken here for now.

    def get_data(self):
        return None
    
    def set_data(self, data):
        pass


# 
# Node base classes
# 


class PythonOCCNodeBase(Node):

    GUI = guis.PythonOCCNodeGuiBase

    def inp(self, index):
        """Convenience method to unpack input data if applicable."""
        return self.input(index).payload if self.input(index) is not None else None

    def get_inputs(self):
        """Convenience method to get a tuple of all (unpacked) input values."""
        return (self.inp(i) for i in range(len(self.inputs)))

    def have_gui(self):
        # check if we are running with a GUI
        # and not in headless mode
        return hasattr(self, 'gui')


class PythonOCCNodeBase_DynamicInputs(PythonOCCNodeBase):

    GUI = guis.PyOCCBase_DynamicInputsGui

    num_init_inputs = 0

    def place_event(self):
        for i in range(self.num_init_inputs):
            if self.have_gui():
                self.gui.add_operand_input()
            else:
                self.add_operand_input()

    def add_operand_input(self):
        # self.create_input_dt(dtype=dtypes.Data(size='s'))
        # TODO: input widgets are currently only supported in initial inputs
        # fallback:
        self.create_input()

        self.update()

    def remove_operand_input(self, index):
        self.delete_input(index)
        self.update()

    def update_event(self, inp=-1):
        self.set_output_val(0, OCCData(
            self.apply_op([self.inp(i) for i in range(len(self.inputs))])
        ))

    def apply_op(self, elements: list):
        return None


# 
# GP nodes
# 


class GpNodeBase(PythonOCCNodeBase):
    version = 'v0.1'
    GUI = guis.GpNodeGui


@attach_input_widgets([
    'DataSmall', 
    'DataSmall', 
    'DataSmall',
])
class Pnt_Node(GpNodeBase):
    """
    Generates Point_______-
    o_X___________________-
    o_Y___________________-
    o_Z___________________-
    """

    title = 'point'

    init_inputs = [
        NodeInputType('x'),
        NodeInputType('y'),
        NodeInputType('z'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        x, y, z = self.clean(self.get_inputs())
        self.set_output_val(0, OCCData(
            gp_Pnt(x, y, z)
        ))

    def clean(self, coords):
        """Returns a tuple of coords where `None` values are replaced by 0"""
        return ( (c if c is not None else 0) for c in coords )


class PointZero_Node(GpNodeBase):
    """
    Generates Point Zero__-
    """

    title = 'Point0'

    init_outputs = [
        NodeOutputType(),
    ]

    def place_event(self):
        point = gp_Pnt(0,0,0)
        self.set_output_val(0, OCCData(point))


@attach_input_widgets([
    'DataSmall',
])
class DeconstructPnt_Node(GpNodeBase):
    """
    Deconstruct Point_____-
    o_Point_______________-
    """

    title = 'deconstruct point'

    init_inputs = [
        NodeInputType('point'),
    ]

    init_outputs = [
        NodeOutputType('X'),
        NodeOutputType('Y'),
        NodeOutputType('Z'),
    ]

    def update_event(self, inp=-1):
        for point in self.get_inputs():
            self.set_output_val(0, OCCData(point.X()))
            self.set_output_val(1, OCCData(point.Y()))
            self.set_output_val(2, OCCData(point.Z()))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
    'DataSmall',
])
class Vec_Node(GpNodeBase):
    """
    Generates Vector______-
    o_X___________________-
    o_Y___________________-
    o_Z___________________-
    """

    title = 'Vector'

    init_inputs = [
        NodeInputType('x'),
        NodeInputType('y'),
        NodeInputType('z'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        x, y, z = self.get_inputs()
        self.set_output_val(0, OCCData(gp_Vec(x, y, z)))


class DX_Node(GpNodeBase):
    """
    Generates Dir X____-
    """

    title = 'DirX'

    init_outputs = [
        NodeOutputType(),
    ]

    def place_event(self):
        dx = gp_DX()
        self.set_output_val(0, OCCData(dx))


class DY_Node(GpNodeBase):
    """
    Generates Dir Y____-
    """

    title = 'DirY'

    init_outputs = [
        NodeOutputType(),
    ]

    def place_event(self):
        dy = gp_DY()
        self.set_output_val(0, OCCData(dy))


class DZ_Node(GpNodeBase):
    """
    Generates Dir Z____-
    """

    title = 'DirZ'

    init_outputs = [
        NodeOutputType(),
    ]

    def place_event(self):
        dz = gp_DZ()
        self.set_output_val(0, OCCData(dz))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
    'DataSmall',
])
class Dir_Node(GpNodeBase):
    """
    Generates Dir_______-
    o_X___________________-
    o_Y___________________-
    o_Z___________________-
    """

    title = 'dir'

    init_inputs = [
        NodeInputType('x'),
        NodeInputType('y'),
        NodeInputType('z'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        x, y, z = self.get_inputs()
        self.set_output_val(0, OCCData(gp_Dir(x, y, z)))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Ax2_Node(GpNodeBase):
    """
    Generates Ax2_________-
    o_Point_______________-
    o_Dir_________________-
    """

    title = 'Ax2'

    init_inputs = [
        NodeInputType('point'),
        NodeInputType('dir'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        point, dir_ = self.get_inputs()
        self.set_output_val(0, OCCData(gp_Ax2(point, dir_)))

class XOY_Node(GpNodeBase):
    """
    Generates Ax Z____-
    """

    title = 'AxZ'

    init_outputs = [
        NodeOutputType(),
    ]

    def place_event(self):
        axz = gp_XOY()
        self.set_output_val(0, OCCData(axz))

class YOZ_Node(GpNodeBase):
    """
    Generates Ax X____-
    """

    title = 'AxX'

    init_outputs = [
        NodeOutputType(),
    ]

    def place_event(self):
        axx = gp_YOZ()
        self.set_output_val(0, OCCData(axx))

class ZOX_Node(GpNodeBase):
    """
    Generates Ax Y____-
    """

    title = 'AxY'

    init_outputs = [
        NodeOutputType(),
    ]

    def place_event(self):
        axy = gp_ZOX()
        self.set_output_val(0, OCCData(axy))

@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Pln_Node(GpNodeBase):
    """
    Generates Plane_______-
    o_Point_______________-
    o_Dir_________________-
    """

    title = 'Plane'

    init_inputs = [
        NodeInputType('point'),
        NodeInputType('dir'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        point, dir_ = self.get_inputs()
        self.set_output_val(0, OCCData(gp_Pln(point, dir_)))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Trsf_Node(GpNodeBase):
    """
    Generates transform___-
    o_[Shapes]____________-
    o_[Vectors]___________-
    """

    title = 'Transform'

    init_inputs = [
        NodeInputType('shapes'),
        NodeInputType('vectors'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        shapes, vectors = self.get_inputs()
        result = []
        
        if isinstance(shapes, list) and isinstance(vectors, list):
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
            self.set_output_val(0, OCCData(result))
        
        elif isinstance(shapes, list) and not isinstance(vectors, list):
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
            self.set_output_val(0, OCCData(result))
        
        elif not isinstance(shapes, list) and isinstance(vectors, list):
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
            self.set_output_val(0, OCCData(result))
        
        else:
            trns = gp_Trsf()
            trns.SetTranslation(vectors)
            if isinstance(shapes, gp_Pnt):
                sh2 = shapes
                sh2.Transform(trns)
                translated = sh2
            else:
                translated = BRepBuilderAPI_Transform(shapes, trns).Shape()
            self.set_output_val(0, OCCData(translated))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
    'DataSmall',
])
class Move2pts_Node(GpNodeBase):
    """
    Move 2 points_________-
    o_from pnt____________-
    o_to pnt______________-
    """

    title = 'Move2pnts'

    init_inputs = [
        NodeInputType('shapes'),
        NodeInputType('from'),
        NodeInputType('to'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        shapes, from_pnt, to_pnt = self.get_inputs()
        vectors = []
        result = []

        if isinstance(from_pnt, list):
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
            self.set_output_val(0, OCCData(result))
        
        else:
            v = gp_Vec()
            x = to_pnt.X() - from_pnt.X()
            y = to_pnt.Y() - from_pnt.Y()
            z = to_pnt.Z() - from_pnt.Z()
            v.SetCoord(x, y, z)
            trns = gp_Trsf()
            trns.SetTranslation(v.Reversed())
            translated = BRepBuilderAPI_Transform(shapes, trns).Shape()
            self.set_output_val(0, OCCData(translated))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class MidPoint_Node(GpNodeBase):
    """
    MidPoint_____________-
    o_Point A____________-
    o_Point B______________-
    """

    title = 'MidPoint'

    init_inputs = [
        NodeInputType('pointA'),
        NodeInputType('pointB'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        pointA, pointB = self.get_inputs()
        vec1 = gp_Vec(pointA.XYZ())
        vec2 = gp_Vec(pointB.XYZ())
        midvec = (vec1 + vec2) / 2.
        midpoint = gp_Pnt(midvec.XYZ())
        self.set_output_val(0, OCCData(midpoint))


@attach_input_widgets([
    'DataSmall',
])
class Get_dir_from_edge_Node(GpNodeBase):
    """
    Dir from Edge________-
    o_Edge_______________-
    """

    title = 'DirfromEdge'

    init_inputs = [
        NodeInputType('Edge'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        print('ERROR - EDGE IS BROKEN')
        return

        for edge in self.get_inputs():
            edg = Edge(edge)
            first_point = BRep_Tool.Pnt(edg.first_vertex())
            last_point = BRep_Tool.Pnt(edg.last_vertex())
            dir_edge = gp_Dir(last_point.X() - first_point.X(), last_point.Y() - first_point.Y(),
                              last_point.Z() - first_point.Z())
        self.set_output_val(0, OCCData(dir_edge))


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
    Get_dir_from_edge_Node,
]


# 
# BrepBuilderAPI nodes
# 


class BrepBuilderAPINodeBase(PythonOCCNodeBase):
    version = 'v0.1'
    GUI = guis.BrepBuilderAPINodeGui


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class TwoPtsEdge_Node(BrepBuilderAPINodeBase):
    """
    Generates 2 pts Edge__-
    o_Point_______________-
    o_Point_______________-
    """

    title = '2ptsEdge'

    init_inputs = [
        NodeInputType('pnt1'),
        NodeInputType('Pnt2'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        pnt1, pnt2 = self.get_inputs()

        if isinstance(pnt1, list):
            edges = []
            for p1, p2 in zip(pnt1, pnt2):
                edge = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
                edges.append(edge)
            self.set_output_val(0, OCCData(edges))
        
        else:
            edge = BRepBuilderAPI_MakeEdge(pnt1, pnt2).Edge()
            self.set_output_val(0, OCCData(edge))


@attach_input_widgets([
    'DataSmall',
])
class Wire_Node(BrepBuilderAPINodeBase):
    """
    Generates Wire________-
    o_List of Points______-
    """

    title = 'Wire'

    init_inputs = [
        NodeInputType('pntslist'),
    ]

    init_outputs = [
        NodeOutputType(),
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
        
        self.set_output_val(0, OCCData(wirebuild.Shape()))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class WireFillet2d_Node(BrepBuilderAPINodeBase):
    """
    Generates 2dWireFillet_-
    o_List of Points______-
    o_Fillet Radius_______-
    """

    title = '2dWireFillet'

    init_inputs = [
        NodeInputType('pntslist'),
        NodeInputType('radius'),
    ]

    init_outputs = [
        NodeOutputType(),
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
        self.set_output_val(0, OCCData(wirebuild.Shape()))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class DiscretizeWire_Node(BrepBuilderAPINodeBase):
    """
    Discretize Wire_______-
    o_Wire________________-
    o_Nb of points________-
    """

    title = 'DiscretizeWire'

    init_inputs = [
        NodeInputType('Wire'),
        NodeInputType('Nb'),
    ]

    init_outputs = [
        NodeOutputType(),
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
        self.set_output_val(0, OCCData(pnts))
        # print(tmp)

@attach_input_widgets([
    'DataSmall',
])
class CurveLength_Node(BrepBuilderAPINodeBase):
    """
    Curve Length__________-
    o_Wire/Edge(L)________-
    """

    title = 'CurveLength'

    init_inputs = [
        NodeInputType('Wire/Edge'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        lengths = []
        for curve in self.get_inputs():
            lengths.append(curve_length(curve))
        self.set_output_val(0, OCCData(lengths))
        # print(tmp)


BRepBuilderAPI_nodes = [
    TwoPtsEdge_Node,
    Wire_Node,
    WireFillet2d_Node,
    DiscretizeWire_Node,
    CurveLength_Node,
]


# 
# BrepOffsetAPI nodes
# 


class BrepOffsetAPINodeBase(PythonOCCNodeBase):
    version = 'v0.1'
    GUI = guis.BrepOffsetAPINodeGui


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Pipe_Node(BrepOffsetAPINodeBase):
    """
    Generates pipe________-
    o_Wire________________-
    o_Radius______________-
    """

    title = 'pipe'

    init_inputs = [
        NodeInputType('wire'),
        NodeInputType('radius'),
    ]

    init_outputs = [
        NodeOutputType(),
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
            self.set_output_val(0, OCCData(pipes))
       
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
            self.set_output_val(0, OCCData(pipe))


BRepOffsetAPI_nodes = [
    Pipe_Node,
]


# 
# BRepPrimAPI nodes
# 


class BrepPrimAPINodeBase(PythonOCCNodeBase):
    version = 'v0.1'
    GUI = guis.BrepPrimAPINodeBase


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
    'DataSmall',
])
class Box_Node(BrepPrimAPINodeBase):
    """
    Generates box_________-
    o_Width_______________-
    o_Length______________-
    o_Height______________-
    """

    title = 'box'

    init_inputs = [
        NodeInputType('w'),
        NodeInputType('l'),
        NodeInputType('h'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        width, length, height = self.get_inputs()
        box = BRepPrimAPI_MakeBox(gp_Pnt(), width, length, height).Shape()
        self.set_output_val(0, OCCData(box))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Sphere_Node(BrepPrimAPINodeBase):
    """
    Generates sphere_________-
    o_Center point/ax2_______-
    o_Radius_________________-
    """

    title = 'sphere'

    init_inputs = [
        NodeInputType('point'),
        NodeInputType('radius'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        point, radius = self.get_inputs()
        sphere = BRepPrimAPI_MakeSphere(point, radius).Shape()
        self.set_output_val(0, OCCData(sphere))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
    'DataSmall',
])
class Cylinder_Node(BrepPrimAPINodeBase):
    """
    Generates cylinder_______-
    o_Axe____________________-
    o_Radius_________________-
    o_Length_________________-
    """

    title = 'cylinder'

    init_inputs = [
        NodeInputType('axe'),
        NodeInputType('radius'),
        NodeInputType('len'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        axe, radius, length = self.get_inputs()
        cylinder = BRepPrimAPI_MakeCylinder(axe, radius, length).Shape()
        self.set_output_val(0, OCCData(cylinder))

@attach_input_widgets([
    'DataSmall',
    'DataSmall',
    'DataSmall',
])
class Torus_Node(BrepPrimAPINodeBase):
    """
    Generates torus__________-
    o_Ax2____________________-
    o_Distance center/center_-
    o_Radius_________________-
    """

    title = 'torus'

    init_inputs = [
        NodeInputType('axe'),
        NodeInputType('distance'),
        NodeInputType('radius'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        axe, distance, radius = self.get_inputs()
        torus = BRepPrimAPI_MakeTorus(axe, distance, radius).Shape()
        self.set_output_val(0, OCCData(torus))


BRepPrimAPI_nodes = [
    Box_Node,
    Sphere_Node,
    Cylinder_Node,
    Torus_Node,
]


# 
# BrepAlgoAPI nodes
# 


class BrepAlgoAPINodeBase(PythonOCCNodeBase):
    version = 'v0.1'
    GUI = guis.BrepAlgoAPINodeGui


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Fuse_Node(BrepAlgoAPINodeBase):
    """
    Generates fusion_________-
    o_Part 1 (or list)_______-
    o_Part 2_________________-
    """

    title = 'fuse'

    init_inputs = [
        NodeInputType('a'),
        NodeInputType('b'),
    ]
    init_outputs = [
        NodeOutputType(),
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
            self.set_output_val(0, OCCData(fuse_shps[ijk]))
        else:
            fuse_shp = BRepAlgoAPI_Fuse(a, b).Shape()
            self.set_output_val(0, OCCData(fuse_shp))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Common_Node(BrepAlgoAPINodeBase):
    """
    Generates common_________-
    o_Part 1_________________-
    o_Part 2_________________-
    """

    title = 'common'

    init_inputs = [
        NodeInputType('a'),
        NodeInputType('b'),
    ]
    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        a, b = self.get_inputs()
        common_shp = BRepAlgoAPI_Common(a, b).Shape()
        self.set_output_val(0, OCCData(common_shp))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Cut_Node(BrepAlgoAPINodeBase):
    """
    Generates cutting________-
    o_Basis__________________-
    o_Cutter (or list)_______-
    """

    title = 'cut'

    init_inputs = [
        NodeInputType('Basis'),
        NodeInputType('Cutter'),
    ]
    init_outputs = [
        NodeOutputType(),
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
            self.set_output_val(0, OCCData(cut_shps[ijk]))
        elif type(basis) is list and type(cutter) is not list:
            cut_shps = []
            for b in basis:
                cut_shps.append(BRepAlgoAPI_Cut(b, cutter).Shape())
            self.set_output_val(0, OCCData(cut_shps))
        else:
            cut_shp = BRepAlgoAPI_Cut(basis, cutter).Shape()
            self.set_output_val(0, OCCData(cut_shp))

@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Section_Node(BrepAlgoAPINodeBase):
    """
    Generates Sections_______-
    o_Basis__________________-
    o_Cutter (or list)_______-
    """

    title = 'section'

    init_inputs = [
        NodeInputType('Basis'),
        NodeInputType('Cutter'),
    ]
    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        basis, cutter = self.get_inputs()
        if None not in (basis, cutter):
            if type(cutter) is list and type(basis) is not list:
                count = len(cutter)
                cut_shps = {}
                ijk = 0
                cut_shps[ijk] = BRepAlgoAPI_Section(basis, cutter[0]).Shape()
                for i in range(1, count):
                    ijk += 1
                    cut_shps[ijk] = BRepAlgoAPI_Section(cut_shps[ijk - 1], cutter[i]).Shape()
                self.set_output_val(0, OCCData(cut_shps[ijk]))
            elif type(basis) is list and type(cutter) is not list:
                cut_shps = []
                for b in basis:
                    cut_shps.append(BRepAlgoAPI_Section(b, cutter).Shape())
                self.set_output_val(0, OCCData(cut_shps))
            else:
                cut_shp = BRepAlgoAPI_Section(basis, cutter).Shape()
                self.set_output_val(0, OCCData(cut_shp))


BRepAlgoAPI_nodes = [
    Fuse_Node,
    Common_Node,
    Cut_Node,
    Section_Node,
]


# BrepFilletAPI nodes
# 


class BrepFilletAPINodeBase(PythonOCCNodeBase):
    version = 'v0.1'
    GUI = guis.BrepFilletAPINodeGui


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Fillet_Node(BrepFilletAPINodeBase):
    """
    Generates fillet_________-
    o_Shape__________________-
    o_Radius_________________-
    """

    title = 'fillet'

    init_inputs = [
        NodeInputType('shape'),
        NodeInputType('radius'),
    ]
    init_outputs = [
        NodeOutputType(),
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

        self.set_output_val(0, OCCData(blended_fused_solids))


BRepFilletAPI_nodes = [
    Fillet_Node,
]


# 
# Geom and GeomAPI nodes
# 


class GeomNodeBase(PythonOCCNodeBase):
    version = 'v0.1'
    GUI = guis.GeomNodeGui

@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Circle_Node(GeomNodeBase):
    """
    Draw circle______________-
    o_Ax2____________________-
    o_Radius_________________-
    """

    title = 'Circle'

    init_inputs = [
        NodeInputType('Ax2'),
        NodeInputType('Radius'),
    ]
    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        axis, radius  = self.get_inputs()
        circle = Geom_Circle(axis, radius)
        self.set_output_val(0, OCCData(circle))

Geom_nodes = [
    Circle_Node,
]

class GeomAPINodeBase(PythonOCCNodeBase):
    version = 'v0.1'
    GUI = guis.GeomAPINodeGui

@attach_input_widgets([
    'DataSmall',
])
class PointsSurface_Node(GeomAPINodeBase):
    """
    Generates surface________-
    o_List of points_________-
    """

    title = 'PointsSurface'

    init_inputs = [
        NodeInputType('points'),
    ]
    init_outputs = [
        NodeOutputType(),
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
        self.set_output_val(0, OCCData(nurbs))


GeomAPI_nodes = [
    PointsSurface_Node,
]


# 
# Shape Analysis
# 


@attach_input_widgets([
    'DataSmall',
])
class TopExplorer_Node(PythonOCCNodeBase):
    """
    Topology Explorer________-
    o_Shape__________________-
    """

    title = 'topexp'
    version = 'v0.1'
    GUI = guis.TopExplorerGui

    init_inputs = [
        NodeInputType('shape'),
    ]
    init_outputs = [
        NodeOutputType('vertex'),
        NodeOutputType('edges'),
        NodeOutputType('wires'),
        NodeOutputType('faces'),
        NodeOutputType('shells'),
        NodeOutputType('solids'),
        NodeOutputType('compounds'),
        NodeOutputType('compsolids'),
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

        self.set_output_val(0, OCCData(vertices_red))
        self.set_output_val(1, OCCData(edges))
        self.set_output_val(2, OCCData(wires))
        self.set_output_val(3, OCCData(faces))
        self.set_output_val(4, OCCData(shells))
        self.set_output_val(5, OCCData(solids))
        self.set_output_val(6, OCCData(compounds))
        self.set_output_val(7, OCCData(compsolids))


@attach_input_widgets([
    'DataSmall',
])
class BoundingBox_Node(PythonOCCNodeBase):
    """
    Bounding Box________-
    o_Shape__________________-
    """

    title = 'bounding box'
    version = 'v0.1'
    GUI = guis.BoundingBoxGui

    init_inputs = [
        NodeInputType('shape'),
    ]
    init_outputs = [
        NodeOutputType('box'),
    ]

    def update_event(self, inp=-1):
        bboxes = []
        for shape in self.get_inputs():
            aBaryCenter, [aHalfX, aHalfY, aHalfZ], aBox = get_oriented_boundingbox(shape)
            bboxes.append(aBox)
        self.set_output_val(0, OCCData(bboxes))  # TODO make it work for list


Shape_Analysis_nodes = [
    TopExplorer_Node,
    BoundingBox_Node,
]


# 
# Display nodes
# 


class DisplayNodeBase(PythonOCCNodeBase):
    version = 'v0.1'
    GUI = guis.DisplayNodeGui


@attach_input_widgets([
    'DataSmall',
])
class Display_Node(DisplayNodeBase):
    """
    display shapes
    o_Shapes__________________-
    """

    title = 'display'

    init_inputs = [
        NodeInputType('shapes'),
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


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class Color_Node(DisplayNodeBase):
    """
    Choose Color_____________-
    o_Shape__________________-
    o_QuantityColor(int)_____-
    """

    title = 'color'

    init_inputs = [
        NodeInputType('shape'),
        NodeInputType('Int'),
    ]
    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        shapecolored = []
        shape, colore = self.get_inputs()
        if type(shape) is list:
            for shp in shape:
                shapecolored.append([shp, colore])
                self.set_output_val(0, OCCData(shapecolored))
        else:
            shapecolored.append(shape)
            shapecolored.append(colore)
            self.set_output_val(0, OCCData(shapecolored))


Display_nodes = [
    Display_Node,
    Color_Node,
]


#
# Utility nodes
# 


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class List_Node(PythonOCCNodeBase_DynamicInputs):
    """
    Generates List_______-
    o_A__________________-
    o_B__________________-
    """

    title = 'List'
    version = 'v0.1'
    GUI = guis.ListGui

    init_inputs = [
        NodeInputType(),
        NodeInputType(),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def apply_op(self, elements: list):
        return elements


@attach_input_widgets([
    'DataSmall',
])
class ListLength_Node(PythonOCCNodeBase):
    """
    List Length__________-
    o_List_______________-
    """

    title = 'ListLength'
    version = 'v0.1'
    GUI = guis.ListLengthGui

    init_inputs = [
        NodeInputType('list'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        for el in self.get_inputs():
            if type(el) is list:
                length = len(el)
                self.set_output_val(0, OCCData(length))
            else :
                pass


@attach_input_widgets([
    'DataSmall',
])
class FlattenList_Node(PythonOCCNodeBase):
    """
    Flatten list_________-
    o_List_______________-
    """

    title = 'FlattenList'
    version = 'v0.1'
    GUI = guis.FlattenListGui

    init_inputs = [
        NodeInputType('list'),
    ]

    init_outputs = [
        NodeOutputType(),
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
        self.set_output_val(0, OCCData(newlist))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class ListItem_Node(PythonOCCNodeBase):
    """
    Item list____________-
    o_List_______________-
    o_Indec______________-
    """

    title = 'ListItem'
    version = 'v0.1'
    GUI = guis.ListItemGui

    init_inputs = [
        NodeInputType('list'),
        NodeInputType('index'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        reflist, index = self.get_inputs()
        self.set_output_val(0, OCCData(reflist[index]))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class RepeatData_Node(PythonOCCNodeBase):
    """
    Repeat Data__________-
    o_Data as List_______-
    o_Length of repeat___-
    """

    title = 'RepeatData'
    version = 'v0.1'
    GUI = guis.RepeatDataGui

    init_inputs = [
        NodeInputType('Data'),
        NodeInputType('Length'),
    ]

    init_outputs = [
        NodeOutputType(),
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
        self.set_output_val(0, OCCData(repeat))


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
    'DataSmall',
])
class Serie_Node(PythonOCCNodeBase):
    """
    Create Serie_________-
    o_Start______________-
    o_Step_______________-
    o_Length_____________-
    """

    title = 'Serie'
    version = 'v0.1'
    GUI = guis.SerieGui

    init_inputs = [
        NodeInputType('Start'),
        NodeInputType('Step'),
        NodeInputType('Length'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        Start, Step, Length = self.get_inputs()
        serie = []
        count = Start
        serie.append(Start)
        for l in range(Length-1):
            count += Step
            serie.append(count)
        self.set_output_val(0, OCCData(serie))

@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class ShiftList_Node(PythonOCCNodeBase):
    """
    Shift List___________-
    o_List_______________-
    o_Shift value________-
    """

    title = 'ShiftLIst'
    version = 'v0.1'
    GUI = guis.ShiftListGui

    init_inputs = [
        NodeInputType('List'),
        NodeInputType('ShiftValue'),
    ]

    init_outputs = [
        NodeOutputType(),
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
        self.set_output_val(0, OCCData(shifted_list))


Tools_nodes = [
    List_Node,
    ListLength_Node,
    FlattenList_Node,
    ListItem_Node,
    RepeatData_Node,
    Serie_Node,
    ShiftList_Node,
]


# 
# Data Exchange nodes
# 


class DataExchangeNodeBase(PythonOCCNodeBase):
    version = 'v0.1'
    GUI = guis.DataExchangeNodeGui


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class ExportStep_Node(DataExchangeNodeBase):
    """
    Generates Step_______-
    o_Shape______________-
    o_Name_______________-
    """

    title = 'ExportStep'

    init_inputs = [
        NodeInputType('shape'),
        NodeInputType('fname'),
    ]

    init_outputs = [
        NodeOutputType(),
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
        NodeOutputType(),
    ]
    # main_widget_class = guis.ImportFileNode_MainWidget
    # main_widget_pos = 'between ports'
    # style = 'normal'
    GUI = guis.ImportFileNode_Gui

    def __init__(self, params):
        super().__init__(params)

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
        self.set_output_val(0, OCCData(shape))

    def get_current_var_name(self):
        return self.inp(0)

    def get_state(self):
        return {'string': self.string}

    def set_state(self, data, version):
        self.string = data['string']


@attach_input_widgets([
    'DataSmall',
    'DataSmall',
])
class ExportStl_Node(DataExchangeNodeBase):
    """
    Generates Stl________-
    o_Shape______________-
    o_Name_______________-
    """

    title = 'ExportStl'

    init_inputs = [
        NodeInputType('shape'),
        NodeInputType('name'),
    ]

    init_outputs = [
        NodeOutputType(),
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
        NodeOutputType(),
    ]
    # main_widget_class = guis.ImportFileNode_MainWidget
    # main_widget_pos = 'between ports'
    # style = 'normal'
    GUI = guis.ImportFileNode_Gui

    def __init__(self, params):
        super().__init__(params)

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
        self.set_output_val(0, OCCData(shape))

    def get_current_var_name(self):
        return self.inp(0)

    def get_state(self):
        return {'string': self.string}

    def set_state(self, data, version):
        self.string = data['string']

@attach_input_widgets([
    'DataSmall',
    'DataSmall',
    'DataSmall',
])
class ExportGcode_Node(DataExchangeNodeBase):
    """
    Generates Gcode______-
    o_List of point______-
    o_Name_______________-
    o_Speed______________-
    """

    title = 'ExportGcode'

    init_inputs = [
        NodeInputType('points'),
        NodeInputType('name'),
        NodeInputType('speed'),
    ]

    init_outputs = [
        NodeOutputType(),
    ]

    def update_event(self, inp=-1):
        points, filename, speed = self.get_inputs()
        with open(str(filename)+'.gcode', 'w') as file:
            for point in points:
                file.write('G1 X' + str(point.X()) + ' Y' + str(point.Y()) + ' Z' + str(point.Z()) + ' F' + str(speed) + '\n')


DataExchange_nodes = [
    ExportStep_Node,
    ImportStep_Node,
    ExportStl_Node,
    ImportStl_Node,
    ExportGcode_Node,
]


# ---------------------------------------------------------------------------------------------------------------------------------


# 
# Export
# 


export_nodes([
    *Gp_nodes,
    *BRepBuilderAPI_nodes,
    *BRepOffsetAPI_nodes,
    *BRepPrimAPI_nodes,
    *BRepAlgoAPI_nodes,
    *BRepFilletAPI_nodes,
    *Geom_nodes,
    *GeomAPI_nodes,
    *Shape_Analysis_nodes,
    *Display_nodes,
    *Tools_nodes,
    *DataExchange_nodes,
])
