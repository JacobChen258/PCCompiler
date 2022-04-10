
class InternalError(Exception): pass


class ValueTable(object):
    """
    Base value table class
    """

    def __init__(self):
        self.var_stack = [{}]
        self.temp_dict = {}

    def push_scope(self):
        self.var_stack.append(dict())

    def pop_scope(self):
        assert len(self.var_stack) > 1
        return self.var_stack.pop()

    def is_temp(self, name):
        assert type(name) == str, name + " is not a variable"
        return name[0] == "_" or name in self.temp_dict

    def set(self, name, value):
        if self.is_temp(name):
            self.set_temp(name, value)
        else:
            self.set_variable(name, value)

    def set_variable(self, name: str, value: any):
        self.var_stack[-1][name] = value

    def reset_variable(self, name):
        for stack in self.var_stack:
            if name in stack:
                stack[name] = name

    def reset_variables(self,vars:list):
        for var in vars:
            self.reset_variable(var)

    def set_temp(self, name: str, value: any):
        self.temp_dict[name] = value

    def lookup(self, name):
        if self.is_temp(name):
            return self.lookup_temp(name)
        return self.lookup_variable(name)

    def lookup_variable(self, name: str):
        for scope in reversed(self.var_stack):
            if name in scope:
                return scope[name]
        raise InternalError("Variable \"" + name + "\" not found")

    def lookup_temp(self, name):
        if name in self.temp_dict:
            cur_val = name
            prev = None
            while cur_val:
                prev = cur_val
                cur_val = self.temp_dict.get(cur_val)
            return prev
        return None
