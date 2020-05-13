from abc import abstractmethod, ABC
from typing import Tuple, Dict, Any, Type, List, final
from itertools import combinations

from bson import ObjectId

from extutils.utils import to_snake_case
from models import Model, OID_KEY
from models.exceptions import (
    RequiredKeyUnfilledError, IdUnsupportedError, ModelConstructionError, FieldKeyNotExistedError,
    JsonKeyNotExistedError, ModelUncastableError
)
from models.field.exceptions import FieldReadOnly
from tests.base import TestCase

__all__ = ["TestModel"]


# TEST: `Model` equality test with same/diff id, same/diff data, dict vs json


@final
class TestModel(ABC):
    """
    Class to test various operations on :class:`Model` exluding communication between the database.

    To use this, inherit a new class from :class:`TestModel.TestClass`.

    .. seealso::
        https://stackoverflow.com/a/25695512/11571888 to see why there's a class wrapper.
    """

    class TestClass(TestCase):
        """The class to be inherited for :class:`TestModel`."""

        @classmethod
        @abstractmethod
        def get_model_class(cls) -> Type[Model]:
            """
            Model class to be tested.
            """
            raise NotImplementedError()

        @classmethod
        def get_optional(cls) -> Dict[Tuple[str, str], Any]:
            """
            Optional keys and its corresponding values to be inserted to test.

            Key:
                - 1st element: json key name
                - 2nd element: field key name
            Value:
                Value to be inserted for testing.
            """
            return {}

        @classmethod
        def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
            """
            Default keys and its corresponding value that expect to be auto-filled or being used for test.

            Key:
                - 1st element: json key name
                - 2nd element: field key name
            Value:
                - 1st element: expected default value (auto-default)
                - 2nd element: value different from the expected one to be used for testing (manual-default)
            """
            return {}

        @classmethod
        @abstractmethod
        def get_required(cls) -> Dict[Tuple[str, str], Any]:
            """
            Required keys and its corresponding values to be inserted to test.

            Key:
                - 1st element: json key name
                - 2nd element: field key name
            Value:
                Value to be inserted for testing.
            """
            raise NotImplementedError()

        @classmethod
        def get_required_invalid(cls) -> List[Tuple[Dict[Tuple[str, str], Any], Type[ModelConstructionError]]]:
            """
            List of a tuple which contains:

            - A ``dict`` which required keys and its corresponding INVALID values.

                Key:
                    - 1st element: json key name
                    - 2nd element: field key name
                Value:
                    Value to be inserted for testing.

            - The expected :class:`ModelConstructionError`
            """
            return []

        @final
        def get_optional_key_combinations(self) -> List[Tuple[Tuple[str, str], ...]]:
            """
            Get the combinations of the optional keys with all possible counts.

            :return: combinations of the optional keys
            """
            optional_keys = self.get_optional().keys()
            ret = []

            for count in range(len(optional_keys) + 1):
                ret.extend(combinations(optional_keys, count))

            return ret

        @final
        def get_required_key_combinations(self) -> List[Tuple[Tuple[str, str], ...]]:
            """
            Get the combinations of the required keys with all possible counts except the empty combination.

            :return: combinations of the required keys
            """
            required_keys = self.get_required().keys()
            ret = []

            for count in range(1, len(required_keys) + 1):
                ret.extend(combinations(required_keys, count))

            return ret

        @final
        def get_default_key_combinations(self) -> List[Tuple[Tuple[str, str], ...]]:
            """
            Get the combinations of the default keys with all possible counts.

            :return: combinations of the default keys
            """
            default_keys = self.get_default().keys()
            ret = []

            for count in range(len(default_keys) + 1):
                ret.extend(combinations(default_keys, count))

            return ret

        @final
        def get_constructed_model(self, *, manual_default=False, including_optional=False, **jkwargs):
            """
            Get a constructed model.

            :param manual_default: use the manual default values
            :param including_optional: include all optional values
            :param jkwargs: kwargs which the key is json key
            """
            json = dict(map(lambda x: (x[0][0], x[1]), self.get_required().items()))

            if manual_default:
                json_default, _ = self._dict_to_json_field_(self.get_default())
                json.update({k: v[1] for k, v in json_default.items()})

            if including_optional:
                json_optional, _ = self._dict_to_json_field_(self.get_optional())
                json.update(json_optional)

            json.update(jkwargs)

            return self.get_model_class().cast_model(json)

        @staticmethod
        @final
        def _dict_to_json_field_(d: Dict[Tuple[str, str], Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            """
            Process ``d`` to return a ``dict`` with json key (1st returned element)
            and the other ``dict`` with field key.

            :param d: `dict` to be processed
            :return: data dict with json key & data dict with field key
            """
            dict_json = {}
            dict_field = {}

            for k, v in d.items():
                jk, fk = k
                dict_json[jk] = dict_field[fk] = v

            return dict_json, dict_field

        def test_model_construct_valid(self):
            """
            Test if the model can be successfully constructed with different key combinations.

            If the construction passed, test if the content is the expected.
            """
            default_val = self.get_default()
            optional = self.get_optional()

            for optional_keys in self.get_optional_key_combinations():
                # Get required dict
                expected_json, expected_field = self._dict_to_json_field_(self.get_required())

                # Insert all optionals
                for opk in optional_keys:
                    jk, fk = opk
                    expected_json[jk] = expected_field[fk] = optional[opk]

                # Get default keys to manually fill
                for manual_defaults in self.get_default_key_combinations():
                    for dfk in default_val.keys():
                        jk, fk = dfk
                        auto_default, manual_default = default_val[dfk]

                        if dfk in manual_defaults:
                            expected_json[jk] = expected_field[fk] = manual_default
                        else:
                            expected_json[jk] = expected_field[fk] = auto_default

                    actual_json_cast = self.get_model_class().cast_model(expected_json).to_json()
                    actual_json_init = self.get_model_class()(**expected_json, from_db=True).to_json()
                    actual_field = self.get_model_class()(**expected_field).to_json()

                    with self.subTest(
                            expected=expected_json, actual_json_cast=actual_json_cast,
                            actual_json_init=actual_json_init, actual_field=actual_field):
                        self.assertDictEqual(actual_json_cast, expected_json)
                        self.assertDictEqual(actual_json_init, expected_json)
                        self.assertDictEqual(actual_field, expected_json)

        def test_model_construct_invalid(self):
            for init_dict, expected_error in self.get_required_invalid():
                init_json, init_field = self._dict_to_json_field_(init_dict)

                with self.subTest(init_json=init_json, expected_error=expected_error):
                    with self.assertRaises(expected_error):
                        self.get_model_class()(**init_json, from_db=True)
                with self.subTest(init_field=init_field, expected_error=expected_error):
                    with self.assertRaises(expected_error):
                        self.get_model_class()(**init_field, from_db=False)

        def test_model_construct_missing_required(self):
            for required_keys in self.get_required_key_combinations():
                # Generate a required dict
                required = self.get_required()

                # Remove some required keys
                for rk in required_keys:
                    del required[rk]

                # Initialize dict to construct the model
                init_dict_json, init_dict_field = self._dict_to_json_field_(required)

                # Test for the expected error
                with self.assertRaises(RequiredKeyUnfilledError):
                    self.get_model_class()(**init_dict_field, from_db=False)
                with self.assertRaises(RequiredKeyUnfilledError):
                    self.get_model_class()(**init_dict_json, from_db=True)

        def test_contains_oid(self):
            # Initialized model should **NOT** contain OID
            mdl = self.get_constructed_model()
            self.assertIsNone(mdl.get_oid())

        def test_set_oid(self):
            mdl = self.get_constructed_model()

            oid = ObjectId()
            if self.get_model_class().WITH_OID:
                mdl.id = oid
                self.assertEquals(mdl.id, oid)

                oid = ObjectId()
                mdl.set_oid(oid)
                self.assertEquals(mdl.id, oid)
            else:
                with self.assertRaises(IdUnsupportedError):
                    mdl.id = oid
                with self.assertRaises(IdUnsupportedError):
                    mdl.set_oid(oid)

        def test_init_with_oid(self):
            json = self.get_constructed_model().to_json()
            json[OID_KEY] = ObjectId()

            if self.get_model_class().WITH_OID:
                mdl = self.get_model_class()(**json, from_db=True)

                self.assertEquals(mdl.to_json(), json)
            else:
                with self.assertRaises(IdUnsupportedError):
                    self.get_model_class()(**json, from_db=True)

        def test_init_non_exist(self):
            init_json, init_field = self._dict_to_json_field_(self.get_required())
            init_json["absolutely_not_a_field"] = 7
            init_field["AbsolutelyNotAField"] = 7

            with self.assertRaises(JsonKeyNotExistedError):
                self.get_model_class()(**init_json, from_db=True)
            with self.assertRaises(FieldKeyNotExistedError):
                self.get_model_class()(**init_field, from_db=False)

        def test_set_non_exist(self):
            mdl = self.get_constructed_model(manual_default=True, including_optional=True)

            with self.assertRaises(FieldKeyNotExistedError):
                mdl.absolutely_not_a_field = 7
            with self.assertRaises(JsonKeyNotExistedError):
                mdl["abs_n_field"] = 7

        def test_set_value(self):
            for dk, dv in self.get_default().items():
                # Unpack values
                jk, fk = dk
                auto, manual = dv

                # Set by field key
                mdl = self.get_constructed_model(including_optional=True)

                with self.subTest(fk=fk, jk=jk, manual=manual):
                    try:
                        setattr(mdl, to_snake_case(fk), manual)
                    except FieldReadOnly:
                        self.skipTest(f"Field key <{fk}> is readonly.")

                    self.assertEquals(getattr(mdl, to_snake_case(fk)), manual)
                    self.assertEquals(mdl[jk], manual)

                # Set by json key
                mdl = self.get_constructed_model(including_optional=True)

                with self.subTest(fk=fk, jk=jk, manual=manual):
                    try:
                        mdl[jk] = manual
                    except FieldReadOnly:
                        self.skipTest(f"Json key <{fk}> is readonly.")

                    self.assertEquals(getattr(mdl, to_snake_case(fk)), manual)
                    self.assertEquals(mdl[jk], manual)

        def test_get_non_exist(self):
            mdl = self.get_constructed_model(manual_default=True, including_optional=True)

            with self.assertRaises(FieldKeyNotExistedError):
                _ = getattr(mdl, "absolutely_not_a_field")
            with self.assertRaises(JsonKeyNotExistedError):
                _ = mdl["abs_n_field"]

        def test_get_value(self):
            for dk, dv in self.get_default().items():
                # Unpack values
                jk, fk = dk
                auto, manual = dv

                # Test get value
                mdl = self.get_constructed_model(including_optional=True)

                with self.subTest(fk=fk, jk=jk, auto=auto):
                    self.assertEquals(getattr(mdl, to_snake_case(fk)), auto)
                    self.assertEquals(mdl[jk], auto)

        def test_cast_model_none(self):
            self.assertIsNone(self.get_model_class().cast_model(None))

        def test_cast_model_non_mutabble_mapping(self):
            with self.assertRaises(ModelUncastableError):
                self.get_model_class().cast_model(1)
            with self.assertRaises(ModelUncastableError):
                self.get_model_class().cast_model(False)

        def test_cast_constructed_model(self):
            mdl_to_cast = self.get_constructed_model()
            mdl_casted = self.get_model_class().cast_model(mdl_to_cast)
            self.assertEquals(mdl_casted.to_json(), mdl_to_cast.to_json())

        def test_cast_model_additional_fields(self):
            expected_mdl_dict = self.get_constructed_model()
            dict_to_cast = self.get_constructed_model().to_json()
            dict_to_cast["abs_n_field"] = "$(*#^%(#^"

            actual_mdl_dict = self.get_model_class().cast_model(dict_to_cast)

            self.assertEquals(actual_mdl_dict, expected_mdl_dict)
