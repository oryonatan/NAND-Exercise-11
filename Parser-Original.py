__author__ = 'larrath'

import xml.dom.minidom as minidom

XML_imp = minidom.getDOMImplementation().createDocument(None, None, None)

def pop_child(xml_data, top):
    result = xml_data.item(0)
    return result

def peek(xml_data):
    return xml_data.item(0).firstChild.data.strip()

def peek_child(xml_data):
    return xml_data.item(1).firstChild.data.strip()

def get_node_type(xml_data):
    return xml_data.item(0).nodeName

def get_child_node_type(xml_data):
    return xml_data.item(1).nodeName

def append_nodes_batch(xml_data, anchor, count):
    for i in range(count):
        anchor.appendChild(pop_child(xml_data, anchor))

# Program Structure
def parse_class(xml_data):
    # Each file contains a single class.
    # Data format: 'class' className '{' classVarDec* subroutineDec* '}'
    global XML_imp
    if (peek(xml_data) != 'class'):
        print("Invalid data format; first token should be 'class'. Instead it was " + peek(xml_data) + "\nTerminating.")
        exit()

    XML_imp = minidom.getDOMImplementation().createDocument(None, 'class', None)
    top_node = XML_imp.documentElement
    append_nodes_batch(xml_data, top_node, 3)                        # <keyword> class, <identifier> className, <symbol> {
    parse_class_variable_declaration(xml_data, top_node)            # parse class variable declarations, if any
    parse_class_subroutine_declaration(xml_data, top_node)        # parse class subroutines, if any
    append_nodes_batch(xml_data, top_node, 1)                        # <symbol> '}'

    if (xml_data.length > 1):
        print ("Seems we read too few lines")
    return top_node


def parse_class_variable_declaration(xml_data, anchor):
    # ('static'|'field') type varName (',' varName)* ';'
    global XML_imp
    # first test if this even appears.
    if (peek(xml_data) in ['static', 'field']):
        declaration_anchor = XML_imp.createElement('classVarDec')
        anchor.appendChild(declaration_anchor)    						# attach the declaration statement to the parent anchor

        append_nodes_batch(xml_data, declaration_anchor, 3)            # <keyword> static|field, <keyword|identifier> type, <identifier> name
        while (peek(xml_data) == ','):
            append_nodes_batch(xml_data, declaration_anchor, 2)        # <symbol> ',', <identifier> varName

        append_nodes_batch(xml_data, declaration_anchor, 1)        # <symbol> ';'
        parse_class_variable_declaration(xml_data, anchor)          	# call the function again, in case more declarations exist after the one we parsed.


def parse_class_subroutine_declaration(xml_data, anchor):
    # ('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody

    # first test if this even appears.
    global XML_imp
    if (peek(xml_data) in ['constructor', 'function', 'method']):
        declaration_anchor = XML_imp.createElement('subroutineDec')
        anchor.appendChild(declaration_anchor)        # attach the declaration statement to the parent anchor
        append_nodes_batch(xml_data, declaration_anchor, 4)        # <keyword> constructor|function|method, <keyword|identifier> type, <identifier> name, <symbol> (
        parse_parameter_list(xml_data, declaration_anchor)        # parse and append the parameterList
        append_nodes_batch(xml_data, declaration_anchor, 1)        # <symbol> ')'

        parse_subroutine_body(xml_data, declaration_anchor)        # parse the subroutine body

        parse_class_subroutine_declaration(xml_data, anchor)            # call the function again, in case more declarations exist after the one we parsed.



def parse_parameter_list(xml_data, anchor):
    # ( (typename varName) (',' (typename Varname))* )?
    global XML_imp
    parameters_anchor = XML_imp.createElement('parameterList')
    anchor.appendChild(parameters_anchor)

    if (peek(xml_data) == ')'):    # empty parameter list
        blank_tag = XML_imp.createTextNode('\n')
        parameters_anchor.appendChild(blank_tag)
        return

    append_nodes_batch(xml_data, parameters_anchor, 2)        # <keyword|identifier> type, <identifier> varName
    while (peek(xml_data) == ','):    # more parameters exist
        append_nodes_batch(xml_data, parameters_anchor, 3)    # <symbol> ',', <keyword|identifier> type, <identifier> varName


def parse_subroutine_body(xml_data, anchor):
    # '{' varDec* statements '}'
    global XML_imp
    subroutine_anchor = XML_imp.createElement('subroutineBody')
    anchor.appendChild(subroutine_anchor)

    append_nodes_batch(xml_data, subroutine_anchor, 1)        # <symbol> '{'
    empty_body = True
    if (peek(xml_data) != '}'):                                # subroutine has a non-empty body
        empty_body = False
        parse_variable_declaration(xml_data, subroutine_anchor)
        parse_statements(xml_data, subroutine_anchor)

    if (empty_body):    # expand empty tags
        blank_tag = XML_imp.createTextNode('\n')
        subroutine_anchor.appendChild(blank_tag)

    append_nodes_batch(xml_data, subroutine_anchor, 1)    # <symbol> '}'


def parse_variable_declaration(xml_data, anchor):
    # 'var' type varName (',' varName)* ';'
    global XML_imp

    if (peek(xml_data) == 'var'):
        declaration_anchor = XML_imp.createElement('varDec')
        anchor.appendChild(declaration_anchor)
        append_nodes_batch(xml_data, declaration_anchor, 3)    # <keyword> var, <keyword|identifier> type, <identifier> name

        while (peek(xml_data) == ','):    # more parameters exist
            append_nodes_batch(xml_data, declaration_anchor, 2)    # <symbol> ',', <identifier> name

        append_nodes_batch(xml_data, declaration_anchor, 1)     # <symbol> ';'
        parse_variable_declaration(xml_data, anchor) # call self again, in case the next lines also declare variables

# Statements
def parse_statements(xml_data, anchor):
    # statement *
    statements_anchor = None
    while (peek(xml_data) in ['let', 'if', 'while', 'do', 'return']):
        if (not statements_anchor):
            statements_anchor = XML_imp.createElement('statements')
            anchor.appendChild(statements_anchor)

        parse_statement(xml_data, statements_anchor)


def parse_statement(xml_data, anchor):
    # letStatement | ifStatement | whileStatement | doStatement | returnStatement
    global XML_imp

    statement_type = peek(xml_data)

    if (statement_type == 'let'):
        parse_let_statement(xml_data, anchor)
    elif (statement_type == 'if'):
        parse_if_statement(xml_data, anchor)
    elif (statement_type == 'while'):
        parse_while_statement(xml_data, anchor)
    elif (statement_type == 'do'):
        parse_do_statement(xml_data, anchor)
    elif (statement_type == 'return'):
        parse_return_statement(xml_data, anchor)
    else:
        raise NotImplementedError


def parse_let_statement(xml_data, anchor):
    # 'let' varName ( '[' expression ']' )? '=' expression ';'
    global XML_imp
    let_anchor = XML_imp.createElement('letStatement')            # add <letStatement> anchor
    anchor.appendChild(let_anchor)

    append_nodes_batch(xml_data, let_anchor, 2)    # <keyword> let, <identifier> varName

    if peek(xml_data) == '[':
        append_nodes_batch(xml_data, let_anchor, 1)    # <symbol> '['
        parse_expression(xml_data, let_anchor)
        append_nodes_batch(xml_data, let_anchor, 1)    # <symbol> ']'

    append_nodes_batch(xml_data, let_anchor, 1)        # <symbol> '='
    parse_expression(xml_data, let_anchor)
    append_nodes_batch(xml_data, let_anchor, 1)        # <symbol> ';'


def parse_if_statement(xml_data, anchor):
    # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    global XML_imp
    if_anchor = XML_imp.createElement('ifStatement')            # add <ifStatement> anchor
    anchor.appendChild(if_anchor)

    append_nodes_batch(xml_data, if_anchor, 2)    # <keyword> if, <symbol> '('
    parse_expression(xml_data, if_anchor)
    append_nodes_batch(xml_data, if_anchor, 2)    # <symbol> ')', <symbol> '{'
    parse_statements(xml_data, if_anchor)
    append_nodes_batch(xml_data, if_anchor, 1)    # <symbol> '}'
    if peek(xml_data) == 'else':
        append_nodes_batch(xml_data, if_anchor, 2)    # <keyword> else, <symbol> '{'
        parse_statements(xml_data, if_anchor)
        append_nodes_batch(xml_data, if_anchor, 1)    # <symbol> '}'


def parse_while_statement(xml_data, anchor):
    # 'while' '(' expression ')' '{' statements '}'
    global XML_imp
    while_anchor = XML_imp.createElement('whileStatement')            # add <whileStatement> anchor
    anchor.appendChild(while_anchor)

    append_nodes_batch(xml_data, while_anchor, 2)    # <keyword> while, <symbol> '('
    parse_expression(xml_data, while_anchor)
    append_nodes_batch(xml_data, while_anchor, 2)    # <symbol> ')', <symbol> '{'
    parse_statements(xml_data, while_anchor)
    append_nodes_batch(xml_data, while_anchor, 1)    # <symbol> '}'


def parse_do_statement(xml_data, anchor):
    # 'do' subroutineCall ';'
    global XML_imp
    do_anchor = XML_imp.createElement('doStatement')            # add <doStatement> anchor
    anchor.appendChild(do_anchor)

    append_nodes_batch(xml_data, do_anchor, 2) # <keyword> do, <identifier> name
    if (peek(xml_data) == '.'): # explicit function calling [Class.Function(args)]
        append_nodes_batch(xml_data, do_anchor, 3) # <symbol> '.', <identifier> name, <symbol> '('
    else:   # normal function calling [Function(args)]
        append_nodes_batch(xml_data, do_anchor, 1) # <symbol> '('


    parse_expression_list(xml_data, do_anchor)
    append_nodes_batch(xml_data, do_anchor, 2) # <symbol> ')', <symbol> ';'


def parse_return_statement(xml_data, anchor):
    # 'return' expression? ';'
    global XML_imp
    return_anchor = XML_imp.createElement('returnStatement')    # add <returnStatement> anchor
    anchor.appendChild(return_anchor)

    append_nodes_batch(xml_data, return_anchor, 1) # <keyword> return
    if (peek(xml_data) != ';'):
        parse_expression(xml_data, return_anchor)

    append_nodes_batch(xml_data, return_anchor, 1) # <symbol> ';'

# Expressions
def parse_expression(xml_data, anchor):
# term (op term)*
    global XML_imp
    expression_anchor = XML_imp.createElement('expression')    # add <expression> anchor
    anchor.appendChild(expression_anchor)

    parse_term(xml_data, expression_anchor)

    while ((peek(xml_data) in ['+', '-', '*', '/', '&', '|', '<', '>', '='])):
        append_nodes_batch(xml_data, expression_anchor, 1)    # <symbol> operator
        parse_term(xml_data, expression_anchor)


def parse_term(xml_data, anchor):
    # integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
    global XML_imp
    term_anchor = XML_imp.createElement('term')    # add <term> anchor
    anchor.appendChild(term_anchor)

    tag = get_node_type(xml_data)   # peek at current node type

    if (tag in ['integerConstant', 'stringConstant', 'keywordConstant']):
        parse_term_constant(xml_data, term_anchor)
    elif (tag in ['identifier', 'keyword']):
        parse_term_identifier_keyword(xml_data, term_anchor)
    elif (tag == 'symbol'):        # expecting '(' expression ')'
        if (peek(xml_data) in ['-', '~']): # unary operation
            parse_term_unary_op(xml_data, term_anchor)
        else: # '(' expression ')'
            parse_term_symbol(xml_data, term_anchor)
    else:
        raise NotImplementedError


def parse_term_constant(xml_data, anchor):
    append_nodes_batch(xml_data, anchor, 1)    # append single-line element

def parse_term_identifier_keyword(xml_data, anchor):
    lookahead = peek_child(xml_data)

    if (lookahead == '.'):	# fully-qualified function call
        append_nodes_batch(xml_data, anchor, 4)    # <identifier> name, <symbol> '.', <identifier> name, <symbol> '('
        parse_expression_list(xml_data, anchor)
        append_nodes_batch(xml_data, anchor, 1)    # <symbol> ')'

    elif (lookahead == '('): # regular function call
        append_nodes_batch(xml_data, anchor, 2)    # <identifier> name, <symbol> '('
        parse_expression_list(xml_data, anchor)
        append_nodes_batch(xml_data, anchor, 1)    # <symbol> ')'

    elif (lookahead == '['): # array access
        append_nodes_batch(xml_data, anchor, 2)	# <identifier> name, <symbol> '['
        parse_expression(xml_data, anchor)
        append_nodes_batch(xml_data, anchor, 1)	# <symbol> ']'

    else: # just a variable
        append_nodes_batch(xml_data, anchor, 1)	# <identifier> name

def parse_term_symbol(xml_data, anchor):
    append_nodes_batch(xml_data, anchor, 1)    # <symbol> '('
    parse_expression(xml_data, anchor)
    append_nodes_batch(xml_data, anchor, 1)    # <symbol> ')'

def parse_term_unary_op(xml_data, anchor):
    append_nodes_batch(xml_data, anchor, 1)    # <symbol> '~'|'-'
    parse_term(xml_data, anchor)

def parse_subroutine_call(xml_data, anchor):
    # subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
    global XML_imp
    call_anchor = XML_imp.createElement('subroutineCall')
    anchor.appendChild(call_anchor)

    append_nodes_batch(xml_data, call_anchor, 1)    # <identifier> name
    if (peek(xml_data) == '.'):        # Call format: className.function(expressionList)
        append_nodes_batch(xml_data, call_anchor, 3)    # <symbol> '.', <identifier> subroutineName, <symbol> '('
    else:
        append_nodes_batch(xml_data, call_anchor, 1)    # <symbol> '('

    parse_expression_list(xml_data, call_anchor)
    append_nodes_batch(xml_data, call_anchor, 1)    # <symbol> ')'


def parse_expression_list(xml_data, anchor):
    # (expression (',' expression)* )?
    global XML_imp
    expression_list_anchor = XML_imp.createElement('expressionList')
    anchor.appendChild(expression_list_anchor)
    empty_body = True

    if (peek(xml_data) != ')'):        # expressionList only validly appears when enclosed by parentheses
        empty_body = False
        parse_expression(xml_data, expression_list_anchor)
        while (peek(xml_data) == ','):
            append_nodes_batch(xml_data, expression_list_anchor, 1)        # <symbol> ','
            parse_expression(xml_data, expression_list_anchor)

    if (empty_body):
        blank_tag = XML_imp.createTextNode('\n')
        expression_list_anchor.appendChild(blank_tag)


def parse(xml_data, debug=False):
    global counter
    counter = 0
    tokens = xml_data.getElementsByTagName("tokens").item(0).childNodes
    if debug:
        print("Length of tokens children: " + str(tokens.length))
        for t in tokens:
            print(str(t.tagName) + "\t" + str(t.firstChild.nodeValue))
        return parse_class(tokens)
    else:
        return parse_class(tokens)