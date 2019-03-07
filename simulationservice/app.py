import json
from sqlalchemy import inspect
from IPython.utils.capture import capture_output
from settings import Settings
from models import Calculation, Experiment
from emulatorcommon.database import Database
from emulatorcommon.utilities import Utils
from emulatorcommon.message_bus import MessageBus
from qedlib.parser.parser import run_qasm

settings = Settings()
utils = Utils()

bus = MessageBus(settings)
conn = bus.connection

database = Database(settings)
db_session = database.session


@conn.task(name="simulation.tasks.list_executions")
def list_executions(filter):
    calculations_array = []
    if filter is None:
        calculations = Calculation.query.all()
        for calculation in calculations:
            calculations_array.extend(utils.object_as_dict(calculation))
    else:
        calculations = Calculation.query.filter_by(**filter)
        for calculation in calculations:
            calculations_array.append(utils.object_as_dict(calculation))
    if len(calculations_array) > 0:
        return {
            "message": "Calculations found.",
            "data": calculations_array,
            "status": 200
        }
    else:
        return {
            "message": "No matching calculations found.",
            "status": 404
        }


@conn.task(name="simulation.tasks.list_experiments")
def list_experiments(filter):
    experiments_array = []
    if filter is None:
        experiments = Experiment.query.all()
        for experiment in experiments:
            experiments_array.extend(utils.object_as_dict(experiment))
    else:
        experiments = Experiment.query.filter_by(**filter)
        for experiment in experiments:
            experiments_array.append(utils.object_as_dict(experiment))
    if len(experiments_array) > 0:
        return {
            "message": "Experiments found.",
            "data": experiments_array,
            "status": 200
        }
    else:
        return {
            "message": "No matching experiments found.",
            "status": 404
        }


@conn.task(name="simulation.tasks.create_experiment")
def create_experiment(user_id, name, type):

    try:
        new_experiment = Experiment(name=name, user_id=user_id, type=type)

        add_refresh(new_experiment)
        db_session.commit()

        return {
            "message": f'Successfully created {name} experiment.',
            "data": utils.object_as_dict(new_experiment),
            "status": 200
        }

    except Exception as e:
        error_message = str(e)
        return {
            "message": f'An error occurred: {error_message}',
            "status": 500
        }


@conn.task(name="simulation.tasks.execute")
def execute_qasm(user_id, qasm, name, experiment_id):

    try:

        with capture_output() as captured:

            result = run_qasm(qasm)

            result[0].ensemble.print_density_matrices()
            result[0].ensemble.print_max_requirements()

        readout = captured.stdout

        new_calculation = Calculation(result=readout, user_id=user_id, type=name, experiment_id=experiment_id)
        add_refresh(new_calculation)
        db_session.commit()

        return {
            "message": f'"{name} simulation successful."',
            "result": json.dumps(readout),
            "status": 200
        }

    except Exception as e:
        error_message = str(e)
        return {
            "message": f'An error occurred: {error_message}',
            "status": 500
        }


def add_refresh(obj):
    db_session.add(obj)
    db_session.flush()
    db_session.refresh(obj)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
