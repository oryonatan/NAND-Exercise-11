__author__ = 'larrath'

class ScopeChain:

    def __init__(self):
        self.class_scope = {}
        self.current_scope = {}

    def startSubroutine(self):
        self.current_scope = {}

    def define(self, var_name, var_type, var_visibility):
        if (var_visibility in ['static', 'field']):
            self.class_scope[var_name] = (var_name, var_type, var_visibility, len(self.class_scope) + 1)
        else:
            self.current_scope[var_name] = (var_name, var_type, var_visibility, len(self.current_scope) + 1)

    def varCount(self, visibility):
        if (visibility in ['static', 'field']):
            return len(self.class_scope)
        else:
            return len(self.current_scope)

    def kindOf(self, var_name):
        if (var_name in self.current_scope):
            return self.current_scope[var_name][2]
        elif (var_name in self.class_scope):
            return self.class_scope[var_name][2]
        else:
            return None

    def indexOf(self, var_name):
        if (var_name in self.current_scope):
            return self.current_scope[var_name][3]
        elif (var_name in self.class_scope):
            return self.class_scope[var_name][3]
        else:
            return None