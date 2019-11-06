from geoh5io.data import DataType, GeometricDataConstants
from geoh5io.workspace import Workspace


def test_xyz_dataype():
    the_workspace = Workspace()
    x_datatype = DataType.for_x_data(the_workspace)
    assert x_datatype.uid == GeometricDataConstants.x_datatype_uid()
    assert (
        DataType.find(the_workspace, GeometricDataConstants.x_datatype_uid())
        is x_datatype
    )
    # make sure another call does no re-create another type
    assert DataType.for_x_data(the_workspace) is x_datatype

    y_datatype = DataType.for_y_data(the_workspace)
    assert y_datatype.uid == GeometricDataConstants.y_datatype_uid()
    assert (
        DataType.find(the_workspace, GeometricDataConstants.y_datatype_uid())
        is y_datatype
    )
    # make sure another call does no re-create another type
    assert DataType.for_y_data(the_workspace) is y_datatype

    z_datatype = DataType.for_z_data(the_workspace)
    assert z_datatype.uid == GeometricDataConstants.z_datatype_uid()
    assert (
        DataType.find(the_workspace, GeometricDataConstants.z_datatype_uid())
        is z_datatype
    )
    # make sure another call does no re-create another type
    assert DataType.for_z_data(the_workspace) is z_datatype