import os

import pandas as pd
import sqlalchemy

DB_STRINGS = [
    "postgresql://postgres:password@postgres_test_base/postgres",
    "mysql+pymysql://root:password@mysql_test_base/test_db",
]

TEST_TABLES_DUMPS = ["test_data.csv"]


if __name__ == "__main__":

    for db_string in DB_STRINGS:
        # Replace URL in alembic config
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

        engine = sqlalchemy.create_engine(db_string)

        for dump in TEST_TABLES_DUMPS:
            dump = "test_data/" + dump
            df = pd.read_csv(dump)
            for column in df.columns:
                if "bool" in column:
                    df[column] = df[column].astype(bool)

            df.to_sql("test_table_1", con=engine, if_exists="append", index=False)
