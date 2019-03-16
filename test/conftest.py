"""
Needs to be run as the postgres user.
"""

from sqlalchemy import create_engine

from psqlgraph.node import Base
from psqlgraph import PsqlGraphDriver

@pytest.fixture(scope="session")
def root_user():
    return "postgres"

@pytest.fixture(scope="session")
def user():
    return "test"

@pytest.fixture(scope="session")
def host()
    return "localhost"

@pytest.fixture(scope="session")
def password():
    return "test"

@pytest.fixture(scope="session")
def database():
    return "automated_test"

@pytest.fixture(scope="session")
def get_connection(user, host):
    engine = create_engine("postgres://{user}@{host}/postgres".format(
        user=root_user, host=host))
    connection = engine.connect()
    connection.execute("commit") # Not sure why this is needed
    yield connection
    connection.close()

@pytest.fixture(scope="session")
def init_data(get_connection, database, user, password):
    conn = get_connection

    create_stmt = 'CREATE DATABASE "{database}"'.format(database=database)
    conn.execute(create_stmt)

    user_stmt = "CREATE USER {user} WITH PASSWORD '{password}'".format(
        user=user, password=password)
    conn.execute(user_stmt)

    perm_stmt = 'GRANT ALL PRIVILEGES ON DATABASE {database} to {password}'\
                ''.format(database=database, password=password)
    conn.execute(perm_stmt)
    conn.execute("commit")

    yield # All tests run right meow

    create_stmt = 'DROP DATABASE "{database}"'.format(database=database)
    connection.execute(create_stmt)

    user_stmt = "DROP USER {user}".format(user=user)
    conn.execute(user_stmt)

@pytest.fixture(scope="session")
def create_tables(host, user, password, database):
    """
    create a table
    """

    # TODO these certainly have side effects
    driver = PsqlGraphDriver(host, user, password, database)
    Base.metadata.create_all(driver.engine)
