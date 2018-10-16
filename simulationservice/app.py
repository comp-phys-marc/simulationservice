from coefficient import Coefficient, ComplexCoefficient
from state import State, one, zero
from superimposed_states import States
from actualization import *
from database import db_session
from models import User, Calculation, SinglePhase
from celery import Celery
from sqlalchemy import inspect
from IPython.utils.capture import capture_output
import json


celery = Celery("tasks", backend='rpc://',
                    broker='amqp://guest:guest@35.196.180.90:5672', queue="simulation")

@celery.task(name="simulation.tasks.teleportation")
def teleportation(user_id):
    
    initial_coeff = Coefficient(magnitude=1.00, imaginary=False)
    initial_state = State(coeff=initial_coeff, val="000")
    state = States(state_array=[initial_state], num_qubits=3)

    with capture_output() as captured:
        
        print("State to transmit: {0}\n".format(initial_state.get_val()[2]))
        
        first_phase = actualize(state)
        state.print_density_matrices()
        state.h(qubit=0)
        state.print_density_matrices()
        second_phase = actualize(state, first_phase)
        state.cx(source=0, target=1).cx(source=2, target=0).h(qubit=2)
        state.print_density_matrices()
        third_phase = actualize(state, second_phase)
        
        m_1 = state.m(qubit=2)
        m_2 = state.m(qubit=0)
    
        print("Alice measures {0}, {1}\n".format(m_1, m_2))
        
        if m_2 == one:
            state.x(qubit=1)
        if m_1 == one:
            state.z(qubit=1)
            
        state.print_density_matrices()
        
        print("State received: {0}\n".format(state.states[0].get_val()[1]))
        
        state.print_max_requirements()
        
    result = captured.stdout
    
    new_teleportation = Calculation(result=result, user_id=user_id, type="teleporation")
    add_refresh(new_teleportation)
    
    first_phase.calculation_id = new_teleportation.id
    second_phase.calculation_id = new_teleportation.id
    third_phase.calculation_id = new_teleportation.id
    
    db_session.add(first_phase)
    db_session.add(second_phase)
    db_session.add(third_phase)
    db_session.commit()
    
    return result

def add_refresh(obj):
    db_session.add(obj)
    db_session.flush()
    db_session.refresh(obj)

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
    