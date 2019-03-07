from sqlalchemy import Column, Integer, String, ForeignKey
from emulatorcommon.database import Database
from sqlalchemy.orm import relationship


class SinglePhase(Database.Base):

    __tablename__ = 'SinglePhase'

    id = Column(Integer, primary_key=True, autoincrement=True)
    flags = Column(String(2048))
    states = Column(String(2048))
    previous_phase_id = Column(Integer)
    phase = Column(String(2048))
    calculation_id = Column(Integer, ForeignKey('Calculation.id'))

    def __init__(self, previous_phase_id, phase, user_id):
        self.previous_phase_id = previous_phase_id
        self.phase = phase
        self.user_id = user_id

    def __repr__(self):
        return '<SinglePhase %r>' % (self.id)


class Calculation(Database.Base):

    __tablename__ = 'Calculation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    result = Column(String(2048))
    user_id = Column(Integer, ForeignKey('User.id'))
    experiment_id = Column(Integer, ForeignKey('Experiment.id'))
    type = Column(String(255))
    phases = relationship("SinglePhase", primaryjoin=SinglePhase.calculation_id == id)

    def __init__(self, result, user_id, type, experiment_id):
        self.result = result
        self.user_id = user_id
        self.type = type
        self.experiment_id = experiment_id

    def __repr__(self):
        return '<Calculation %r>' % (self.id)


class Experiment(Database.Base):

    __tablename__ = 'Experiment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    user_id = Column(Integer, ForeignKey('User.id'))
    type = Column(String(255))
    executions = relationship("Calculation", primaryjoin=Calculation.experiment_id == id)

    def __init__(self, name, user_id, type):
        self.name = name
        self.user_id = user_id
        self.type = type

    def __repr__(self):
        return '<Experiment %r>' % (self.id)


class User(Database.Base):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String(255))
    companyname = Column(String(255))
    phone = Column(String(50))
    calculations = relationship("Calculation", primaryjoin=Calculation.user_id == id)
    experiments = relationship("Experiment", primaryjoin=Experiment.user_id == id)

    def __init__(self, name, email, phone, password, companyname):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password
        self.companyName = companyname

    def __repr__(self):
        return '<User %r>' % (self.name)
