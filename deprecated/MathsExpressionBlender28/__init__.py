# Author: Rich Sedman
# Description: Dynamic Maths Expresion node Blender Add-on
# Version: (0.99)
# Date: May 2018
################################################### History ######################################################
# 0.4  01/06/2018 : Fix problems in parse_expression (parse_expression v0.3)
# 0.41 02/06/2018 : Fix problem with pruning of group input nodes that are no longer part of the expression.
#                   (dynamic_maths_expression_node v0.41)
# 0.42 09/06/2018 : Support multiple expressions and improve automatic layout (dynamic_maths_expression_node)
# 0.49 11/06/2018 : Separate out node layout tools and implement simpler hierarchy layout
# 0.50 11/06/2018 : Support multi-expressions including naming with 'Name=expression' format.
# 0.51 15/06/2018 : Improve operator precedence in parse_expression (v0.4)
# 0.52 15/06/2018 : Fix minor bug in naming output sockets when multiple outputs added
# 0.61 05/02/2019 : Bring up to date for Blender 2.8 API changes
# 0.90 01/03/2019 : Implement Edit and tidy up placement of created node.
# 0.91 01/03/2019 : Remove unnecessary import of ShaderNodeCategory (no longer used)
# 0.99 04/03/2019 : Implement Edit mode from custom node within group
##################################################################################################################

bl_info = {  
 "name": "Dynamic Maths Expression",  
 "author": "Rich Sedman",  
 "version": (0, 99),  
 "blender": (2, 80, 0),  
 "location": "Node Editor > Add",  
 "description": "Provide an option to create a new group from a typed maths expression.",  
 "warning": "",  
 "wiki_url": "https://github.com/baldingwizard/Blender-Addons/wiki",  
 "tracker_url": "https://github.com/baldingwizard/Blender-Addons/issues",  
 "category": "Node"} 

import bpy

from .dynamic_maths_expression_node import DynamicMathsExpression_Operator, DynamicMathsExpressionEdit_Operator, DynamicMathsExpressionEditWithin_Operator, DynamicMathsExpressionNode

from nodeitems_utils import NodeItem, register_node_categories, unregister_node_categories

def menu_draw(self, context):
    self.layout.operator("node.node_dynamic_maths_expression", text='Maths Expression')
    
    # Edit is not required since we can now edit within the group itself via the custom node
    #self.layout.operator("node.node_dynamic_maths_expression_edit", text='Maths Expression(Edit)')

bpy.types.NODE_MT_add.append(menu_draw)
#TODO : Need to add it to Add/Group rather than Add

classes = ( DynamicMathsExpression_Operator, DynamicMathsExpressionEdit_Operator, DynamicMathsExpressionEditWithin_Operator, DynamicMathsExpressionNode)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()