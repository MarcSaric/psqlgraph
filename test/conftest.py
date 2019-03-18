"""
Needs to be run as the postgres user.
"""
import pytest

from sqlalchemy import create_engine

from psqlgraph import PsqlGraphDriver

@pytest.fixture(scope="session")
def root_user():
    return ("postgres", "postgres")

@pytest.fixture(scope="session")
def user():
    return ("test", "test")

@pytest.fixture(scope="session")
def host():
    return "localhost"

@pytest.fixture(scope="session")
def database():
    return "automated_test"

@pytest.fixture(scope="session")
def engine_factory():
    def a(*args, **kwargs):
        return None
    return a

@pytest.fixture(scope="session")
def connection(user, host):
    engine = create_engine("postgres://{user}@{host}/postgres".format(
        user=user, host=host))
    connection = engine.connect()
    connection.execute("commit") # Not sure why this is needed
    yield connection
    connection.close()

@pytest.fixture(scope="session")
def root_connection(root_user, host):
    engine = create_engine("postgres://{user}@{host}/postgres".format(
        user=root_user, host=host))
    connection = engine.connect()
    connection.execute("commit") # Not sure why this is needed
    yield connection
    connection.close()

@pytest.fixture(scope="session")
def db_maker(root_connection, database):
    create_stmt = 'CREATE DATABASE "{database}"'.format(database=database)
    root_connection.execute(create_stmt)
    yield root_connection
    create_stmt = 'DROP DATABASE "{database}"'.format(database=database)
    root_connection.execute(create_stmt)


@pytest.fixture(scope="session")
def user_maker(db_maker):
    user_stmt = "CREATE USER {user} WITH PASSWORD '{password}'".format(**user)
    db_maker.execute(user_stmt)
    perm_stmt = 'GRANT ALL PRIVILEGES ON DATABASE {database} to {user}'\
                ''.format(database=database, user=user[0])
    conn.execute(perm_stmt)
    conn.execute("commit")
    yield db_maker
    user_stmt = "DROP USER {user}".format(user=user)
    conn.execute(user_stmt)

@pytest.fixture(scope="session", autouse=True)
def init_data(user_maker):
    yield # All tests run right meow

@pytest.fixture(scope="session")
def driver(host, user, password, database):
    """
    create a table
    """

    # TODO this certainly has side effects
    return PsqlGraphDriver(host, user, password, database)
