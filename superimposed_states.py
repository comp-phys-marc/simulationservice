from .state import State, one, zero
from functools import wraps, partial
import random
import copy
from math import sqrt
from .coefficient import Coefficient

def normalize_print_and_get_requirements(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pfunc = partial(func, *args, **kwargs)
        result = pfunc()
        states = args[0]
        states.normalize()
        states.register_requirements()
        states.print()
        return result
    return wrapper

class States:
    
    def __init__(self, state_array=[], num_qubits=1):
        
        self.states = []
        self.num_qubits = num_qubits
        
        for state in state_array:
            self.add_state(state)
            
        self.state_bits = 0
        self.flag_bits = 0
        self.signals = 0
    
    def add_state(self, state):
        if isinstance(state, State):
            if len(state.get_val()) == self.num_qubits:
                self.states.append(state)
            else:
                raise ValueError("setting state with incorrect number of qubits {0} != {1} was attempted".format(len(state.get_val()), self.num_qubits))
        else:
            raise ValueError("setting state of incorrect type was attempted")
        
    def remove_state(self, state):
        self.states.remove(state)
    
    def get_components(self, qubit):
        alpha = Coefficient()
        beta = Coefficient()
        for state in self.states:
            if state.get_val()[qubit] == one:
                beta = beta.add(state.get_coefficient())
            elif state.get_val()[qubit] == zero:
                alpha = alpha.add(state.get_coefficient())
        return [alpha, beta]
        
    @normalize_print_and_get_requirements
    def x(self, qubit):
        for state in self.states:
            print("x ({0})".format(qubit), end='')
            state.print()
            print(" =", end='')
            state.x(qubit)
            state.print()
            print("\n")
        return self
         
    @normalize_print_and_get_requirements
    def cx(self, source, target):
        for state in self.states:
            print("cx ({0} -> {1})".format(source, target), end='')
            state.print()
            print(" =", end='')
            state.cx(source, target)
            state.print()
            print("\n")
        return self
       
    @normalize_print_and_get_requirements
    def y(self, qubit):
        for state in self.states:
            print("y ({0})".format(qubit), end='')
            state.print()
            print(" =", end='')
            state.y(qubit)
            state.print()
            print("\n")
        return self
            
    @normalize_print_and_get_requirements
    def z(self, qubit):
        for state in self.states:
            print("z ({0})".format(qubit), end='')
            state.print()
            print(" =", end='')
            state.z(qubit)
            state.print()
            print("\n")
        return self
            
    @normalize_print_and_get_requirements
    def h(self, qubit):
        
        alpha = Coefficient(magnitude=0.00, imaginary=False)
        beta = Coefficient(magnitude=0.00, imaginary=False)
        one_states = []
        zero_states = []
        
        for state in self.states:
            if state.get_val()[qubit] == one:
                one_states.append(state)
                beta = beta.add(state.get_coefficient())
            elif state.get_val()[qubit] == zero:
                zero_states.append(state)
                alpha = alpha.add(state.get_coefficient())
        
        negative_beta = copy.deepcopy(beta)
        negative_beta.negate_magnitude()
        if alpha.equals(beta):
            self.states = zero_states
        elif alpha.equals(negative_beta):
            self.states = one_states
        else:
            new_states = []  
            for state in self.states:
                hadamard_result = state.h(qubit)
                new_states.extend(hadamard_result)
                print("h ({0})".format(qubit), end='')
                state.print()
                print(" =", end='')
                hadamard_result[0].print()
                hadamard_result[1].print()
                print("\n")
            self.states = new_states
            return self 
    
    @normalize_print_and_get_requirements
    def m(self, qubit):
        alpha = Coefficient()
        beta = Coefficient()
        one_states = []
        zero_states = []
        
        for state in self.states:
            if state.get_val()[qubit] == one:
                one_states.append(state)
                beta = beta.add(state.get_coefficient())
            elif state.get_val()[qubit] == zero:
                zero_states.append(state)
                alpha = alpha.add(state.get_coefficient())
        
        result = self._measure(alpha.to_probability(), beta.to_probability())
        
        if result == one:
            self.states = one_states
        elif result == zero:
            self.states = zero_states
            
        return result
    
    def normalize(self):
        total_probability = 0
        unique_states = []
        for state in self.states:
            already_found = False
            for unique_state in unique_states:
                if state.get_val() == unique_state.get_val():
                    already_found = True 
                    unique_state.get_coefficient().add(state.get_coefficient())
            if not already_found:
                unique_states.append(state)
        for unique_state in unique_states:
            total_probability += unique_state.get_probability()
        norm_factor = 1/sqrt(total_probability)
        if total_probability != 1:
            for unique_state in unique_states:
                unique_state.get_coefficient().multiply_by_number(norm_factor)
        self.states = unique_states
        print("normalizing factor: {0}\n".format(norm_factor))
        return self
                
    def _measure(self, alpha, beta):
        cutoff = int(alpha*100)
        outcome = random.randint(0, 100)
        if outcome < cutoff:
            return zero
        else:
            return one
        
    def print(self):
        print("|Ψ> =", end='')
        for state in self.states:
            state.print()
        print("\n")
        
    def register_requirements(self):
        num_states = len(self.states)
        if num_states*self.num_qubits > self.state_bits:
            self.state_bits = num_states*self.num_qubits
        if num_states*2 > self.flag_bits:
            self.flag_bits = num_states*2 
        if num_states > self.signals:
            self.signals = 1
        
    def print_requirements(self):
        num_states = len(self.states)
        print("state bits: {0}, flag bits: {1}, signals: {2}\n".format(num_states*self.num_qubits, num_states*2, 1))
        
    def print_max_requirements(self):
        print("state bits: {0}, flag bits: {1}, signals: {2}\n".format(self.state_bits, self.flag_bits, self.signals))
        