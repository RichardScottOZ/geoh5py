#  Copyright (c) 2022 Mira Geoscience Ltd.
#
#  This file is part of geoh5py.
#
#  geoh5py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  geoh5py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with geoh5py.  If not, see <https://www.gnu.org/licenses/>.
#
#  This file is part of geoh5py.
#
#  geoh5py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  geoh5py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with geoh5py.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import uuid

from geoh5py.shared import Entity, EntityType


class ConcatenatorEntity(Entity):
    """
    Concatenation of objects and data.
    This group is not registered to the workspace and only visible to the parent object.
    Currently, only used by the DrillholeGroup
    """

    _attribute_map = Entity._attribute_map.copy()
    _attribute_map.update(
        {
            "Attributes": "attributes",
            "Property Groups IDs": "property_group_ids",
            "Concatenated object IDs": "concatenated_object_ids",
            "Concatenated Data": "concatenated_data",
        }
    )

    def __init__(self, **kwargs):
        self._concatenated_data = None
        self._concatenated_object_ids = None
        self._property_group_ids = None
        self._attributes = None

        super().__init__(**kwargs)

    @classmethod
    def default_type_uid(cls) -> uuid.UUID | None:
        ...

    @property
    def attribute_map(self) -> dict:
        """
        :obj:`dict` Attribute names mapping between geoh5 and geoh5py
        """
        return self._attribute_map

    @property
    def attributes(self):
        """Dictionary of concatenated objects and data attributes."""
        return self._attributes

    @attributes.setter
    def attributes(self, attr: dict):
        if not isinstance(attr, dict):
            raise AttributeError("Input value for 'attributes' must be of type dict.")

        self._attributes = attr

    @property
    def concatenated_object_ids(self):
        """Dictionary of concatenated objects and data concatenated_object_ids."""
        if getattr(self, "_concatenated_object_ids", None) is None:
            self.workspace.fetch_concatenated_data(
                self.uid, "Group", "Concatenated object IDs"
            )
        return self._concatenated_object_ids

    @concatenated_object_ids.setter
    def concatenated_object_ids(self, object_ids: list[uuid.UUID]):
        if not isinstance(object_ids, list):
            raise AttributeError(
                "Input value for 'concatenated_object_ids' must be of type list."
            )

        self._concatenated_object_ids = object_ids

    @property
    def entity_type(self) -> EntityType:
        ...

    @property
    def property_group_ids(self):
        """Dictionary of concatenated objects and data property_group_ids."""
        if getattr(self, "_property_group_ids", None) is None:
            self.workspace.fetch_concatenated_data(
                self.uid, "Group", "Property Group IDs"
            )
        return self._property_group_ids

    @property_group_ids.setter
    def property_group_ids(self, object_ids: list[uuid.UUID]):
        if not isinstance(object_ids, list):
            raise AttributeError(
                "Input value for 'property_group_ids' must be of type list."
            )

        self._property_group_ids = object_ids
