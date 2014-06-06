__author__ = 'larrath'

class ScopeChain:

    def __init__(self):
        #self.class_scope = {}
        #self.chain = [self.class_scope]
        
        self.static_variables = {}
        self.field_variables = {}
        self.local_variables = {}
        self.argument_variables = {}

        self.class_name = ''
        self.functions = {}

    def setClassName(self, name):
        self.class_name = name.strip()

    def pushNewScope(self):
        #current_scope = {}
        self.local_variables = {}
        self.argument_variables = {}
        #self.chain.append(current_scope)

    def leaveScope(self):
        #self.chain.pop(-1)
        self.local_variables = {}
        self.argument_variables = {}

    def define(self, var_name, var_type, var_visibility):
        if (var_visibility == 'static'):
            self.static_variables[var_name] = (var_name, var_type, var_visibility, len(self.static_variables))
        elif (var_visibility == 'field'):
            self.field_variables[var_name] = (var_name, var_type, var_visibility, len(self.field_variables))
        elif (var_visibility == 'var'):
            self.local_variables[var_name] = (var_name, var_type, var_visibility, len(self.local_variables))
        elif (var_visibility == 'argument'):
            self.argument_variables[var_name] = (var_name, var_type, var_visibility, len(self.argument_variables))
        else:
            raise NotImplementedError("Unknown visibility scope")

        print('='*30 + 'Dumping entire symbol table' + '='*30)
        print("Local: ")
        for var_name in self.local_variables:
            print('\t' + str(self.local_variables[var_name]))
        print("Argument: ")
        for var_name in self.argument_variables:
            print('\t' + str(self.argument_variables[var_name]))
        print("Static: ")
        for var_name in self.static_variables:
            print('\t' + str(self.static_variables[var_name]))
        print("Field: ")
        for var_name in self.field_variables:
            print('\t' + str(self.field_variables[var_name]))

        print('='*30 + 'Symbol table dump complete' + '='*30 + '\n\n')

    def varCount(self, declaration_type):
        if (declaration_type == 'static'):
            return len(self.static_variables)
        elif (declaration_type == 'field'):
            return len(self.field_variables)
        elif (declaration_type == 'argument'):
            return len(self.argument_variables)
        elif (declaration_type in ['local', 'var']):
            return len(self.local_variables)
        else:
            raise NotImplementedError("Unknown visibility level")

    def kindOf(self, var_name):
        if (var_name in self.argument_variables):
            return 'argument'
        elif (var_name in self.local_variables):
            return 'local'
        elif (var_name in self.static_variables):
            return 'static'
        elif (var_name in self.field_variables):
            return 'field'
        else:
            return None

    def indexOf(self, var_name):
        if (var_name in self.argument_variables):
            return self.argument_variables[var_name][3]
        elif (var_name in self.local_variables):
            return self.local_variables[var_name][3]
        elif (var_name in self.static_variables):
            return self.static_variables[var_name][3]
        elif (var_name in self.field_variables):
            return self.field_variables[var_name][3]
        else:
            return None

    def typeOf(self, var_name):
        if (var_name in self.argument_variables):
            return self.argument_variables[var_name][1]
        elif (var_name in self.local_variables):
            return self.local_variables[var_name][1]
        elif (var_name in self.static_variables):
            return self.static_variables[var_name][1]
        elif (var_name in self.field_variables):
            return self.field_variables[var_name][1]
        else:
            return None


    def getClassName(self):
        return self.class_name

    def defineFunction(self, func_name, func_type, func_class):

        if (func_name in self.functions):
            self.functions[func_name].append([(func_name, func_type, func_class)])
        else:
            self.functions[func_name] = [(func_name, func_type, func_class)]

    def getFunctionData(self, func_name, class_name):
        if (func_name in self.functions):
            for entry in self.functions[func_name]:
                if (entry[2] == class_name):
                    return entry

        return None

    def getFunctionsWithName(self, func_name):
        if (func_name in self.functions):
            return self.functions[func_name]

        return None