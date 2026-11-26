from sqlalchemy import text

from src.database.connection import engine


def main():

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT current_database(), current_user")
            ).one()

            print("Database connection successful!")
            print(f"Database: {result[0]}")
            print(f"User: {result[1]}")


    except Exception as error:

        print(f"Database connection failed: {type(error).__name__}")

        print(str(error))

        raise SystemExit(1)

if __name__ == "__main__":
    main()
