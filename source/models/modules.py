from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import JSON
from sqlalchemy import String

from . import Base


class InstalledModules(Base):
    __tablename__ = "installed_modules"

    id = Column(String, primary_key=True)
    module_name = Column(String)
    version = Column(String)
    installation_date = Column(DateTime)
    functions_config = Column(JSON)

    def to_dict(self):
        return {
            "module_name": self.module_name,
            "version": self.version,
            "installation_date": self.installation_date.strftime("%d-%m-%Y %H:%M"),
        }
