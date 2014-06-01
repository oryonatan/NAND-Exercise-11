__author__ = 'larrath'

from SymbolTable import ScopeChain
import xml.dom.minidom as minidom

def expect_label(xml_data, desired_value):
    if (xml_data.tagName.strip() != desired_value):
        raise Exception('Label should be ' + str(desired_value) + '; instead got ' + xml_data.tagName)

def expect_values(xml_data, desired_values):
    if (str(xml_data.firstChild.nodeValue).strip() not in desired_values):
        raise Exception('Label should be in' + str(desired_values) + '; instead got ' + xml_data.firstChild.nodeValue)

def encode(xml_data):
    expect_label(xml_data, 'class')

    # parsing new class
    scope = ScopeChain()
    main_nodes = list(xml_data.childNodes)

    compileClassDeclaration(xml_data, scope, '')
    print("encode exit")
    exit()

def compileClassDeclaration(xml_data, scope, buf):
    class_data = list(xml_data.childNodes)
    class_name = class_data[1].firstChild.nodeValue
    class_body = class_data[3]
    
    print('Recognized Class Declaration')
    print('\tClass name:' + str(class_name))
    print('\tCompiling class body')
    compileClassBody(class_body, scope, buf)

def compileClassBody(xml_data, scope, buf):
    expect_label(xml_data, 'subroutineDec')
    print('Recognized class body')
    
    while (xml_data.hasChildNodes()):
        print('body data length: ' + str(len(xml_data.childNodes)))
        current_top = xml_data.childNodes[0]
        print(current_top.firstChild.nodeValue)
        if (str(current_top.firstChild.nodeValue).strip() in ['constructor', 'function', 'method']):
            compileFunctionDeclaration(current_top.parentNode, scope, buf)
    
    for node in xml_data.childNodes:
        print node.tagName + ' : ' + str(node.firstChild.nodeValue)

def compileFunctionDeclaration(xml_data, scope, buf):
    expect_values(xml_data.firstChild, ['constructor', 'function', 'method'])
    print("Recognized function declaration")
    func_data = list(xml_data.childNodes)
    for node in func_data:
        print(node)
    
    function_declare_mode = func_data[0].firstChild.nodeValue.strip()
    function_return_type = func_data[1].firstChild.nodeValue.strip()
    function_name = func_data[2].firstChild.nodeValue.strip()
    function_args = func_data[4] # parse parameter list
    function_body = func_data[6] # parse function body
    print('Function data: (' + function_declare_mode + ') ' + function_return_type + ' ' + function_name)
    # TODO: function names are not added to scope, right?

    compileFunctionArguments(function_args, scope, buf)
    compileFunctionBody(function_body, scope, buf)

    # destroy the nodes we compiled
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()



def writePush(mem_segment, index):
    pass # TODO: writes a VM push command

def writePop(mem_segment, index):
    pass # TODO: writes a VM pop command

def writeArithmetic(expression_root):
    op = expression_root.data # TODO: actually need to get the entire expression here, so print the whole thing

    if (op.isdigit()): # if op is identifier, keyword or constant
        return 'push ' + op

    # if op is binary of the form op_1 x op_2, return writeArithmetic(op1) + writeArithmetic(op2) + x
    # if op is unary, return writeArithmetic(op1) + x
    # if op is a function call, do writeArithmetic on each parameter and then call the function

def writeLabel(label):
    pass # write a VM label command

def writeGoto(label):
    pass # write a VM goto command

def writeIf(label):
    pass # write a VM if-goto command

def writeCall(function_name, argument_count):
    pass # write a VM call command

def writeFunction(function_name, argument_count):
    pass # write a VM function (definition) command

def writeReturn():
    pass # write a VM return statement