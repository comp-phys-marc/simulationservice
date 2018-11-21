from state import State, one, zero
from functools import wraps, partial
from math import sqrt
from coefficient import Coefficient
import random
import copy


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
    
    def get_density_matrix(self, qubit):
            
        [alpha, beta] = self.get_components(qubit)
        if isinstance(beta, Coefficient) and isinstance(alpha, Coefficient):
            
            entry00 = abs(alpha.get_magnitude())**2
            entry00 = str(round(entry00, 3))
            
            beta_conjugate = copy.deepcopy(beta)
            beta_conjugate.complex_conjugate()
    
            entry01 = alpha.get_magnitude()*beta_conjugate.get_magnitude()
            if alpha.get_imaginary() == True and beta_conjugate.get_imaginary() == True:
                entry01 = - entry01
            elif alpha.get_imaginary() == True or beta_conjugate.get_imaginary() == True:
                entry01 = str(entry01) + 'i'
            entry01 = str(round(entry01, 3))
            
            alpha_conjugate = copy.deepcopy(alpha)
            alpha_conjugate.complex_conjugate()
            
            entry10 = alpha_conjugate.get_magnitude()*beta.get_magnitude()
            if alpha_conjugate.get_imaginary() == True and beta.get_imaginary() == True:
                entry10 = - entry10
            elif alpha_conjugate.get_imaginary() == True or beta.get_imaginary() == True:
                entry10 = str(entry10) + 'i'
            entry10 = str(round(entry10, 3))
            
            entry11 = abs(beta.get_magnitude())**2
            entry11 = str(round(entry11, 3))
            
            return [[entry00, entry01], [entry10, entry11]]
    
    def print_density_matrices(self):
        
        for qubit in range(self.num_qubits):
            print("qubit {0} density matrix:\n".format(qubit))
            
            matrix = self.get_density_matrix(qubit)
            print(" _         _")
            print("|{:5s} {:>5s}|\n|{:5s} {:>5s}|\n".format(matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1]), end='')
            print(" -         -")     
        return
