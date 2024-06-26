#  Copyright (c) 2024 Mira Geoscience Ltd.
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

import numpy as np

from .cell_object import CellObject
from .object_base import ObjectType


class Surface(CellObject):
    """
    Surface object defined by vertices and cells
    """

    __TYPE_UID = uuid.UUID(
        fields=(0xF26FEBA3, 0xADED, 0x494B, 0xB9, 0xE9, 0xB2BBCBE298E1)
    )

    def __init__(
        self,
        object_type: ObjectType,
        vertices: np.ndarray = tuple([[0.0, 0.0, 0.0]] * 3),
        cells: np.ndarray | list | tuple = (0, 1, 2),
        **kwargs,
    ):
        super().__init__(object_type, cells=cells, vertices=vertices, **kwargs)

    @property
    def cells(self) -> np.ndarray:
        """
        Array of vertices index forming triangles
        :return cells: :obj:`numpy.array` of :obj:`int`, shape ("*", 3)
        """
        if self._cells is None and self.on_file:
            self._cells = self.workspace.fetch_array_attribute(self, "cells")

        return self._cells

    @classmethod
    def default_type_uid(cls) -> uuid.UUID:
        return cls.__TYPE_UID

    def validate_cells(self, indices: list | tuple | np.ndarray | None):
        if isinstance(indices, (tuple | list)):
            indices = np.array(indices, ndmin=2)

        if not isinstance(indices, np.ndarray):
            raise AttributeError(
                "Attribute 'cells' must be provided as type numpy.ndarray, list or tuple."
            )

        if indices.ndim != 2 or indices.shape[-1] != 3:
            raise ValueError("Array of 'cells' should be of shape (*, 3).")

        if not np.issubdtype(indices.dtype, np.integer):
            raise TypeError("Indices array must be of integer type")

        return indices.astype(np.int32)

    @classmethod
    def validate_vertices(cls, xyz: np.ndarray | list | tuple) -> np.ndarray:
        """
        Validate and format type of vertices array.

        :param xyz: Array of vertices as defined by :obj:`~geoh5py.objects.points.Points.vertices`.
        """
        xyz = super().validate_vertices(xyz)

        if len(xyz) < 3:
            raise ValueError("Surface must have at least three vertices.")

        return xyz
