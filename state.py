from coefficient import Coefficient, ComplexCoefficient
import copy

zero = "0"
one = "1"


class State:
    
    def __init__(self, coeff=None, val=None):
    
        self.set_coefficient(coeff)
        self.set_val(val)
        
    def __eq__(self, other):
        if isinstance(other, State):
            return self.val == other.get_val()
        return False
        
    def get_val(self):
        return self.val
    
    def get_coefficient(self):
        return self.coefficient
        
    def set_val(self, val):
        if isinstance(val, str):
            self.val = val
            for qubit in val:
                if not (qubit in [zero, one]):
                    self.val = None
                    raise ValueError("state value {0} is not entirely 1's and 0's".format(val))
                    
    def set_coefficient(self, coeff):
        if isinstance(coeff, Coefficient) or isinstance(coeff, ComplexCoefficient):
            self.coefficient = coeff
        else:
            raise ValueError("setting coefficient of incorrect type was attempted")
            
    def get_probability(self):
        return self.coefficient.to_probability()
        
    def x(self, qubit):
        self.val = self.val[0:qubit] + str(int(not int(self.val[qubit]))) + self.val[qubit+1:]
        return self
    
    def cx(self, source, target):
        new_target = str(int(not int(self.val[target]))) if self.val[source] == one else self.val[target]
        self.val = self.val[0:target] + new_target + self.val[target+1:]
        return self
    
    def z(self, qubit):
        if int(self.val[qubit]) == 1:
            self.coefficient.negate_magnitude()
        return self
    
    def y(self, qubit):
        self.z(qubit)
        self.x(qubit)
        self.coefficient.multiply_by_i()
        return self
        
    def h(self, qubit):
        new_coeff = copy.deepcopy(self.coefficient)
        new_val = copy.deepcopy(self.val)
        new_state = State(new_coeff, new_val)
        new_state.x(qubit)
        
        if self.val[qubit] == one:
            self.coefficient.negate_magnitude()
            
        return [self, new_state]
        
    def print(self):
        self.coefficient.print()
        print("|{0}>".format(self.val), end='')
