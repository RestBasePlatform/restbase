class EntityAlreadyExistsException(Exception):
    def __init__(self, entity_name: str, entity_data: str):
        super().__init__(
            f"Entity {entity_name} with name {entity_data} already exists."
        )


class EntityNotFoundException(Exception):
    def __init__(self, entity_name: str, entity_data: str):
        super().__init__(f"Entity {entity_name} with name {entity_data} not found.")
