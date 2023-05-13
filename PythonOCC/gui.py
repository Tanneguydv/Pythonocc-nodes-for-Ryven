from ryven.gui_env import *

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QLineEdit


# 
# General Base Classes
# 


class PythonOCCNodeGuiBase(NodeGUI):

    input_widget_classes = {
        'DataSmall': inp_widgets.Builder.evaled_line_edit(size='s', resizing=True),
    }
    
    @staticmethod
    def builder():
        return GuiBuilder


class GuiBuilder:

    @staticmethod
    def attach_input_widgets(input_widgets):
        """
        A decorator which automatically attaches input widgets specified
        in the input_widgets list to the gui of the node.
        """
        
        # make sure all input widget names provided are valid
        assert all([
            wn in PythonOCCNodeGuiBase.input_widget_classes 
            for wn in input_widgets if wn is not None
        ])

        def decorator(cls):
            inp_widgets = {
                i: {'name': widget_name, 'pos': 'besides'}
                for i, widget_name in enumerate(input_widgets)
                if widget_name is not None
            }
            if not issubclass(cls.GUI, PythonOCCNodeGuiBase):
                # override GUI class
                class AutoInputWidgets_NodeGui(PythonOCCNodeGuiBase):
                    init_input_widgets = inp_widgets
                cls.GUI = AutoInputWidgets_NodeGui
            else:
                # add input widgets to existing GUI class
                cls.GUI.init_input_widgets = inp_widgets
            return cls
        
        return decorator


# 
# Specific Node GUIs
# 


class PyOCCBase_DynamicInputsGui(PythonOCCNodeGuiBase):
    def __init__(self, params):
        super().__init__(params)

        self.num_inputs = 0
        self.actions['add input'] = {'method': self.add_operand_input}
        self.actions['remove input'] = {}
        
    def initialized(self):
        # if the node was loaded from a state, catch up with 
        # the number of inputs
        self.num_inputs = len(self.node.inputs)
        # the actions are restrored automatically

        self.actions['remove input'] = {
            i: {
                'method': self.remove_operand_input,
                'data': i,
            } for i in range(self.num_inputs)
        }

    def add_operand_input(self):
        self.node.add_operand_input()
        
        # update actions
        new_index = self.num_inputs
        self.actions['remove input'][new_index] = {
            'method': self.remove_operand_input,
            'data': new_index,
        }
        self.num_inputs += 1
    
    def remove_operand_input(self, index):
        self.node.remove_operand_input(index)
        del self.actions['remove input'][self.num_inputs-1]
        self.num_inputs -= 1


class GpNodeGui(PythonOCCNodeGuiBase):
    color = '#5e0a91'


class BrepBuilderAPINodeGui(PythonOCCNodeGuiBase):
    color = '#DAA520'


class BrepOffsetAPINodeGui(PythonOCCNodeGuiBase):
    color = '#aabb44'


class BrepPrimAPINodeBase(PythonOCCNodeGuiBase):
    color = '#aabb44'


class BrepAlgoAPINodeGui(PythonOCCNodeGuiBase):
    color = '#ab0c36'


class BrepFilletAPINodeGui(PythonOCCNodeGuiBase):
    color = '#e0149c'


class GeomNodeGui(PythonOCCNodeGuiBase):
    color = '#c91604'


class GeomAPINodeGui(PythonOCCNodeGuiBase):
    color = '#ff4633'


class TopExplorerGui(PythonOCCNodeGuiBase):
    color = '#FF00FF'


class BoundingBoxGui(PythonOCCNodeGuiBase):
    color = '#FF00FF'


class DisplayNodeGui(PythonOCCNodeGuiBase):
    color = '#3355dd'


class ListGui(PyOCCBase_DynamicInputsGui):
    color = '#000000'


class ListLengthGui(PythonOCCNodeGuiBase):
    color = '#000000'


class FlattenListGui(PythonOCCNodeGuiBase):
    color = '#000000'


class ListItemGui(PythonOCCNodeGuiBase):
    color = '#000000'


class RepeatDataGui(PythonOCCNodeGuiBase):
    color = '#000000'


class SerieGui(PythonOCCNodeGuiBase):
    color = '#000000'


class ShiftListGui(PythonOCCNodeGuiBase):
    color = '#000000'


class DataExchangeNodeGui(PythonOCCNodeGuiBase):
    color = '#6b6767'


# 
# inport file node
# 


class ImportFileNode_MainWidget(NodeMainWidget, QLineEdit):

    value_changed = Signal(object)

    def __init__(self, params):
        NodeMainWidget.__init__(self, params)
        QLineEdit.__init__(self)

        # self.setFixedWidth(80)
        # self.setMinimumWidth(80)
        self.resize(120, 31)
        self.editingFinished.connect(self.editing_finished)

    def editing_finished(self):
        # self.node.update()
        self.value_changed.emit(self.get_val())

    def get_val(self):
        val = None
        try:
            val = eval(self.text())
        except Exception as e:
            val = self.text()
        return val

    def get_state(self):
        data = {'text': self.text()}
        return data

    def set_state(self, data):
        self.setText(data['text'])


class ImportFileNode_Gui(NodeGUI):
    main_widget_class = ImportFileNode_MainWidget
    main_widget_pos = 'between ports'


# ---------------------------------------------------------------------------------------------------------------------------------


# 
# Export
# 


export_guis([
    PythonOCCNodeGuiBase,
    PyOCCBase_DynamicInputsGui,
    GuiBuilder,

    GpNodeGui,
    BrepBuilderAPINodeGui,
    BrepOffsetAPINodeGui,
    BrepPrimAPINodeBase,
    BrepAlgoAPINodeGui,
    BrepFilletAPINodeGui,
    GeomNodeGui,
    GeomAPINodeGui,
    TopExplorerGui,
    BoundingBoxGui,
    DisplayNodeGui,
    ListGui,
    ListLengthGui,
    FlattenListGui,
    ListItemGui,
    RepeatDataGui,
    SerieGui,
    ShiftListGui,
    DataExchangeNodeGui,

    ImportFileNode_Gui,
])