from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import urllib

DEV_CONN = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=QedSim;UID=SA;PWD=tercesdeqmis"

params = urllib.parse.quote_plus(DEV_CONN)
engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
