from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


from .modules import *  # noqa: F40*
from .secrets import *  # noqa: F40*
