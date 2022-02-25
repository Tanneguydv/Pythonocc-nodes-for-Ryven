class BrepPrimAPINodeBase(PythonOCCNodeBase):		# The parent class of the box
    color = '#aabb44'								# The color attributed to the parent class


class Box_Node(BrepPrimAPINodeBase):		# explicit class name(parent class name)
    """
    Generates box_________-
    o_Width_______________-
    o_Length______________-					#the text that will appear when your mouse will stay on the node in Ryven
    o_Height______________-					#it indicates what inputs are expected
    """
    init_inputs = [
        NodeInputBP(dtype=dtypes.Data(size='s')),		# number of inputs following what your function needs
        NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(dtype=dtypes.Data(size='s')),
    ]

    init_outputs = [
        NodeOutputBP(),						# output of the node
    ]

    title = 'box'							# the title name of your node

    def apply_op(self, elements: list):
        width = elements[0]					# your inputs
        length = elements[1]
        height = elements[2]
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox			# import of the method
        from OCC.Core.gp import gp_Pnt
        box = BRepPrimAPI_MakeBox(gp_Pnt(), width, length, height).Shape()			# the function to get a result

        return box					# the output of the node


BRepPrimAPI_nodes = [			# add the node to the list if its family
    Box_Node,
]


export_nodes(
    *BRepPrimAPI_nodes,			# specified the family nodes to export and to make available in Ryven
)
