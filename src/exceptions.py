class EmptyDatabaseError(Exception):
    def __init__(self, ip: str, db_name: str):
        super().__init__(f"DataBase on server: {ip} db_name: {db_name} is empty")


class AdminTokenExistsError(Exception):
    def __init__(self):
        super().__init__("Admin token already exists")


class TableNotFoundError(Exception):
    def __init__(self, table_name):
        super().__init__(f'Table "{table_name}" not found')


class AccessAlreadyGrantedError(Exception):
    def __init__(self, table_name):
        super().__init__(f'Access to "{table_name}" already granted')


class DatabaseAlreadyExistsError(Exception):
    def __init__(self, local_name):
        super().__init__(f"Database with name {local_name} aleready exists")
