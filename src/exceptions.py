class EmptyDatabaseError(Exception):
    def __init__(self, ip: str, db_name: str):
        super().__init__(f"DataBase on server: {ip} db_name: {db_name} is empty")


class AdminTokenExistsError(Exception):
    def __init__(self):
        super().__init__("Admin token already exists")
