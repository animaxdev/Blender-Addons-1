# Author: Rich Sedman
# Description: Dynamic Maths Expresion node
# Version: (0.45)
# Date: May 2018
################################################### History ######################################################
# 0.4  01/06/2018 : Remove old redundant code
# 0.41 02/06/2018 : Fix pruning of group inputs that are no longer required
# 0.42 06/06/2018 : Start to support multiple expressions and improve auto-layout
# 0.43 11/06/2018 : Move node layout tools into a separate class
# 0.44 11/06/2018 : Prune inputs and outputs no longer required for multi-expressions
# 0.45 15/06/2018 : Fix allocation of name when adding multiple new outputs
##################################################################################################################


import bpy

from .parse_expression import Expression
from .node_tree_tools import NodeTreeTools

class DynamicMathsExpressionNode(bpy.types.NodeCustomGroup):

    bl_name='DynamicMathsExpression'
    bl_label='Dynamic Maths Expression'

    # Manage the node's sockets, adding additional ones when needed and removing those no longer required
    def __nodeinterface_setup__(self):
        print("Node interface setup")
        # No operators --> no inpout or output sockets
        #if self.inputSockets < 1:
        #self.node_tree.inputs.clear()
        #self.node_tree.outputs.clear()

        # Add the output socket
        if len(self.node_tree.outputs) < 1:
            self.node_tree.outputs.new("NodeSocketFloat", "Value")
        
        return

    # Manage the internal nodes to perform the chained operation - clear all the nodes and build from scratch each time.
    def __nodetree_setup__(self):
        print("Node Setup")
        # Remove all links and all nodes that aren't Group Input or Group Output
        self.node_tree.links.clear()
        for node in self.node_tree.nodes:
            if not node.name in ['Group Input','Group Output']:
                self.node_tree.nodes.remove(node)
            else:
                node.location = [0,0]

        # Start from Group Input and add nodes as required, chaining each new one to the previous level and the next input
        groupinput = self.node_tree.nodes['Group Input']
        previousnode = groupinput

        print("About to parse expression...")
        operations = Expression.parse_expression(self.expressionText)
        outputslot = 0
        while True:
            if operations[0] == ',':
                # Multiple expressions - assign the first one then continue with the next
                exprname = 'Value'
                expr = operations[1]
                if expr[0] == '=':
                    # In the form '<var>=<expression>' - use <var> as the name
                    if expr[1][0] == 'variable':
                        exprname = expr[1][1]
                        expr = expr[2]
                        
                if len(self.node_tree.outputs) < (outputslot+2):
                    self.node_tree.outputs.new("NodeSocketFloat", exprname)
                
                self.node_tree.outputs[outputslot].name = exprname;
                    
                self.build_nodes(expr, self.node_tree.nodes['Group Output'].inputs[outputslot], self.node_tree.nodes['Group Output'].location,0)
                operations = operations[2]
            else:
                # Single expression - process it and then exit

                exprname = 'Value'
                expr = operations
                if expr[0] == '=':
                    # In the form '<var>=<expression>' - use <var> as the name
                    if expr[1][0] == 'variable':
                        exprname = expr[1][1]
                        expr = expr[2]

                self.node_tree.outputs[outputslot].name = exprname;
                self.build_nodes(expr, self.node_tree.nodes['Group Output'].inputs[outputslot], self.node_tree.nodes['Group Output'].location,0)
                break
                
            outputslot += 1
        
        self.prune_group_inputs()
        self.prune_group_outputs()
        
        #for l in range(1,100):
        #    print("Arrange("+str(l)+")")
        #    NodeTreeTools.arrange_nodes(self.node_tree, l>2, True)
        NodeTreeTools.arrangeBasedOnHierarchy(self.node_tree)
        
    def build_nodes(self, nested_operations, to_output, output_location,depth):
        depth+=1

        print("Build Nodes")
        if len(nested_operations) == 0:
            return
        
        operation = nested_operations[0]
        
        print("Build Nodes "+str(nested_operations)+" : "+str(operation))
        
        if operation == 'variable':
            #....link to 'group input'
            variablename = nested_operations[1]
            
            if variablename in self.node_tree.nodes['Group Input'].outputs.keys():
                 self.node_tree.links.new(self.node_tree.nodes['Group Input'].outputs[variablename],to_output)
            else:
                # Add a new socket
                self.node_tree.inputs.new("NodeSocketFloat", variablename)
                self.node_tree.links.new(self.node_tree.nodes['Group Input'].outputs[-2],to_output)  # Add link to group input we just added (-1 is 'blank' socket, -2 is last 'real' socket)
        
        elif operation == 'value':
            #create new 'Value' node and link to to_output
            newnode = self.node_tree.nodes.new('ShaderNodeValue')
            print("Value = '"+str(nested_operations[1])+"'")
            newnode.outputs[0].default_value = float(nested_operations[1])
            self.node_tree.links.new(newnode.outputs[0],to_output)

        else:
            # create a new 'Maths' node
            newnode = self.node_tree.nodes.new('ShaderNodeMath')
            
            # set the operation
            if operation == '+':
                newnode.operation = "ADD"
            elif operation == '-':
                newnode.operation = "SUBTRACT"
            elif operation == '*':
                newnode.operation = "MULTIPLY"
            elif operation == '/':
                newnode.operation = "DIVIDE"
            elif operation == '**':
                newnode.operation = "POWER"
            elif operation == 'sin':
                newnode.operation = "SINE"
            elif operation == 'cos':
                newnode.operation = "COSINE"
            elif operation == 'tan':
                newnode.operation = "TANGENT"
            elif operation == 'asin':
                newnode.operation = "ARCSINE"
            elif operation == 'acos':
                newnode.operation = "ARCCOSINE"
            elif operation == 'atan':
                newnode.operation = "ARCTANGENT"
            elif operation == 'min':
                newnode.operation = "MINIMUM"
            elif operation == 'max':
                newnode.operation = "MAXIMUM"
            elif operation == '>':
                newnode.operation = "GREATER_THAN"
            elif operation == '<':
                newnode.operation = "LESS_THAN"
            elif operation == 'log':
                newnode.operation = "LOGARITHM"
            elif operation == 'round':
                newnode.operation = "ROUND"
            elif operation == 'mod':
                newnode.operation = "MODULO"
            elif operation == 'abs':
                newnode.operation = "ABSOLUTE"
            elif operation == ',':
                newnode.operation = "***Not yet implemented***"
            else:
                print("Unknown operation '"+ str(operation)+"'")
                newnode.operation = "Unknown"
            
            # link output to to_output
            self.node_tree.links.new(newnode.outputs[0],to_output)

            newlocation = output_location
            newlocation[0] -= 1/depth
            newnode.location = newlocation

            # Repeat for sub-nodes
            self.build_nodes(nested_operations[1], newnode.inputs[0], newlocation,depth)
            if len(nested_operations) > 2:
                newlocation[1]+=1/depth
                self.build_nodes(nested_operations[2], newnode.inputs[1], newlocation,depth)
                
    def prune_group_inputs(self):
        #run through the 'Group Input' sockets and remove any that are no longer connected
        for output in self.node_tree.nodes['Group Input'].outputs:
            if len(output.name) > 0 and len(output.links) == 0:
                print("Need to remove "+str(output))
                #self.node_tree.nodes['Group Input'].outputs.remove(output)  ### This doesn't appear to be working!!!!
                for input in self.node_tree.inputs:
                    if input.name == output.name:
                        self.node_tree.inputs.remove(input)
                        print("Removed "+input.name)
                
    def prune_group_outputs(self):
        #run through the 'Group Output' sockets and remove any that are no longer connected
        for input in self.node_tree.nodes['Group Output'].inputs:
            if len(input.name) > 0 and len(input.links) == 0:
                for output in self.node_tree.outputs:
                    if output.name == input.name:
                        self.node_tree.outputs.remove(output)
                        print("Removed "+output.name)
                
    # Expression has changed - update the nodes and links
    def update_expression(self, context):
        
        self.__nodeinterface_setup__()
        self.__nodetree_setup__()

    expressionText = bpy.props.StringProperty(name="Expression", update=update_expression)

    # Setup the node - setup the node tree and add the group Input and Output nodes
    def init(self, context):
        self.node_tree=bpy.data.node_groups.new(self.bl_name, 'ShaderNodeTree')
        if hasattr(self.node_tree, 'is_hidden'):
            self.node_tree.is_hidden=True
        self.node_tree.nodes.new('NodeGroupInput')
        self.node_tree.nodes.new('NodeGroupOutput') 

    # Draw the node components
    def draw_buttons(self, context, layout):
        row=layout.row()
        row.prop(self, 'expressionText', text='Expression')

    # Copy
    def copy(self, node):
        self.node_tree=node.node_tree.copy()

    # Free (when node is deleted)
    def free(self):
        bpy.data.node_groups.remove(self.node_tree, do_unlink=True)
