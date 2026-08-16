import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


DATA_DIRECTORY = Path(__file__).resolve().parent
DATABASE_PATH = DATA_DIRECTORY / "payflux.db"
SCHEMA_PATH = DATA_DIRECTORY / "schema.sql"


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    Provide a configured SQLite connection.

    Every caller receives:
    - foreign-key enforcement;
    - dictionary-like row access;
    - automatic commit and connection cleanup.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def create_database() -> None:
    """
    Create the PayFlux SQLite database using schema.sql.
    """

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        connection.executescript(schema)

        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

    table_names = [table["name"] for table in tables]

    print(f"Database created at: {DATABASE_PATH}")
    print(f"Tables available: {table_names}")


if __name__ == "__main__":
    create_database()