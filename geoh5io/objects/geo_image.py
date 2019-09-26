import uuid

from .object_base import ObjectBase, ObjectType


class GeoImage(ObjectBase):
    __TYPE_UID = uuid.UUID("{77AC043C-FE8D-4D14-8167-75E300FB835A}")

    def __init__(self, object_type: ObjectType, name: str, uid: uuid.UUID = None):
        super().__init__(object_type, name, uid)
        # TODO
        self.vertices = None

    @classmethod
    def default_type_uid(cls) -> uuid.UUID:
        return cls.__TYPE_UID
