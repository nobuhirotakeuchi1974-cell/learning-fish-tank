from sqlmodel import SQLModel, create_engine, Session

DB_URL = "sqlite:///./fish_tank.db"
engine = create_engine(DB_URL, echo=False)

def init_db():
    from . import models  # noqa: F401
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
