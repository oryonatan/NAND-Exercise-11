__author__ = 'larrath'

class ScopeChain:

    def __init__(self):
        self.class_scope = {}
        self.chain = [self.class_scope]
        self.class_name = ''

    def setClassName(self, name):
        self.class_name = name.strip()

    def pushNewScope(self):
        current_scope = {}
        self.chain.append(current_scope)

    def leaveScope(self):
        self.chain.pop(-1)

    def define(self, var_name, var_type, var_visibility):
        if (var_visibility in ['static', 'field']):
            self.chain[0][var_name] = (var_name, var_type, var_visibility, len(self.chain[0]) + 1)
        else:
            self.chain[-1][var_name] = (var_name, var_type, var_visibility, len(self.chain[-1]) + 1)

    def varCount(self, visibility):
        if (visibility in ['static', 'field']):
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