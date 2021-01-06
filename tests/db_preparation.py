import os


DB_STRINGS = ["postgresql://postgres:password@postgres_test_base/postgres"]


if __name__ == "__main__":
    for db_string in DB_STRINGS:
        # Replace URL in alebic config
        with open("alembic_test_db/alembic.ini") as f:
            file_data = f.read()

        file_data = file_data.replace("%URL%", db_string)

        with open("alembic_test_db/alembic.ini", "w") as f:
            f.write(file_data)

        # Run migration
        os.chdir("alembic_test_db")
        os.system("alembic upgrade head")

        os.chdir("../")

        # Replace back
        with open("alembic_test_db/alembic.ini") as f:
            file_data = f.read()

        file_data = file_data.replace(db_string, "%URL%")

        with open("alembic_test_db/alembic.ini", "w") as f:
            f.write(file_data)
