__author__ = 'larrath'

class ScopeChain:

    def __init__(self):
        self.class_scope = {}
        self.chain = [self.class_scope]
        self.class_name = ''
        self.functions = {}

    def setClassName(self, name):
        self.class_name = name.strip()

    def pushNewScope(self):
        current_scope = {}
        self.chain.append(current_scope)

    def leaveScope(self):
        self.chain.pop(-1)

    def define(self, var_name, var_type, var_visibility):
        if (var_visibility in ['static', 'field']):
            self.chain[0][var_name] = (var_name, var_type, var_visibility, len(self.chain[0]))
        else:
            if (var_visibility == 'var'):
                var_visibility = 'local'
            self.chain[-1][var_name] = (var_name, var_type, var_visibility, len(self.chain[-1]))

    def varCount(self, declaration_type):
        if (declaration_type in ['static', 'field']):
            return len(self.chain[0])
        else:
            return len(self.chain[-1])

    def kindOf(self, var_name):
        for i in range(len(self.chain) - 1, 0, -1):
            if (var_name in self.chain[i]):
                return self.chain[i][var_name][2]
        else:
            return None

    def indexOf(self, var_name):
        for i in range(len(self.chain) - 1, 0, -1):
            if (var_name in self.chain[i]):
                return self.chain[i][var_name][3]
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