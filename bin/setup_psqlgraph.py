"""
Needs to be run as the postgres user.
"""

from sqlalchemy import create_engine
import logging


from psqlgraph.node import Base
from psqlgraph import PsqlGraphDriver
from models import TestNode

@pytest.fixture(scope="Session")
def user():
    return "test"

@pytest.fixture(scope="Session")
def host()
    return "localhost"

@pytest.fixture(scope="Session")
def password():
    return "test"

@pytest.fixture(scope="Session")
def database():
    return "automated_test"

@pytest.fixture(scope="Session")
def root_user():
    return "postgres"

@pytest.fixture
def try_drop_test_data(user, database, root_user, host):

    engine = create_engine("postgres://{user}@{host}/postgres".format(
        user=root_user, host=host))

    conn = engine.connect()
    conn.execute("commit")

    try:
        create_stmt = 'DROP DATABASE "{database}"'.format(database=database)
        conn.execute(create_stmt)
    except Exception, msg:
        logging.warn("Unable to drop test data:" + str(msg))

    try:
        user_stmt = "DROP USER {user}".format(user=user)
        conn.execute(user_stmt)
    except Exception, msg:
        logging.warn("Unable to drop test data:" + str(msg))

    conn.close()


@pytest.fixture
def setup_database(user, password, database, root_user, host):
    """
    setup the user and database
    """

    try_drop_test_data(user, database)

    engine = create_engine("postgres://{user}@{host}/postgres".format(
        user=root_user, host=host))
    conn = engine.connect()
    conn.execute("commit")

    create_stmt = 'CREATE DATABASE "{database}"'.format(database=database)
    conn.execute(create_stmt)

    try:
        user_stmt = "CREATE USER {user} WITH PASSWORD '{password}'".format(
            user=user, password=password)
        conn.execute(user_stmt)

        perm_stmt = 'GRANT ALL PRIVILEGES ON DATABASE {database} to {password}'\
                    ''.format(database=database, password=password)
        conn.execute(perm_stmt)
        conn.execute("commit")
    except Exception, msg:
        logging.warn("Unable to add user:" + str(msg))
    conn.close()

def create_tables(host, user, password, database):
    """
    create a table
    """

    driver = PsqlGraphDriver(host, user, password, database)
    Base.metadata.create_all(driver.engine)

    setup_database(user, password, database)
    create_tables(host, user, password, database)
