#  Copyright (c) 2023 Mira Geoscience Ltd.
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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import numpy as np

from ..data import Data
from .points import Points

if TYPE_CHECKING:
    from geoh5py.objects import ObjectType


class CellObject(Points, ABC):
    """
    Base class for object with cells.
    """

    _attribute_map: dict = Points._attribute_map.copy()

    def __init__(self, object_type: ObjectType, name="Object", **kwargs):
        self._cells: np.ndarray | None = None

        super().__init__(object_type, name=name, **kwargs)

    @classmethod
    @abstractmethod
    def default_type_uid(cls) -> uuid.UUID:
        """Default type uid."""

    def remove_cells(self, indices: list[int] | np.ndarray, clear_cache: bool = False):
        """
        Safely remove cells and corresponding data entries.

        :param indices: Indices of cells to be removed.
        :param clear_cache: Clear cache of data values.
        """

        if self._cells is None:
            warnings.warn("No cells to be removed.", UserWarning)
            return

        if (
            isinstance(self.cells, np.ndarray)
            and np.max(indices) > self.cells.shape[0] - 1
        ):
            raise ValueError("Found indices larger than the number of cells.")

        # Pre-load data values
        for child in self.children:
            if isinstance(child, Data):
                getattr(child, "values")

        cells = np.delete(self.cells, indices, axis=0)
        self._cells = None
        setattr(self, "cells", cells)

        self.remove_children_values(indices, "CELL", clear_cache=clear_cache)

    def remove_vertices(self, indices: list[int], clear_cache: bool = False):
        """
        Safely remove vertices and cells and corresponding data entries.

        :param indices: Indices of vertices to be removed.
        :param clear_cache: Clear cache of data values.
        """

        if self.vertices is None:
            warnings.warn("No vertices to be removed.", UserWarning)
            return

        if (
            isinstance(self.vertices, np.ndarray)
            and np.max(indices) > self.vertices.shape[0] - 1
        ):
            raise ValueError("Found indices larger than the number of vertices.")

        vert_index = np.ones(self.vertices.shape[0], dtype=bool)
        vert_index[indices] = False
        vertices = self.vertices[vert_index, :]

        # Pre-load data values
        for child in self.children:
            if isinstance(child, Data):
                getattr(child, "values")

        self._vertices = None
        setattr(self, "vertices", vertices)
        self.remove_children_values(indices, "VERTEX", clear_cache=clear_cache)

        new_index = np.ones_like(vert_index, dtype=int)
        new_index[vert_index] = np.arange(self.vertices.shape[0])
        self.remove_cells(np.where(~np.all(vert_index[self.cells], axis=1)))
        setattr(self, "cells", new_index[self.cells])

    def copy(
        self,
        parent=None,
        copy_children: bool = True,
        clear_cache: bool = False,
        mask: list[float] | np.ndarray | None = None,
        cell_mask: list[float] | np.ndarray | None = None,
        **kwargs,
    ):
        """
        Function to copy an entity to a different parent entity.

        :param parent: New parent for the copied object.
        :param copy_children: Copy children entities.
        :param clear_cache: Clear cache of data values.
        :param mask: Array of indices to sub-sample the input entity.
        :param cell_mask: Array of indices to sub-sample the input entity cells.
        :param kwargs: Additional keyword arguments.

        :return: New copy of the input entity.
        """

        if parent is None:
            parent = self.parent

        if mask is not None and self.vertices is not None:
            if not isinstance(mask, np.ndarray) or mask.shape != (
                self.vertices.shape[0],
            ):
                raise ValueError("Mask must be an array of shape (n_vertices,).")

            kwargs.update({"vertices": self.vertices[mask, :]})

        if self.cells is not None and mask is not None:
            if cell_mask is None:
                cell_mask = np.all(mask[self.cells], axis=1)

            new_id = np.ones_like(mask, dtype=int)
            new_id[mask] = np.arange(np.sum(mask))
            new_cells = new_id[self.cells]
            new_cells = new_cells[cell_mask, :]
            kwargs.update(
                {
                    "cells": new_cells,
                }
            )
        else:
            cell_mask = None

        new_object = self.workspace.copy_to_parent(
            self,
            parent,
            clear_cache=clear_cache,
            **kwargs,
        )

        if copy_children:
            children_map = {}
            for child in self.children:
                if isinstance(child, Data) and child.association is not None:
                    if child.name in ["A-B Cell ID", "Transmitter ID"]:
                        continue

                    child_copy = child.copy(
                        parent=new_object,
                        clear_cache=clear_cache,
                        mask=cell_mask if child.association.name == "CELL" else mask,
                    )
                else:
                    child_copy = self.workspace.copy_to_parent(
                        child, new_object, clear_cache=clear_cache
                    )
                children_map[child.uid] = child_copy.uid

            if self.property_groups:
                self.workspace.copy_property_groups(
                    new_object, self.property_groups, children_map
                )
                new_object.workspace.update_attribute(new_object, "property_groups")

        return new_object
