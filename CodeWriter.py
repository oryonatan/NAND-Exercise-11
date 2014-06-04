__author__ = 'larrath'

from SymbolTable import ScopeChain

def expect_label(xml_data, desired_value):
    if (xml_data.nodeName.strip() != desired_value):
        raise Exception('Label should be ' + str(desired_value) + '; instead got ' + xml_data.nodeName)

def expect_values(xml_data, desired_values):
    if (str(xml_data.firstChild.nodeValue).strip() not in desired_values):
        raise Exception('Label should be in' + str(desired_values) + '; instead got ' + xml_data.firstChild.nodeValue)

def encode(xml_data):
    expect_label(xml_data, 'class')
    
    # parsing new class
    scope = ScopeChain()

    result = compileClassDeclaration(xml_data, scope)
    print('Encoding complete.')
    return result

def compileClassDeclaration(xml_data, scope):
    class_data = list(xml_data.childNodes)
    class_name = class_data[1].firstChild.nodeValue
    scope.setClassName(class_name)
    buf = ''
    print('Recognized Class Declaration')
    print('\tCompiling class body')
    class_data = class_data[3:] # discard previously handled elements

    while (class_data):
        operation = class_data[0].tagName
        if (operation == 'subroutineDec'):
            buf += compileClassBody(class_data[0], scope)
        elif (operation == 'classVarDec'):
            buf += compileVarDeclaration(class_data[0], scope)
        elif (operation == 'symbol' and class_data[0].firstChild.nodeValue.strip() == '}'):
            print('Finished compiling class subroutines and variables')
        else:
            raise Exception('Unknown operation in class body')
        class_data.pop(0)
    return buf

def compileClassBody(xml_data, scope):
    expect_label(xml_data, 'subroutineDec')
    print('Recognized class body')
    buf = ''

    while (xml_data.hasChildNodes()):
        print('\tbody data length: ' + str(len(xml_data.childNodes)))
        current_top = xml_data.childNodes[0]
        command = str(current_top.firstChild.nodeValue).strip()
        if (command in ['constructor', 'function', 'method']):
            buf += compileFunctionDeclaration(current_top.parentNode, scope)

    return buf

def compileFunctionDeclaration(xml_data, scope):
    expect_values(xml_data.firstChild, ['constructor', 'function', 'method'])
    print("Recognized function declaration")
    func_data = list(xml_data.childNodes)
    buf = ''
    
    function_declare_mode = func_data[0].firstChild.nodeValue.strip()
    function_return_type = func_data[1].firstChild.nodeValue.strip()
    function_name = func_data[2].firstChild.nodeValue.strip()
    function_args = compileFunctionArguments(func_data[4], scope)
    function_body = compileFunctionBody(func_data[6], scope) # parse function body

    scope.defineFunction(function_name, function_declare_mode, scope.getClassName())

    print('\tFunction data: (' + function_declare_mode + ') ' + function_return_type + ' ' + function_name)
    print(function_args)
    arg_count = 0    # TODO this is wrong! Need to count the arguments!


    buf += 'function ' + str(scope.getClassName()) + '.' + function_name + ' ' + str(arg_count) + '\n'
    buf += function_args
    buf += function_body
    # destroy the nodes we compiled

    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileFunctionArguments(parameterList, scope):
    scope.pushNewScope()
    expect_label(parameterList, 'parameterList')
    print('Compiling parameter list')
    buf = '' # TODO add VM code here
    params = list(parameterList.childNodes)

    if (len(params) == 1 and params[0].nodeValue == '\n'):
        print('\tFunction accepts zero arguments')

    else:
        while (params): # don't actually need to push the declaration anywhere, just add them to local scope and push them into ARG register.
            declaration_kind = 'argument'
            var_type = params.pop(0).firstChild.nodeValue.strip()
            var_name = params.pop(0).firstChild.nodeValue.strip()
            if (params): # discard delimiter, if one exists (last entry has none)
                params.pop(0)
            scope.define(var_name, var_type, declaration_kind)
            print('\tAdded variable {' + str(var_type) + ' ' + str(var_name) +'} to local scope as function parameter')

    # destroy the nodes we compiled
    parameterList.parentNode.removeChild(parameterList)
    parameterList.unlink()
    return buf

def compileFunctionBody(body, scope):
    print("Compiling function body")
    data = list(body.childNodes)
    data = data[1:-1]   # remove first and last elements ( '{' and '}' )
    buf = ''
    while (data):
        action = data[0].tagName
        if (action == 'varDec'):
            buf += str(compileVarDeclaration(data[0], scope))
        elif (action == 'statements'):
            buf += str(compileStatements(data[0], scope))
        else:
            raise Exception('Unknown operation in function body')
        data.pop(0)
    return buf
    
def compileVarDeclaration(declaration, scope):
    try:
        expect_label(declaration, 'varDec')
    except Exception:
        expect_label(declaration, 'classVarDec')

    data = list(declaration.childNodes)
    print ('Compiling variable declaration section')
    declaration_kind = data.pop(0).firstChild.nodeValue.strip()
    var_type = data.pop(0).firstChild.nodeValue.strip()

    while (data):
        var_name = data.pop(0).firstChild.nodeValue.strip()
        scope.define(var_name, var_type, declaration_kind)

        print('\tAdded variable: ' + str(declaration_kind) + ' ' + str(var_type) + ' ' + str(var_name))
        data.pop(0) # discard delimiter

    # Variable declarations do not generate code. It's enough to update the scope with data.
    return ''

def compileStatements(xml_data, scope):
    expect_label(xml_data, 'statements')
    data = list(xml_data.childNodes)
    print ('Compiling statement container')
    buf = ''
    for statement in data:
        statement_type = statement.tagName

        if (statement_type == 'letStatement'):
            buf += compileLetStatement(statement, scope)
        elif (statement_type == 'ifStatement'):
            buf += compileIfStatement(statement, scope)
        elif (statement_type == 'whileStatement'):
            buf += compileWhileStatement(statement, scope)
        elif (statement_type == 'doStatement'):
            buf += compileDoStatement(statement, scope)
        elif (statement_type == 'returnStatement'):
            buf += compileReturnStatement(statement, scope)
        else:
            raise Exception('Unknown statement type')
    return buf


def compileLetStatement(xml_data, scope):
    expect_label(xml_data, 'letStatement')
    print('\tCompiling let statement')
    data = list(xml_data.childNodes)
    var_name = data[1]
    buf = ''
    if (data[2].firstChild.nodeValue.strip() == '['):   # accessing array element
        print('\t\tAccessing array')
        array_exp = data[3]
        rvalue_exp = data[6]

        buf += compileExpression(array_exp, scope)
    else:
        rvalue_exp = data[3]

    buf += compileExpression(rvalue_exp, scope)

    #TODO assign value into var_name

    # remove nodes for garbage collection
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileIfStatement(xml_data, scope):
    expect_label(xml_data, 'ifStatement')
    print('\tCompiling if statement')
    data = list(xml_data.childNodes)

    cond_exp = data[2]
    buf = ''
    statement_body = data[5]

    if (len(data) == 11):
        print('If block with Else statement')
        else_statement = data[9]
        # TODO: might need to change the internal ordering of some function calls here
        buf += compileExpression(cond_exp, scope)
        buf += compileStatements(statement_body, scope)
        buf += compileStatements(else_statement, scope)
    elif (len(data) == 7):
        print('If block without an Else statement')
        # TODO: might need to change the internal ordering of some function calls here
        buf += compileExpression(cond_exp, scope)
        buf += compileStatements(statement_body, scope)
    else:
        print('====bad node count in if statement====')
        exit(1)

    # remove nodes for garbage collection
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileWhileStatement(xml_data, scope):
    expect_label(xml_data, 'whileStatement')
    print('\tCompiling while statement')
    data = list(xml_data.childNodes)
    buf = ''
    cond_exp = data[2]
    statement_body = data[5]

    # for k in data:
    #     print (k.nodeName)

    buf += compileExpression(cond_exp, scope)
    buf += compileStatements(statement_body, scope)

    # remove nodes for garbage collection
    xml_data.parentNode.removeChild(xml_data)
    xml_data.unlink()
    return buf

def compileDoStatement(xml_data, scope):
    expect_label(xml_data, 'doStatement')
    data = list(xml_data.childNodes)
    print('\tCompiling do statement')
    buf = ''
    if (data[2].firstChild.nodeValue.strip() == '.'):   # do Class.Function( params ) ;
        function_name = str(data[1].firstChild.nodeValue.strip()) + '.' + str(data[3].firstChild.nodeValue.strip())
        params = data[5]
    
    else:
        function_name = data[1].firstChild.nodeValue.strip()
        params = data[3]
    
    # TODO: there might be another implementation detail I am missing here regarding functions' owning classes
    # TODO: can use scope.getFunctionsWithName and scope.getFunctionData to get the necessary information
    for arg in params.childNodes:
        if (str(arg.firstChild.nodeValue).strip() == ','):
            continue
        buf += str(compileExpression(arg, scope))
    params_count = len(params.childNodes)
    buf += 'call ' + function_name + ' ' + str(params_count) + '\n' + 'pop temp 0\n'

    return buf


def compileReturnStatement(xml_data, scope):
    expect_label(xml_data, 'returnStatement')
    data = list(xml_data.childNodes)
    print("\tCompiling return statement")
    buf = ''
    
    if (data[1].tagName == 'expression'):
        print("\t\tReturn statement returns value")
        buf += compileExpression(data[1], scope)
    else:
        print("\t\tReturn statement has no value")
        buf += 'push constant 0\n'

    scope.leaveScope()
    return buf + 'return\n'

def compileExpression(xml_data, scope):
    expect_label(xml_data, 'expression')
    print('\tCompiling Expression')

    terms = list(xml_data.childNodes)

    if (len(terms) == 1): # expression is a constant, a nested expression, unary operation or function call
        return extractTerm(terms[0], scope)

    elif (len(terms) == 2): # expression is an unary operation
        raise Exception('Seems we actually do get expressions of length 2')
    #     operation = handleUnaryOpSymbol(str(terms[0].firstChild.nodeValue).strip())
    #     term = extractTerm(terms[1], scope)
    #     return str(term) + str(operation)
    
    elif (len(terms) == 3): # expression is (term op term)
        operation = handleBinaryOpSymbol(str(terms[1].firstChild.nodeValue).strip(), terms[1], scope)
        left_term = extractTerm(terms[0], scope)
        right_term = extractTerm(terms[2], scope)
        return str(left_term) + str(right_term) + str(operation)
    
    elif (len(terms) == 4): # expression is array[expression]
        array_name = str(terms[0].firstChild.nodeValue).strip()  # TODO: might need to go to firstChild.firstChild
        array_exp = str(compileExpression(terms[2], scope)).strip()
        print(str(array_name) + str(array_exp) + ' <-- temporary code, actually incorrect')
        return str(array_name) + str(array_exp)

    raise Exception('Cannot recognize expression')


def extractTerm(root, scope):
    expect_label(root, 'term')
    term = root.firstChild
    label = term.nodeName

    if (label == 'keyword'):    # generate constant value value
        return keywordConstant(str(term.firstChild.nodeValue).strip())

    elif (label == 'integerConstant'):  # constant number
        return 'push constant ' + str(term.firstChild.nodeValue).strip() + '\n'

    elif (label == 'stringConstant'):   # generate string
        return stringConstant(str(term.firstChild.nodeValue).strip())

    elif (label == 'identifier'):       # load variable from scope
        print('\t\tIn identifier sub-block')
        siblings = list(term.parentNode.childNodes)
        buf = ''
        if (len(siblings) > 4):
            if (str(siblings[1].firstChild.nodeValue).strip() == '.'): # Class.Function(expressionList);
                class_name = str(siblings[0].firstChild.nodeValue).strip()
                func_name = str(siblings[2].firstChild.nodeValue).strip()
                param_count = 0
                for param in siblings[4].childNodes:

                    param_count += 1    # TODO: need a more sophisticated thing here, since we can have junk symbols.
                    buf += str(compileExpression(param, scope))

                buf += 'call ' + str(class_name) + '.' + str(func_name) + ' ' + str(param_count) + '\n'
                return buf
        # for node in data:

        sub_label = str(term.firstChild.nodeValue).strip()

        print(sub_label)
        # TODO: can be a function call, a variable or something else.
        return buf
        raise NotImplementedError

    elif (label == 'symbol'):           # parentheses around expression or unary operation
        if (str(term.firstChild.nodeValue).strip() in ['-','~']):
        # if (term.nextSibling.nodeName == 'term'): # in case we need a more robust check
            return extractTerm(term.nextSibling, scope) + handleUnaryOpSymbol(str(term.firstChild.nodeValue).strip())
        elif (str(term.firstChild.nodeValue).strip() == '('):
            return compileExpression(term.nextSibling, scope)
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
    print(sym)
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
        return 'push constant 0\nneg\n'
    elif (keyword == 'this'):
        return 'push pointer 0\n' # TODO do we need this?

    raise NotImplementedError

def stringConstant(string):
    buf = ''
    str_len = len(string)
    buf += 'push constant '+ str(str_len)  + '\ncall String.new 1\n'
    for c in list(string):
        buf += 'push constant ' + str(int(c)) + '\ncall String.appendChar 2\n'

    return buf
