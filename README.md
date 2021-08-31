# Pythonocc-nodes-for-Ryven
Pythonocc nodes for Ryven


Here a way to work on Pythonocc with a node editor, Ryven in that case.
To get it functional you will have to execute Ryven in an environment where pythonocc is installed.

**Install Ryven**: https://github.com/leon-thomm/Ryven

**Install Pythonocc** : https://github.com/tpaviot/pythonocc-core

You just have to import the `Nodes.py` file in Ryven, then all nodes are available under the right-click of the mouse.

Here a small example of a definition :
https://www.youtube.com/watch?v=lUNYstrfvmg
![exemple_tutogithub](https://user-images.githubusercontent.com/81742654/131111996-7d586497-ecb0-4908-9da7-b8fd9ba72055.jpg)
![exemple_tutogithub_1](https://user-images.githubusercontent.com/81742654/131112006-300cb113-ad9c-406c-9bd4-4ce6629f54ee.jpg)

You can load this project saved in this file : `demo_example.json`

It's just a beginning to explore the possibilities given by matching the two, I've just coded simple functions to see how it works and how it should be to perform complex operations.


# Contribute !
The nodes are of course open for contribution, as there are thousands of functions in OpenCascade and thousands of way to developp properly the nodes!

The functions yet implemented in the nodes.py file are :

`Gp_nodes = Pnt_Node, Dir_Node, Vec_Node, Ax2_Node, Pln_Node, Trsf_Node,`

`BRepPrimAPI_nodes = Box_Node, Sphere_Node, Cylinder_Node,`

`BRepAlgoAPI_nodes = Fuse_Node, Common_Node, Cut_Node,`

`BRepFilletAPI_nodes = fillet_Node,`

`Display_nodes =  display_Node,`

`Tools_nodes = List_Node, ExportStep_Node, ExportStl_Node,`

Each "nodes" family is a class with a color attributed. Node's name are nearly the same than in Pythonocc

To add a function from Pythonocc you have to generate a code as in the `add_function_box_example.py` file

