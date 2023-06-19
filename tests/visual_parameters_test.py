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

import numpy as np

from geoh5py.data.visual_parameters import VisualParameters
from geoh5py.objects import Points
from geoh5py.workspace import Workspace


def test_visual_parameters(tmp_path):
    name = "MyTestPointset"

    # Generate a random cloud of points with reference values
    n_data = 12
    h5file_path = tmp_path / r"testTextData.geoh5"

    with Workspace(h5file_path) as workspace:
        points = Points.create(
            workspace,
            vertices=np.random.randn(n_data, 3),
            name=name,
            allow_move=False,
        )
        assert isinstance(points.visual_parameters, VisualParameters)

        # Test color setter and round-trip transform
        new_colour = np.random.randint(0, 255, (3,)).tolist()
        points.visual_parameters.colour = new_colour

        assert points.visual_parameters.colour == new_colour

        # Test copying object with visual parameters
        copy = points.copy()

        assert copy.visual_parameters.colour == points.visual_parameters.colour
