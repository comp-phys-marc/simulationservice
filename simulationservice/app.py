import json
from sqlalchemy import inspect
from IPython.utils.capture import capture_output
from settings import Settings
from models import Calculation
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


@conn.task(name="simulation.tasks.execute")
def execute_qasm(user_id, qasm, name):

    try:

        with capture_output() as captured:

            result = run_qasm(qasm)

            result.ensemble.print_density_matrices()
            result.ensemble.print_max_requirements()

        readout = captured.stdout

        new_calculation = Calculation(result=readout, user_id=user_id, type=name)
        add_refresh(new_calculation)
        db_session.commit()

        return {
            "message": f'"{name } simulation successful."',
            "data": json.dumps(readout),
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
