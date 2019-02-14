from qedlib.coefficient import Coefficient, ComplexCoefficient
from qedlib.state import State, one
from qedlib.superimposed_states import States
from actualization import actualize
from pennylane import Device


class QEDAsPennyLaneDevice(Device):
    """
       Describes the QED system as a pennylane plugin device
    """
    name = 'QED Emulation Engine'
    short_name = 'qed'
    pennylane_requires = '0.1.0'
    version = '0.0.1'
    author = 'Marcus Edwards'

    _capabilites = {
        "model": "qubit"
    }

    def __init__(self, wires, shots, tolerance):
        super().__init__(wires, shots)

        """
        This circuit will be built as operations are applied,
        and executed in the distributed QED emulation system 
        when execute is called
        """
        self._circuit = None

        self._tolerance = tolerance
        self._topology = wires

        self._operation_map = {
            "CNOT": self.cx,
            "Hadamard": self.h,
            "PauliX": self.x,
            "PauliY": self.y,
            "PauliZ": self.z
        }

        self._expectation_map = {
            "Hermitian": self.m
        }

        self._state = None
        self.reset()

    def cx(self, source, target):
        # superimposed_states.cx proxy
        self._state.cx(source, target)
        return self._state.get_density_matrix(target)

    def x(self, target):
        # superimposed_states.x proxy
        self._state.x(target)
        return self._state.get_density_matrix(target)

    def y(self, target):
        # superimposed_states.y proxy
        self._state.y(target)
        return self._state.get_density_matrix(target)

    def z(self, target):
        # superimposed_states.z proxy
        self._state.z(target)
        return self._state.get_density_matrix(target)

    def h(self, target):
        # superimposed_states.h proxy
        self._state.h(target)
        return self._state.get_density_matrix(target)

    def m(self, target):
        # superimposed_states.m proxy
        result = self._state.m(target)
        return result

    def reset(self):
        """
        Reset the device
        """
        initial_coeff = Coefficient(magnitude=1.00, imaginary=False)
        initial_state = State(coeff=initial_coeff, val="0" * len(self._topology))
        state = States(state_array=[initial_state], num_qubits=len(self._topology))
        self._state = state
        actualize(self._state)

    def pre_apply(self):
        self.reset()

    def apply(self, operation, wires, par):
        """
        :param operation: operation (str) – name of the operation
        :param wires: wires (Sequence[int]) – subsystems the operation is applied on
        :param par: par (tuple) – parameters for the operation

        :return:
        """

        self._operation_map[operation]()
        actualize(self._state)

    def expval(self, expectation, wires, par):
        """
        :param expectation: expectation(str) – name of the expectation
        :param wires: wires(Sequence[int]) – subsystems the expectation value is to be measured on
        :param par: par(tuple) – parameters for the observable

        :return: exp(float) expectation value
        """
        if len(wires) == 1 and expectation == "Hermitian":
            result = self.m(wires[0])
            actualize(self._state)
            return result

        print("Unsupported expectation measure attempted: {0}".format(expectation))
        return None

    @property
    def operations(self):
        return set(self._operation_map.keys())

    @property
    def expectations(self):
        return set(self._expectation_map.keys())
