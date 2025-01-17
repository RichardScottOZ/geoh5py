#  Copyright (c) 2021 Mira Geoscience Ltd.
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

import tempfile
from pathlib import Path

from geoh5py.groups import ContainerGroup
from geoh5py.objects import Points
from geoh5py.workspace import Workspace


def test_create_point_data():

    with tempfile.TemporaryDirectory() as tempdir:
        h5file_path = Path(tempdir) / r"test.geoh5"
        workspace = Workspace(h5file_path)
        group = ContainerGroup.create(workspace, parent=None)
        assert (
            group.parent == workspace.root
        ), "Assigned parent=None should default to Root."

        group = ContainerGroup.create(workspace)
        assert (
            group.parent == workspace.root
        ), "Creation without parent should default to Root."

        points = Points.create(workspace, parent=group)

        assert points.parent == group, "Parent setter did not work."
