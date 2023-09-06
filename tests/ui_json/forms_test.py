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

import uuid

import pytest

from geoh5py.shared.exceptions import AggregateValidationError, TypeValidationError
from geoh5py.ui_json.enforcers import TypeEnforcer, UUIDEnforcer, ValueEnforcer
from geoh5py.ui_json.forms import (
    BoolFormParameter,
    ChoiceStringFormParameter,
    DataFormParameter,
    DataValueFormParameter,
    FileFormParameter,
    FloatFormParameter,
    FormParameter,
    IntegerFormParameter,
    ObjectFormParameter,
    StringFormParameter,
)
from geoh5py.ui_json.parameters import IntegerParameter, StringParameter


def test_form_parameter_construction_empty_value():
    param = FormParameter("my_param")
    assert param.value is None


def test_form_parameter_construction_with_value():
    param = FormParameter("my_param", value=StringParameter("value", "this"))
    assert param.value == "this"


def test_form_parameter_valid_members():
    param = FormParameter("my_param")
    valid_members = [
        "label",
        "value",
        "enabled",
        "optional",
        "group_optional",
        "main",
        "group",
        "dependency",
        "dependency_type",
        "group_dependency",
        "group_dependency_type",
        "tooltip",
    ]
    assert len(param.valid_members) == len(valid_members)
    assert all(k in valid_members for k in param.valid_members)


def test_form_parameter_active():
    param = FormParameter("my_param", value=StringParameter("value", "this"))
    assert param.active == ["value"]
    param.enabled = True
    assert param.active == ["value", "enabled"]
    param.enabled = False
    assert param.active == ["value", "enabled"]


def test_form_parameter_defaults():
    param = FormParameter("my_param")
    assert param.enabled
    assert not param.optional
    assert not param.group_optional
    assert param.main
    assert param.dependency_type == "enabled"
    assert param.group_dependency_type == "enabled"


def test_form_parameter_value_access():
    param = FormParameter("my_param", value=StringParameter("value", "this"))
    assert param.value == "this"
    assert param.enabled


def test_form_parameter_construction_with_kwargs():
    param = FormParameter(
        "my_param",
        value=StringParameter("value", "this"),
        groupOptional=True,
    )
    assert param.group_optional
    assert param._active_members == ["group_optional"]
    assert param.active == ["value", "group_optional"]


def test_form_parameter_extra_members():
    param = FormParameter("my_param", extra="stuff")
    assert param._extra_members == {"extra": "stuff"}


def test_form_parameter_aggregate_member_validations():
    msg = (
        "Validation of 'my_param' collected 2 errors:\n\t0. "
        "Type 'str' provided for 'enabled' is invalid"
    )
    with pytest.raises(AggregateValidationError, match=msg):
        _ = FormParameter(
            "my_param",
            value=StringParameter("value", "this"),
            label="my param",
            enabled="whoops",
            optional="oh-no",
        )


def test_form_parameter_roundtrip():
    form = {"label": "my param", "enabled": False, "extra": "stuff"}
    param = FormParameter("param", IntegerParameter("value", 1), **form)
    assert param.name == "param"
    assert param.label == "my param"
    assert param.value == 1
    assert not param.enabled
    assert not hasattr(param, "extra")
    assert param._extra_members["extra"] == "stuff"
    assert all(hasattr(param, k) for k in param.valid_members)
    assert param.form() == dict(form, **{"value": 1})


def test_string_form_parameter_construction():
    param = StringFormParameter(
        "my_param",
        value="this",
        label="my param",
    )
    assert param.name == "my_param"
    assert param.value == "this"
    assert param.label == "my param"
    assert param._value.validations.enforcers == [TypeEnforcer(str)]


def test_string_form_parameter_validation():
    msg = "Type 'int' provided for 'value' is invalid. Must be: 'str'."
    with pytest.raises(TypeValidationError, match=msg):
        _ = StringFormParameter(
            "my_param",
            value=1,
        )


def test_string_form_parameter_form_includes_value():
    param = StringFormParameter(
        "my_param",
        value="this",
        label="my param",
    )
    assert param.form()["value"] == "this"


def test_bool_form_parameter_construction():
    param = BoolFormParameter(
        "my_param",
        value=True,
        label="my param",
    )
    assert param.name == "my_param"
    assert param.value
    assert param.label == "my param"
    assert param._value.validations.enforcers == [TypeEnforcer(bool)]


def test_bool_form_parameter_validation():
    msg = "Type 'str' provided for 'value' is invalid. " "Must be: 'bool'."
    with pytest.raises(TypeValidationError, match=msg):
        _ = BoolFormParameter(
            "my_param",
            value="nope",
        )


def test_integer_form_parameter_construction():
    param = IntegerFormParameter(
        "my_param",
        value=1,
        label="my param",
    )
    assert param.name == "my_param"
    assert param.value == 1
    assert param.label == "my param"
    assert param._value.validations.enforcers == [TypeEnforcer(int)]
    assert param.min is None
    assert param.max is None


def test_integer_form_parameter_validation():
    msg = "Type 'str' provided for 'value' is invalid. " "Must be: 'int'."
    with pytest.raises(TypeValidationError, match=msg):
        _ = IntegerFormParameter(
            "my_param",
            value="nope",
        )


def test_float_form_parameter_construction():
    param = FloatFormParameter(
        "my_param",
        value=1.0,
        label="my param",
    )
    assert param.name == "my_param"
    assert param.value == 1
    assert param.label == "my param"
    assert param._value.validations.enforcers == [TypeEnforcer(float)]
    assert param.min is None
    assert param.max is None
    assert param.precision is None
    assert param.line_edit is None


def test_float_form_parameter_validation():
    msg = "Type 'str' provided for 'value' is invalid. " "Must be: 'float'."
    with pytest.raises(TypeValidationError, match=msg):
        _ = FloatFormParameter(
            "my_param",
            value="nope",
        )


def test_choice_string_form_parameter_construction():
    param = ChoiceStringFormParameter(
        "my_param", value="onlythis", label="my param", choice_list=["onlythis"]
    )
    assert param.name == "my_param"
    assert param.value == "onlythis"
    assert param.label == "my param"
    assert all(
        k in param._value.validations.enforcers
        for k in [ValueEnforcer(["onlythis"]), TypeEnforcer([list, str])]
    )
    assert param.choice_list == ["onlythis"]


def test_choice_string_form_parameter_validation():
    msg = (
        "Validation of 'choice_list' collected 2 errors:\n\t"
        "0. Value '1' provided for 'choice_list' is invalid. "
        "Must be: 'onlythis'.\n\t"
        "1. Type 'int' provided for 'choice_list' is invalid. "
        "Must be one of: 'list', 'str'."
    )
    with pytest.raises(AggregateValidationError, match=msg):
        _ = ChoiceStringFormParameter(
            "my_param",
            value=1,
            choice_list=["onlythis"],
        )


def test_file_form_parameter_construction():
    param = FileFormParameter(
        "my_param",
        value="my_file",
        label="my param",
    )
    assert param.name == "my_param"
    assert param.value == "my_file"
    assert param.label == "my param"
    assert param._value.validations.enforcers == [TypeEnforcer(str)]
    assert param.file_description is None
    assert param.file_type is None
    assert param.file_multi is None


def test_file_form_parameter_validation():
    msg = "Type 'int' provided for 'value' is invalid. " "Must be: 'str'."
    with pytest.raises(TypeValidationError, match=msg):
        _ = FileFormParameter(
            "my_param",
            value=1,
        )


def test_object_form_parameter_construction():
    new_uuid = str(uuid.uuid4())
    param = ObjectFormParameter(
        "my_param",
        value=new_uuid,
        label="my param",
    )
    assert param.name == "my_param"
    assert param.value == new_uuid
    assert param.label == "my param"
    assert param._value.validations.enforcers == [
        TypeEnforcer([str, uuid.UUID]),
        UUIDEnforcer(),
    ]
    assert param.mesh_type == []


def test_object_form_parameter_validation():
    msg = "Parameter 'value' with value '1' is not a valid uuid string."
    with pytest.raises(AggregateValidationError, match=msg):
        _ = ObjectFormParameter(
            "my_param",
            value=1,
        )


def test_data_form_parameter_construction():
    new_uuid = str(uuid.uuid4())
    param = DataFormParameter(
        "my_param",
        value=new_uuid,
        label="my param",
    )
    assert param.name == "my_param"
    assert param.value == new_uuid
    assert param.label == "my param"
    assert param._value.validations.enforcers == [
        TypeEnforcer([str, uuid.UUID]),
        UUIDEnforcer(),
    ]
    assert param.parent is None
    assert param.association is None
    assert param.data_type is None
    assert param.data_group_type is None


def test_data_form_parameter_validation():
    msg = "Parameter 'value' with value '1' is not a valid uuid string."
    with pytest.raises(AggregateValidationError, match=msg):
        _ = DataFormParameter(
            "my_param",
            value=1,
        )


def test_data_value_form_parameter_construction():
    new_uuid = str(uuid.uuid4())
    param = DataValueFormParameter(
        "my_param", label="my param", is_value=False, property=new_uuid
    )
    assert param.name == "my_param"
    assert param.value == new_uuid
    assert param.label == "my param"
    assert param._property.validations.enforcers == [
        TypeEnforcer([str, uuid.UUID, type(None)]),
        UUIDEnforcer("optional"),
    ]
    assert param._value.validations.enforcers == [TypeEnforcer([int, float])]
    assert param.parent is None
    assert param.association is None
    assert param.data_type is None
    assert not param.is_value


def test_data_value_form_parameter_validation():
    msg = (
        "Type 'str' provided for 'value' is invalid. " "Must be one of: 'int', 'float'."
    )
    with pytest.raises(TypeValidationError, match=msg):
        _ = DataValueFormParameter("my_param", value="uh-oh", is_value=True)
