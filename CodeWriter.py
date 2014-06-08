__author__ = 'larrath'

from SymbolTable import ScopeChain

global label_count
global marker

def expect_label(xml_data, desired_value):
    if (xml_data.nodeName.strip() != desired_value):
        raise Exception('Label should be ' + str(desired_value) + '; instead got ' + xml_data.nodeName)

def expect_values(xml_data, desired_values):
    if (str(xml_data.firstChild.nodeValue).strip() not in desired_values):
        raise Exception('Label should be in' + str(desired_values) + '; instead got ' + xml_data.firstChild.nodeValue) 

def set_marker(tag=''):
    global label_count
    global marker
    if (tag == '' or tag is None):
        marker = ''
    else:
        marker = str(tag) + str(label_count)
        label_count += 1

def get_marker():
    global marker
    if (len(marker) > 0):
        old_mark = marker
        marker = ''
        return old_mark + '\n'

    return ''


def encode(xml_data):
    expect_label(xml_data, 'class')
    global label_count
    label_count = 0
    set_marker(None)

    # parsing new class
    scope = ScopeChain()

    result = compileClassDeclaration(xml_data, scope)
    return result

def compileClassDeclaration(xml_data, scope):
    class_data = list(xml_data.childNodes)
    class_name = str(class_data[1].firstChild.nodeValue).strip()
    scope.setClassName(class_name)
    buf = ''

    class_data = class_data[3:] # discard previously handled elements

    # Scan all function declarations into scope before compilation begins
    func_declarations = xml_data
    for func_root in func_declarations.childNodes:
        if (func_root.nodeName == 'subroutineDec'):
            func_data = func_root.childNodes
            func_visibility = str(func_data[0].firstChild.nodeValue).strip()
            func_name = str(func_data[2].firstChild.nodeValue).strip()
            scope.defineFunction(func_name, func_visibility, class_name)


    while (class_data):
        operation = class_data[0].tagName
        if (operation == 'subroutineDec'):
            buf += compileClassBody(class_data[0], scope)
        elif (operation == 'classVarDec'):
            compileClassVarDeclaration(class_data[0], scope)
        elif (operation == 'symbol' and class_data[0].firstChild.nodeValue.strip() == '}'):
            pass
        else:
            raise Exception('Unknown operation in class body')

        class_data.pop(0)

    return buf

def compileClassBody(xml_data, scope):
    expect_label(xml_data, 'subroutineDec')

    buf = ''

    while (xml_data.hasChildNodes()):
        current_top = xml_data.childNodes[0]
        command = str(current_top.firstChild.nodeValue).strip()
        if (command in ['constructor', 'function', 'method']):
            buf += compileFunctionDeclaration(current_top.parentNode, scope)

    return buf

def compileFunctionDeclaration(xml_data, scope):
    expect_values(xml_data.firstChild, ['constructor', 'function', 'method'])
    
    func_data = list(xml_data.childNodes)
    buf = ''
    
    function_declare_mode = func_data[0].firstChild.nodeValue.strip()
    function_return_type = func_data[1].firstChild.nodeValue.strip()
    function_name = func_data[2].firstChild.nodeValue.strip()
    arg_count = compileFunctionArguments(func_data[4], scope, function_declare_mode)
    function_body, field_count = compileFunctionBody(func_data[6], scope, function_declare_mode)

    scope.defineFunction(function_name, function_declare_mode, scope.getClassName())

    buf += 'function ' + str(scope.getClassName()) + '.' + function_name + ' ' + str(field_count) + '\n'

    if (function_declare_mode == 'constructor'):
        buf += 'push constant ' + str(scope.varCount('field')) + '\n' + 'call Memory.alloc 1\n' + 'pop pointer 0\n'
    elif (function_declare_mode == 'method'):
        buf += 'push argument 0\n' + 'pop pointer 0\n'

    elif (function_declare_mode == 'function'):
        pass
    else:
        raise NotImplementedError

    buf += function_body
    # destroy the nodes we compiled

    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileFunctionArguments(parameterList, scope, mode):
    scope.pushNewScope()
    expect_label(parameterList, 'parameterList')

    if (mode == 'method'):
        scope.define('placeholder', 'NoType', 'argument')

    params = list(parameterList.childNodes)
    count = 0
    if (len(params) == 1 and params[0].nodeValue == '\n'):
        return count

    while (params):
        count += 1

        var_type = params.pop(0).firstChild.nodeValue.strip()
        var_name = params.pop(0).firstChild.nodeValue.strip()
        scope.define(var_name, var_type, 'argument')

        if (params): # discard delimiter, if one exists (last entry has none)
            params.pop(0)


    # destroy the nodes we compiled
    parameterList.parentNode.removeChild(parameterList)
    parameterList.unlink()
    return count

def compileFunctionBody(body, scope, mode='function'):
    data = list(body.childNodes)
    data = data[1:-1]   # remove first and last elements ( '{' and '}' )
    statements = ''
    args = 0
    while (data):
        action = data[0].tagName
        if (action == 'varDec'):
            args += compileVarDeclaration(data[0], scope, mode)
        elif (action == 'statements'):
            statements = str(compileStatements(data[0], scope, mode))
        else:
            raise Exception('Unknown operation in function body')
        data.pop(0)

    return statements, str(args)
    
def compileVarDeclaration(declaration, scope, mode='function'):
    expect_label(declaration, 'varDec')

    var_count = 0
    data = list(declaration.childNodes)

    declaration_kind = data.pop(0).firstChild.nodeValue.strip()
    var_type = data.pop(0).firstChild.nodeValue.strip()

    while (data):
        var_name = data.pop(0).firstChild.nodeValue.strip()
        scope.define(var_name, var_type, declaration_kind)
        var_count += 1
        data.pop(0) # discard delimiter

    # Variable declarations do not generate code. It's enough to update the scope with data.
    return var_count

def compileClassVarDeclaration(declaration, scope, mode='function'):
    expect_label(declaration, 'classVarDec')

    var_count = 0
    data = list(declaration.childNodes)

    declaration_kind = data.pop(0).firstChild.nodeValue.strip()
    var_type = data.pop(0).firstChild.nodeValue.strip()

    while (data):
        var_name = data.pop(0).firstChild.nodeValue.strip()
        scope.define(var_name, var_type, declaration_kind)
        var_count += 1
        data.pop(0) # discard delimiter

    # Variable declarations do not generate code. It's enough to update the scope with data.
    return var_count

def compileStatements(xml_data, scope, mode='function'):
    expect_label(xml_data, 'statements')
    data = list(xml_data.childNodes)
    buf = ''
    
    for statement in data:
        statement_type = statement.tagName

        if (statement_type == 'letStatement'):
            buf += compileLetStatement(statement, scope, mode)
        elif (statement_type == 'ifStatement'):
            buf += compileIfStatement(statement, scope, mode)
        elif (statement_type == 'whileStatement'):
            buf += compileWhileStatement(statement, scope, mode)
        elif (statement_type == 'doStatement'):
            buf += compileDoStatement(statement, scope, mode)
        elif (statement_type == 'returnStatement'):
            buf += compileReturnStatement(statement, scope, mode)
        elif (statement_type == 'symbol' and str(statement.firstChild.nodeValue) == '}'):
            return buf
        else:
            raise Exception('Unknown statement type')
    return buf


def compileLetStatement(xml_data, scope, mode):
    expect_label(xml_data, 'letStatement')

    data = list(xml_data.childNodes)
    var_name = str(data[1].firstChild.nodeValue).strip()
    assign_to_array = (str(data[2].firstChild.nodeValue).strip() == '[')

    var_full_name = str(scope.kindOf(var_name)) + ' ' + str(scope.indexOf(var_name))
    buf = ''

    if (assign_to_array):
        rvalue_exp = data[6]
        arr_exp = data[3]
        # seek to position in array
        buf += compileExpression(arr_exp, scope, mode)
        buf += 'push ' + var_full_name + '\n' + 'add\n'

        # obtain value from rvalue expression
        buf += compileExpression(rvalue_exp, scope, mode)

        # assign value into position in array
        buf += 'pop temp 0\n' + 'pop pointer 1\n' + 'push temp 0\n' + 'pop that 0\n'
    else:
        rvalue_exp = data[3]
        buf += compileExpression(rvalue_exp, scope, mode)
        buf += 'pop ' + var_full_name + '\n'

    buf += get_marker()

    # remove nodes for garbage collection
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileIfStatement(xml_data, scope, mode):
    expect_label(xml_data, 'ifStatement')
    data = list(xml_data.childNodes)

    cond_exp = data[2]
    buf = ''
    statement_body = data[5]

    if (len(data) == 11):   # If statement with Else statement
        else_statement = data[9]
        # Evaluate condition
        buf += compileExpression(cond_exp, scope, mode)

        # Jump instruction if condition is true
        set_marker('IF-TRUE')
        true_label = str(get_marker())
        buf += 'if-goto ' + true_label

        # Jump instruction if false
        set_marker('IF-FALSE')
        false_label = str(get_marker())
        buf += 'goto ' + false_label

        # If block body
        buf += 'label ' + true_label

        empty_if_body = (statement_body.firstChild.nodeValue == '\n')
        if (not empty_if_body):
            buf += compileStatements(statement_body, scope, mode)

        # Jump to termination of If block body (skip Else instructions)
        set_marker('IF-EXIT')
        exit_label = str(get_marker())
        buf += 'goto ' + exit_label

        # Else block body
        buf += 'label ' + false_label
        empty_else_body = (else_statement.firstChild.nodeValue == '\n')
        if (not empty_else_body):
            buf += compileStatements(else_statement, scope, mode)

        # Termination of If body
        buf += 'label ' + exit_label

    elif (len(data) == 7):  # If statement without an Else statement
        # Evaluate condition
        buf += compileExpression(cond_exp, scope, mode)

        # Jump instruction if condition is true
        set_marker('IF-TRUE')
        true_label = str(get_marker())
        buf += 'if-goto ' + true_label

        # Jump instruction if false
        set_marker('IF-FALSE')
        false_label = str(get_marker())
        buf += 'goto ' + false_label

        # If block body
        buf += 'label ' + true_label
        empty_if_body = (statement_body.firstChild.nodeValue == '\n')
        if (not empty_if_body):
            buf += compileStatements(statement_body, scope, mode)

        # Termination of If body
        buf += 'label ' + false_label

    else:
        print('====bad node count in if statement====')
        raise NotImplementedError

    # remove nodes for garbage collection
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileWhileStatement(xml_data, scope, mode):
    expect_label(xml_data, 'whileStatement')

    buf = ''
    data = list(xml_data.childNodes)

    cond_exp = data[2]
    statement_body = data[5]
    empty_body = False

    if (str(statement_body.firstChild.nodeValue).strip() == '}' or (statement_body.firstChild.nodeValue) == '\n'):
        empty_body = True

    # Set label for condition evaluation
    set_marker('WHILE_COND')
    cond_marker = get_marker()
    buf += 'label ' + cond_marker
    buf += compileExpression(cond_exp, scope, mode)
    buf += 'not\n'

    # Set loop exit point and create jump instruction
    set_marker('WHILE_END')
    end_marker = get_marker()
    buf += 'if-goto ' + end_marker

    # Perform iteration
    if (not empty_body):
        buf += compileStatements(statement_body, scope)
    buf += 'goto ' + cond_marker

    # Set finish point
    buf += 'label ' + end_marker

    # remove nodes for garbage collection
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileDoStatement(xml_data, scope, mode):
    expect_label(xml_data, 'doStatement')
    data = list(xml_data.childNodes)
    buf = ''
    pushed = False
    params_count = 0

    if (data[2].firstChild.nodeValue.strip() == '.'):   # do Class.Function( params ) or do Obj.Method( params )
        class_name, called_from_object = objectOrClass(data[1], scope)

        if (called_from_object):
            obj_name = str(data[1].firstChild.nodeValue).strip()
            params_count += 1
            buf += 'push ' + str(scope.kindOf(obj_name)) + ' ' + str(scope.indexOf(obj_name)) + '\n'

        function_name = str(class_name) + '.' + str(data[3].firstChild.nodeValue.strip())
        params = data[5]
        function_type = scope.getFunctionData(str(data[3].firstChild.nodeValue.strip()), class_name)

    else:   # do func ( params )
        function_name = scope.getClassName() + '.' + str(data[1].firstChild.nodeValue).strip()
        params = data[3]
        function_type = scope.getFunctionData(str(data[1].firstChild.nodeValue).strip(), scope.getClassName())
        if (function_type is not None and function_type[1] == 'method'):
            buf += 'push pointer 0\n'
            params_count += 1
            pushed = True

    for arg in params.childNodes:
        if (str(arg.nodeValue) == '\n'):
            break
        if (str(arg.firstChild.nodeValue).strip() == ','):
            continue
        buf += str(compileExpression(arg, scope, mode))
        params_count += 1

    if (not pushed and function_type is not None and function_type[1] == 'method'):
        buf += 'push pointer 0\n'
        params_count += 1

    buf += 'call ' + function_name + ' ' + str(params_count) + '\n' + 'pop temp 0\n'

    return buf


def compileReturnStatement(xml_data, scope, mode):
    expect_label(xml_data, 'returnStatement')
    data = list(xml_data.childNodes)
    buf = ''
    
    if (data[1].tagName == 'expression'):
        buf += compileExpression(data[1], scope, mode)
    else:
        buf += 'push constant 0\n'

    return buf + 'return\n'

def compileExpression(xml_data, scope, mode='function'):
    expect_label(xml_data, 'expression')

    terms = list(xml_data.childNodes)

    if (len(terms) == 1): # expression is a constant, a nested expression, unary operation or function call
        return str(extractTerm(terms[0], scope, mode))

    elif (len(terms) == 3): # expression is (term op term)
        left_term = extractTerm(terms[0], scope, mode)
        operation = handleBinaryOpSymbol(str(terms[1].firstChild.nodeValue).strip(), terms[1], scope)
        right_term = extractTerm(terms[2], scope, mode)
        return str(left_term) + str(right_term) + str(operation)

    elif (len(terms) % 2 == 1): # term (op term)* with multiple repititions
        parsing_term = True

        term_list = []
        op_list = []
        buf = ''

        while (len(terms) > 0):
            if (parsing_term):
                node = terms.pop(0)
                term_list.append(extractTerm(node, scope, mode))
                parsing_term = False
            else:
                node = terms.pop(0)
                op_list.append(handleBinaryOpSymbol(str(node.firstChild.nodeValue).strip(), None, scope))
                parsing_term = True

        buf += term_list.pop(0)
        for (term, op) in zip(term_list, op_list):
            buf += term
            buf += op

        return buf


    raise Exception('Cannot recognize expression')


def extractTerm(root, scope, mode='function'):
    expect_label(root, 'term')
    term = root.firstChild
    label = term.nodeName

    if (label == 'keyword'):    # generate constant value value
        return keywordConstant(str(term.firstChild.nodeValue).strip())

    elif (label == 'integerConstant'):  # constant number
        return 'push constant ' + str(term.firstChild.nodeValue).strip() + '\n'

    elif (label == 'stringConstant'):   # generate string
        return stringConstant(str(term.firstChild.nodeValue)[1:-1])

    elif (label == 'identifier'):       # load variable from scope
        siblings = list(term.parentNode.childNodes)
        buf = ''
        param_count = 0
        if (len(siblings) > 4):
            if (str(siblings[1].firstChild.nodeValue).strip() == '.'): # Class.Function(expressionList);
                class_name, is_method = objectOrClass(siblings[0], scope)
                func_name = str(siblings[2].firstChild.nodeValue).strip()

                if (is_method):
                    obj_name = str(siblings[0].firstChild.nodeValue).strip()
                    param_count += 1
                    buf += 'push ' + str(scope.kindOf(obj_name)) + ' ' + str(scope.indexOf(obj_name)) + '\n'

                for param in siblings[4].childNodes:
                    if (param.nodeValue == '\n'):   # empty parameter list
                        break
                    if (param.nodeName == 'symbol' and str(param.firstChild.nodeValue).strip() == ','):
                        continue
                    param_count += 1
                    buf += str(compileExpression(param, scope, mode))

                buf += 'call ' + str(class_name) + '.' + str(func_name) + ' ' + str(param_count) + '\n'
                return buf

        elif (term.nextSibling is not None and term.nextSibling.nodeName == 'symbol'):
            if (str(term.nextSibling.firstChild.nodeValue).strip() == '['):    # array access
                arr_name = str(term.firstChild.nodeValue).strip()
                buf += compileExpression(term.nextSibling.nextSibling, scope)
                buf += 'push ' + str(scope.kindOf(arr_name)) + ' ' + str(scope.indexOf(arr_name)) + '\n'
                buf += 'add\n'
                buf += 'pop pointer 1\n' + 'push that 0\n'
                return buf

            elif (str(term.nextSibling.firstChild.nodeValue).strip() == '('):  # implicit function invocation
                func_data = scope.getFunctionData(str(term.firstChild.nodeValue).strip(), scope.getClassName())
                func_name = func_data[0]
                func_type = func_data[1]

                if (func_type == 'method'):
                    buf += 'push pointer 0\n'
                    param_count += 1

                params = term.nextSibling.nextSibling
                for arg in params.childNodes:
                    if (arg.nodeValue == '\n'): # empty function call
                        break
                    if (arg.nodeName == 'symbol'):
                        continue
                    buf += compileExpression(arg, scope, mode)
                    param_count += 1

                buf += 'call ' + str(scope.getClassName()) + '.' + str(func_name) + ' ' + str(param_count) + '\n'
                return buf

            elif (str(term.nextSibling.firstChild.nodeValue).strip() == '.'):  # explicit function invocation
                nodes = term.parentNode.childNodes

                class_name = str(nodes[0].firstChilde.nodeValue).strip()
                func_name = str(nodes[2].firstChilde.nodeValue).strip()

                if (scope.indexOf(class_name) is not None):
                    param_count += 1
                    class_name = scope.kindOf(class_name)

                func_data = scope.getFunctionData(class_name, func_name)
                func_type = func_data[1]

                if (func_type == 'method'):
                    buf += 'push pointer 0\n'
                    param_count += 1

                params = term.nextSibling.nextSibling
                for arg in params.childNodes:
                    if (arg.nodeName == 'symbol'):
                        continue
                    buf += compileExpression(arg, scope, mode)
                    param_count += 1

                buf += 'call ' + str(class_name) + '.' + str(func_name) + ' ' + str(param_count) + '\n'
                return buf

        else:   # assuming it's a variable
            var_name = str(term.firstChild.nodeValue).strip()
            return 'push ' + str(scope.kindOf(var_name)) + ' ' + str(scope.indexOf(var_name)) + '\n'

        raise NotImplementedError

    elif (label == 'symbol'):           # parentheses around expression or unary operation
        if (str(term.firstChild.nodeValue).strip() in ['-','~']):
            return extractTerm(term.nextSibling, scope, mode) + handleUnaryOpSymbol(str(term.firstChild.nodeValue).strip())
        elif (str(term.firstChild.nodeValue).strip() == '('):
            return compileExpression(term.nextSibling, scope, mode)
        else:
            raise NotImplementedError


    raise Exception('Unknown term')

def handleBinaryOpSymbol(sym, node, scope):
    if (sym == '('):
        return compileExpression(node.nextSibling, scope)
    elif (sym == '+'):
        return 'add\n'
    elif (sym == '-'):
        return 'sub\n'
    elif (sym == '*'):
        return 'call Math.multiply 2\n'
    elif (sym == '/'):
        return 'call Math.divide 2\n'
    elif (sym == '&'):
        return 'and\n'
    elif (sym == '|'):
        return 'or\n'
    elif (sym == '='):
        return 'eq\n'
    elif (sym == '<'):
        return 'lt\n'
    elif (sym == '>'):
        return 'gt\n'

    raise NotImplementedError

def handleUnaryOpSymbol(sym):
    if (sym == '-'):
        return 'neg\n'
    elif (sym == '~'):
        return 'not\n'

    raise NotImplementedError

def keywordConstant(keyword):
    if (keyword in ['null', 'false']):
        return 'push constant 0\n'
    elif (keyword == 'true'):
        return 'push constant 0\nnot\n'
    elif (keyword == 'this'):
        return 'push pointer 0\n'

    raise NotImplementedError

def stringConstant(string):
    buf = ''
    str_len = len(string)
    buf += 'push constant '+ str(str_len)  + '\ncall String.new 1\n'
    for c in list(string):
        buf += 'push constant ' + str(ord(c)) + '\ncall String.appendChar 2\n'

    return buf

def objectOrClass(obj_node, scope):
    node_name = str(obj_node.firstChild.nodeValue).strip()
    if (scope.indexOf(node_name) is not None):
        return scope.typeOf(node_name), True
    else:
        return node_name, False
