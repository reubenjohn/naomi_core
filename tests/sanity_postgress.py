import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

# Create a table
with engine.connect() as connection:
    connection.execute(
        text(
            """
    CREATE TABLE IF NOT EXISTS _dummy (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100)
    )
    """
        )
    )
    connection.commit()

# Insert a record
with engine.connect() as connection:
    connection.execute(
        text(
            """
    INSERT INTO _dummy (name, email) VALUES ('John Doe', 'john.doe@example.com')
    """
        )
    )
    connection.commit()

# Query the table
with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM _dummy"))
    for row in result:
        print(row)

# Drop the table
with engine.connect() as connection:
    connection.execute(text("DROP TABLE _dummy"))
    connection.commit()
