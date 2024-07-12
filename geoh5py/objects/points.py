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
import warnings

import numpy as np

from .object_base import ObjectBase


class Points(ObjectBase):
    """
    Points object made up of vertices.
    """

    _TYPE_UID: uuid.UUID | None = uuid.UUID("{202C5DB1-A56D-4004-9CAD-BAAFD8899406}")
    __VERTICES_DTYPE = np.dtype([("x", "<f8"), ("y", "<f8"), ("z", "<f8")])
    _default_name = "Points"

    def __init__(
        self,
        vertices: np.ndarray | list | tuple | None = None,
        **kwargs,
    ):
        self._vertices: np.ndarray = self.validate_vertices(vertices)

        super().__init__(**kwargs)

    def copy(
        self,
        parent=None,
        copy_children: bool = True,
        clear_cache: bool = False,
        mask: np.ndarray | None = None,
        **kwargs,
    ) -> Points:
        """
        Sub-class extension of :func:`~geoh5py.shared.entity.Entity.copy`.
        """
        if mask is not None and self.n_vertices:
            if not isinstance(mask, np.ndarray) or mask.shape != (self.n_vertices,):
                raise ValueError("Mask must be an array of shape (n_vertices,).")

            kwargs.update({"vertices": self.vertices[mask]})

        new_entity = super().copy(
            parent=parent,
            copy_children=copy_children,
            clear_cache=clear_cache,
            mask=mask,
            **kwargs,
        )

        return new_entity

    def remove_vertices(
        self, indices: list[int] | np.ndarray, clear_cache: bool = False
    ):
        """
        Safely remove vertices and corresponding data entries.

        :param indices: Indices of vertices to remove.
        :param clear_cache: Clear cached data and attributes.
        """
        if isinstance(indices, list):
            indices = np.array(indices)

        if not isinstance(indices, np.ndarray):
            raise TypeError("Indices must be a list or numpy array.")

        if np.max(indices) > self.vertices.shape[0] - 1:
            raise ValueError("Found indices larger than the number of vertices.")

        vertices = np.delete(self.vertices, indices, axis=0)
        self._vertices = self.validate_vertices(vertices)
        self.remove_children_values(indices, "VERTEX", clear_cache=clear_cache)
        self.workspace.update_attribute(self, "vertices")

    @property
    def vertices(self) -> np.ndarray:
        """
        Array of vertices coordinates, shape(n_vertices, 3).
        """
        if self._vertices is None and self.on_file:
            self._vertices = self.workspace.fetch_array_attribute(self, "vertices")

        return self._vertices.view("<f8").reshape((-1, 3))

    @classmethod
    def validate_vertices(cls, xyz: np.ndarray | list | tuple | None) -> np.ndarray:
        """
        Validate and format type of vertices array.

        :param xyz: Array of vertices as defined by :obj:`~geoh5py.objects.points.Points.vertices`.
        """
        if xyz is None:
            warnings.warn(
                "No 'vertices' provided. Using a default point at the origin.",
                UserWarning,
            )
            xyz = (0.0, 0.0, 0.0)

        if isinstance(xyz, (list, tuple)):
            xyz = np.array(xyz, ndmin=2)

        if not isinstance(xyz, np.ndarray):
            raise TypeError("Vertices must be a numpy array.")

        if np.issubdtype(xyz.dtype, np.number):
            if xyz.ndim != 2 or xyz.shape[-1] != 3:
                raise ValueError("Array of vertices should be of shape (*, 3).")

            xyz = np.asarray(
                np.core.records.fromarrays(
                    xyz.T.tolist(),
                    dtype=cls.__VERTICES_DTYPE,
                )
            )

        if xyz.dtype != np.dtype(cls.__VERTICES_DTYPE):
            raise ValueError(
                f"Array of 'vertices' must be of dtype = {cls.__VERTICES_DTYPE}"
            )

        return xyz
