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
    result = ''
    # parsing new class
    scope = ScopeChain()
    main_nodes = list(xml_data.childNodes)

    compileClassDeclaration(xml_data, scope, result)
    return result

def compileClassDeclaration(xml_data, scope, buf):
    class_data = list(xml_data.childNodes)
    class_name = class_data[1].firstChild.nodeValue
    
    print('Recognized Class Declaration')
    print('\tClass name:' + str(class_name))
    print('\tCompiling class body')
    class_data = class_data[3:] # discard previously handled elements

    while (class_data):
        operation = class_data[0].tagName
        if (operation == 'subroutineDec'):
            compileClassBody(class_data[0], scope, buf)
        elif (operation == 'classVarDec'):
            compileVarDeclaration(class_data[0], scope, buf)
        elif (operation == 'symbol' and class_data[0].firstChild.nodeValue.strip() == '}'):
            print 'Finished compiling class subroutines and variables'
        else:
            raise Exception('Unknown operation in class body')
        class_data.pop(0)
    return buf

def compileClassBody(xml_data, scope, buf):
    expect_label(xml_data, 'subroutineDec')
    print('Recognized class body')
    
    while (xml_data.hasChildNodes()):
        print('\tbody data length: ' + str(len(xml_data.childNodes)))
        current_top = xml_data.childNodes[0]
        command = str(current_top.firstChild.nodeValue).strip()
        if (command in ['constructor', 'function', 'method']):
            compileFunctionDeclaration(current_top.parentNode, scope, buf)
    
    # for node in xml_data.childNodes:
    #     print node.tagName + ' : ' + str(node.firstChild.nodeValue)
    return buf

def compileFunctionDeclaration(xml_data, scope, buf):
    expect_values(xml_data.firstChild, ['constructor', 'function', 'method'])
    print("Recognized function declaration")
    func_data = list(xml_data.childNodes)
    
    function_declare_mode = func_data[0].firstChild.nodeValue.strip()
    function_return_type = func_data[1].firstChild.nodeValue.strip()
    function_name = func_data[2].firstChild.nodeValue.strip()
    function_args = func_data[4] # parse parameter list
    function_body = func_data[6] # parse function body
    print('\tFunction data: (' + function_declare_mode + ') ' + function_return_type + ' ' + function_name)
    # TODO: function names are not added to scope, right?

    compileFunctionArguments(function_args, scope, buf)
    compileFunctionBody(function_body, scope, buf)

    # destroy the nodes we compiled
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileFunctionArguments(parameterList, scope, buf):
    scope.pushNewScope()
    expect_label(parameterList, 'parameterList')
    print('Compiling parameter list')
    params = list(parameterList.childNodes)
    if (len(params) == 1 and params[0].nodeValue == '\n'):
        print('\tFunction accepts zero arguments')
    else:
        print('\tFunction accepts ' + str(len(params) / 2) + ' arguments') # TODO: not accurate, since ',' also appears. Better to use a while loop.
        while (params):
            var_visibility = 'argument' # TODO: verify this; it should be defined as a local variable but accessed from ARG register
            var_type = params.pop(0).firstChild.nodeValue.strip()
            var_name = params.pop(0).firstChild.nodeValue.strip()
            if (params): # discard delimiter, if one exists (last entry has none)
                params.pop(0)
            scope.define(var_name, var_type, var_visibility)
            print('\tAdded variable __' + str(var_type) + ' ' + str(var_name) +'__ to local scope as function parameter')

    # destroy the nodes we compiled
    parameterList.parentNode.removeChild(parameterList)
    parameterList.unlink()
    return buf

def compileFunctionBody(body, scope, buf):
    print("Compiling function body")
    data = list(body.childNodes)
    data = data[1:-1]   # remove first and last elements ( '{' and '}' )
    # TODO: need to compile Variable Declaration and Statements, all using the same scope.
    while (data):
        action = data[0].tagName
        if (action == 'varDec'):
            compileVarDeclaration(data[0], scope, buf)
        elif (action == 'statements'):
            compileStatements(data[0], scope, buf)
        else:
            raise Exception('Unknown operation in function body')
        data.pop(0)
    return buf
    
def compileVarDeclaration(declaration, scope, buf):
    try:
        expect_label(declaration, 'varDec')
    except Exception:
        expect_label(declaration, 'classVarDec')
    
    data = list(declaration.childNodes)
    # TODO: implement this; will be easier to test on a more complex source file
    print ('Compiling variable declaration section')
    var_visibility = data.pop(0).firstChild.nodeValue.strip()
    var_type = data.pop(0).firstChild.nodeValue.strip()

    while (data):
        var_name = data.pop(0).firstChild.nodeValue.strip()
        scope.define(var_name, var_type, var_visibility)
        print('\tAdded variable: ' + str(var_visibility) + ' ' + str(var_type) + ' ' + str(var_name))
        data.pop(0) # discard delimiter
    return buf
    

def compileStatements(xml_data, scope, buf):
    expect_label(xml_data, 'statements')
    data = list(xml_data.childNodes)
    print ('Compiling statement container')
    for statement in data:
        statement_type = statement.tagName

        if (statement_type == 'letStatement'):
            compileLetStatement(statement, scope, buf)
        elif (statement_type == 'ifStatement'):
            compileIfStatement(statement, scope, buf)
        elif (statement_type == 'whileStatement'):
            compileWhileStatement(statement, scope, buf)
        elif (statement_type == 'doStatement'):
            compileDoStatement(statement, scope, buf)
        elif (statement_type == 'returnStatement'):
            compileReturnStatement(statement, scope, buf)
        else:
            raise Exception('Unknown statement type')
    return buf


def compileLetStatement(xml_data, scope, buf):
    expect_label(xml_data, 'letStatement')
    print('\tCompiling let statement')
    data = list(xml_data.childNodes)
    var_name = data[1]
    
    if (data[2].firstChild.nodeValue.strip() == '['):   # accessing array element
        print('\t\tAccessing array')
        array_exp = data[3]
        rvalue_exp = data[6]

        compileExpression(array_exp, scope, buf)
    else:
        rvalue_exp = data[3]

    compileExpression(rvalue_exp, scope, buf)

    # remove nodes for garbage collection
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileIfStatement(xml_data, scope, buf):
    # TODO: do we have Block-level scopes? If so, we need to create a new scope here and discard it when we return.
    expect_label(xml_data, 'ifStatement')
    print('\tCompiling if statement')
    data = list(xml_data.childNodes)
    cond_exp = data[2]
    
    statement_body = data[5]

    if (len(data) == 11):
        print('If block with Else statement')
        else_statement = data[9]
        # TODO: might need to change the internal ordering of some function calls here
        compileExpression(cond_exp, scope, buf)
        compileStatements(statement_body, scope, buf)
        compileStatements(else_statement, scope, buf)
    elif (len(data) == 7):
        print('If block without an Else statement')
        # TODO: might need to change the internal ordering of some function calls here
        compileExpression(cond_exp, scope, buf)
        compileStatements(statement_body, scope, buf)
    else:
        raise Exception('bad node count in if statement')

    # remove nodes for garbage collection
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileWhileStatement(xml_data, scope, buf):
    # TODO: do we have Block-level scopes? If so, we need to create a new scope here and discard it when we return.
    expect_label(xml_data, 'whileStatement')
    print('\tCompiling while statement')
    data = list(xml_data.childNodes)
    
    cond_exp = data[2]
    statement_body = data[4]
    
    compileExpression(cond_exp, scope, buf)
    compileStatements(statement_body, scope, buf)

    # remove nodes for garbage collection
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileDoStatement(xml_data, scope, buf):
    expect_label(xml_data, 'doStatement')
    data = list(xml_data.childNodes)
    print('\tCompiling do statement')
    if (data[2].firstChild.nodeValue.strip() == '.'):   # do Class.Function( params ) ;
        # TODO: might need to 
        function_name = str(data[1].firstChild.nodeValue.strip()) + '.' + str(data[3].firstChild.nodeValue.strip())
        params = data[5]
    
    else:
        function_name = data[1].firstChild.nodeValue.strip()
        params = data[3]
    
    # TODO: there might be another implementation detail I am missing here regarding functions' owning classes
    for arg in params.childNodes:
        buf = str(buf) + str(compileExpression(arg, scope, buf))
    #     while (arg.hasChildNodes()):
    #         arg = arg.firstChild

    #     if (scope.kindOf(arg.nodeValue.strip())):
    #         register = str(scope.kindOf(arg.firstChild.nodeValue))
    #         index = str(scope.indexOf(arg.firstChild.nodeValue))
    #     # TODO: missing implementation for function calls
    #     else:
    #         register = 'constant'
    #         index = arg.nodeValue.strip()
    #     buf += 'push ' + register + ' ' +  index + '\n'
    # buf += 'call ' + str(function_name)

    return buf


def compileReturnStatement(xml_data, scope, buf):
    expect_label(xml_data, 'returnStatement')
    data = list(xml_data.childNodes)
    print("\tCompiling return statement")
    if (data[1].tagName == 'expression'):
        print("\t\tReturn statement returns value")
        compileExpression(data[1], scope, buf)
    else:
        print("\t\tReturn statement has no value")
        pass    # TODO: return 0 or something of that sort
    scope.leaveScope()
    return buf

def compileExpression(xml_data, scope, buf):
    expect_label(xml_data, 'expression')
    terms = list(xml_data.childNodes)
    
    print('\tCompiling Expression')
    buf = traversePostOrder(xml_data, buf)
    # TODO: need something more sophisticated here. Also, should probably write the vm code directly at this point.
    #print(terms)

    #     while (arg.hasChildNodes()):
    #         arg = arg.firstChild

    #     if (scope.kindOf(arg.nodeValue.strip())):
    #         register = str(scope.kindOf(arg.firstChild.nodeValue))
    #         index = str(scope.indexOf(arg.firstChild.nodeValue))
    #     # TODO: missing implementation for function calls
    #     else:
    #         register = 'constant'
    #         index = arg.nodeValue.strip()
    #     buf += 'push ' + register + ' ' +  index + '\n'
    # buf += 'call ' + str(function_name)
    print(buf)
    return buf

def traversePostOrder(root, buf):
    child_nodes = list(root.childNodes)
    if (len(child_nodes) == 3): # term_1 op term_2
        left_term = traversePostOrder(child_nodes[0], buf)
        right_term = traversePostOrder(child_nodes[2], buf)
        op = traversePostOrder(child_nodes[1], buf)
        return str(left_term) + str(right_term) + str(op)

    elif (len(child_nodes) == 2): # op term
        op = traversePostOrder(child_nodes[0])
        term = traversePostOrder(child_nodes[1])
        return str(term) + str(op)

    elif (len(child_nodes) == 1): # term
        node = child_nodes[0]
        label = node.tagName
        if (label == 'integerConstant'):
            print(node.firstChild.nodeValue.strip())
            return node.firstChild.nodeValue.strip()
        elif (label == 'stringConstant'):
            pass    # TODO: create a string constant
        elif (label == 'keywordConstant'):
            print(node.firstChild.nodeValue.strip())    # TODO: create manual representation
            return node.firstChild.nodeValue.strip()
        elif (label == 'identifier'):
            pass
        elif (label == 'symbol'):
            pass
        else:
            raise NotImplementedError




        # print(node.tagName)
        # if (child_nodes[0].hasChildNodes()):
        #     for node in child_nodes[0].childNodes:
        #         traversePostOrder(node, buf)
        # else:
        #     op = child_nodes[0].nodeValue.strip()
        #     if (op in ['(', ')']):
        #         pass
        #     else:
        #         return str(op) + '\n'
    
    # if (root.hasChildNodes()):
    #     temp = ''
    #     for child in root.childNodes:
    #         org_child = child
    #         while (child.nextSibling):
    #             while (not child.nodeValue):
    #                 child = child.firstChild
                
    #             temp = str(temp) + str(traversePostOrder(child, buf))
    #             child = org_child.nextSibling
        
    #     return str(buf) + str(temp)
    # else:
    #     # exp.append(root.nodeValue.strip())
    #     return 'push ' + root.nodeValue.strip() + ' \n'




# ---------------------- VM code generation -------------------------
def writePush(mem_segment, index, buf):
    pass # TODO: writes a VM push command

def writePop(mem_segment, index, buf):
    pass # TODO: writes a VM pop command

def writeArithmetic(expression_root, buf):
    op = expression_root.data # TODO: actually need to get the entire expression here, so print the whole thing

    if (op.isdigit()): # if op is identifier, keyword or constant
        return 'push ' + op

    # if op is binary of the form op_1 x op_2, return writeArithmetic(op1) + writeArithmetic(op2) + x
    # if op is unary, return writeArithmetic(op1) + x
    # if op is a function call, do writeArithmetic on each parameter and then call the function

def writeLabel(label, buf):
    pass # write a VM label command

def writeGoto(label, buf):
    pass # write a VM goto command

def writeIf(label, buf):
    pass # write a VM if-goto command

def writeCall(function_name, argument_count, buf):
    pass # write a VM call command

def writeFunction(function_name, argument_count, buf):
    pass # write a VM function (definition) command

def writeReturn(buf):
    pass # write a VM return statement