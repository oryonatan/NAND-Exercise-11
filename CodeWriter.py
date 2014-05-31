__author__ = 'larrath'

from SymbolTable import ScopeChain

def encode(xml_data):
    scope = ScopeChain()
    scope_chain = []
    static_vars = []

def writePush(mem_segment, index):
    pass # TODO: writes a VM push command

def writePop(mem_segment, index):
    pass # TODO: writes a VM pop command

def writeArithmetic(command):
    # TODO: command can be binary or unary
    pass # write a VM arithmetic command

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