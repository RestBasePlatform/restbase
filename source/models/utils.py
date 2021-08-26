from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///database.db")
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    db_session = Session()
    return db_session
    # try:
    #     yield db_session
    # finally:
    #     db_session.close()
