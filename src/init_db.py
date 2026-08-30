from pathlib import Path
from database import engine

SCHEMA_FILE = Path("sql/schema.sql")

def initialize_database():
    schema = SCHEMA_FILE.read_text(encoding="utf-8")

    with engine.begin() as connection:
        connection.exec_driver_sql(schema)

    print("db tables created")

if __name__ == "__main__":
    initialize_database()