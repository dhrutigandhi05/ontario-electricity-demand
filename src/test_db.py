from sqlalchemy import text
from database import engine
from sqlalchemy import inspect
from database import engine

with engine.connect() as connection:
    result = connection.execute(
        text("SELECT version();")
    )

    print(result.scalar())

inspector = inspect(engine)
print(inspector.get_table_names())