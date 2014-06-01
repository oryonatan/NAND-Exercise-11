__author__ = 'larrath'

from SymbolTable import ScopeChain
import xml.dom.minidom as minidom

def encode(xml_data):
    scope = ScopeChain()
    scope_chain = []
    static_vars = []
    print (xml_data.toprettyxml())
    print("encode exit")
    exit()

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