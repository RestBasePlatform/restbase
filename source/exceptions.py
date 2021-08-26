class EntityAlreadyExistsException(Exception):
    def __init__(self, entity_name: str, entity_data: str):
        super(EntityAlreadyExistsException, self).__init__(f"Entity {entity_name} with name {entity_data} already exists.")
