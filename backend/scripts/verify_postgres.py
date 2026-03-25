from sqlalchemy import inspect, text

from app.db import engine, get_database_url


if __name__ == '__main__':
    with engine.connect() as connection:
        connection.execute(text('select 1'))
        inspector = inspect(connection)
        tables = sorted(inspector.get_table_names())

    print('database_url', get_database_url())
    print('tables', tables)
