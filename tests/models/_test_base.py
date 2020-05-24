from abc import abstractmethod, ABC
from typing import Tuple, Dict, Any, Type, List, final, Set
from itertools import combinations

from bson import ObjectId

from extutils.utils import to_snake_case
from models import Model, OID_KEY, ModelDefaultValueExt
from models.exceptions import (
    IdUnsupportedError, ModelConstructionError, FieldKeyNotExistError, JsonKeyNotExistedError, ModelUncastableError
)
from models.field.exceptions import FieldReadOnlyError
from tests.base import TestCase

__all__ = ["TestModel"]


class DummyModel(Model):
    pass


@final
class TestModel(ABC):
    """
    Class to test various operations on :class:`Model` exluding communication between the database.

    To use this, inherit a new class from :class:`TestModel.TestClass`.

    Default value of the fields will be validated at the beginning of the tests.
    If the validation failed, the test will **NOT** execute.

    Configure class variable ``KEY_SKIP_CHECK`` and ``KEY_SKIP_CHECK_INVALID``
    to set the keys to bypass the validation.

    .. seealso::
        https://stackoverflow.com/a/25695512/11571888 to see why there's a class wrapper.
    """

    class TestClass(TestCase):
        """The class to be inherited for :class:`TestModel`."""

        KEY_SKIP_CHECK: Set[Tuple[str, str]] = set()
        """Keys ``(Json, Field)`` to bypass the field default value validation."""

        KEY_SKIP_CHECK_INVALID: Set[Tuple[str, str]] = set()
        """Keys ``(Json, Field)`` to bypass the field default value validation for invalid model construction."""

        @classmethod
        def setUpTestClass(cls):
            cls.validate_fields()

        @classmethod
        @final
        def validate_fields(cls):
            # Validate REQUIRED
            for k in cls.get_required().keys() - cls.KEY_SKIP_CHECK:
                jk, fk = k
                fc = cls.get_model_class().get_field_class_instance(fk)
                if not fc:
                    raise AttributeError(f"Field with field key `{fk}` not exist.")

                if fc.default_value != ModelDefaultValueExt.Required:
                    raise ValueError(f"The default value of the field with field key `{fk}` "
                                     f"is not REQUIRED. @{cls.__qualname__}")

            # Validate INVALID REQUIRED
            keys = set()
            for comb in cls.get_invalid():
                init_args, exc = comb
                keys.update(init_args.keys())
            keys -= cls.KEY_SKIP_CHECK_INVALID

            for k in keys:
                jk, fk = k
                fc = cls.get_model_class().get_field_class_instance(fk)
                if not fc:
                    raise AttributeError(f"Field with field key `{fk}` not exist.")

                if fc.default_value != ModelDefaultValueExt.Required:
                    raise ValueError(f"The default value of the field with field key `{fk}` "
                                     f"is not REQUIRED. @{cls.__qualname__}")

            # Validate OPTIONAL
            for k in cls.get_optional().keys() - cls.KEY_SKIP_CHECK:
                jk, fk = k
                fc = cls.get_model_class().get_field_class_instance(fk)
                if not fc:
                    raise AttributeError(f"Field with field key `{fk}` not exist.")

                if fc.default_value != ModelDefaultValueExt.Optional:
                    raise ValueError(f"The default value of the field with field key `{fk}` "
                                     f"is not OPTIONAL. @{cls.__qualname__}")

            # Validate DEFAULT
            for k in cls.get_default().keys() - cls.KEY_SKIP_CHECK:
                jk, fk = k
                fc = cls.get_model_class().get_field_class_instance(fk)
                if not fc:
                    raise AttributeError(f"Field with field key `{fk}` not exist.")

                if ModelDefaultValueExt.is_default_val_ext(fc.default_value):
                    raise ValueError(f"The default value of the field with field key `{fk}` "
                                     f"should not be extended default value. @{cls.__qualname__}")

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

            .. note::
                - Items in this function should **NOT** change by each function call.
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

            .. note::
                - Items in this function should **NOT** change by each function call.
            """
            return {}

        @classmethod
        def get_required(cls) -> Dict[Tuple[str, str], Any]:
            """
            Required keys and its corresponding values to be inserted to test.

            Key:
                - 1st element: json key name
                - 2nd element: field key name
            Value:
                Value to be inserted for testing.

            .. note::
                - Items in this function should **NOT** change by each function call.
            """
            return {}

        @classmethod
        def get_invalid(cls) -> List[Tuple[Dict[Tuple[str, str], Any], Type[ModelConstructionError]]]:
            """
            List of a ``tuple`` which contains:

            - A ``dict`` containing the keys and its corresponding **INVALID** values to initialize the model.

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
            optional_keys = self.get_optional()
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
            required_keys = self.get_required()
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
            default_keys = self.get_default()
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
                json_default, _ = self._dict_to_json_field(self.get_default())
                json.update({k: v[1] for k, v in json_default.items()})

            if including_optional:
                json_optional, _ = self._dict_to_json_field(self.get_optional())
                json.update(json_optional)

            json.update(jkwargs)

            return self.get_model_class().cast_model(json)

        @staticmethod
        @final
        def _dict_to_json_field(d: Dict[Tuple[str, str], Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
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
                expected_json, expected_field = self._dict_to_json_field(self.get_required())

                # Insert all optionals
                for opk in optional_keys:
                    jk, fk = opk
                    expected_json[jk] = expected_field[fk] = optional[opk]

                # Get default keys to manually fill
                for manual_defaults in self.get_default_key_combinations():
                    for dfk in default_val:
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
            for init_dict, expected_error in self.get_invalid():
                init_json, init_field = self._dict_to_json_field(init_dict)

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
                init_dict_json, init_dict_field = self._dict_to_json_field(required)

                # Test for the expected error
                with self.assertRaises(ModelConstructionError):
                    self.get_model_class()(**init_dict_field, from_db=False)
                with self.assertRaises(ModelConstructionError):
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
                self.assertEqual(mdl.id, oid)

                oid = ObjectId()
                mdl.set_oid(oid)
                self.assertEqual(mdl.id, oid)
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

                self.assertEqual(mdl.to_json(), json)
            else:
                with self.assertRaises(IdUnsupportedError):
                    self.get_model_class()(**json, from_db=True)

        def test_init_non_exist(self):
            init_json, init_field = self._dict_to_json_field(self.get_required())
            init_json["absolutely_not_a_field"] = 7
            init_field["AbsolutelyNotAField"] = 7

            with self.assertRaises(JsonKeyNotExistedError):
                self.get_model_class()(**init_json, from_db=True)
            with self.assertRaises(FieldKeyNotExistError):
                self.get_model_class()(**init_field, from_db=False)

        def test_set_non_exist(self):
            mdl = self.get_constructed_model(manual_default=True, including_optional=True)

            with self.assertRaises(FieldKeyNotExistError):
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
                    except FieldReadOnlyError:
                        self.skipTest(f"Field key <{fk}> is readonly.")

                    self.assertEqual(getattr(mdl, to_snake_case(fk)), manual)
                    self.assertEqual(mdl[jk], manual)

                # Set by json key
                mdl = self.get_constructed_model(including_optional=True)

                with self.subTest(fk=fk, jk=jk, manual=manual):
                    try:
                        mdl[jk] = manual
                    except FieldReadOnlyError:
                        self.skipTest(f"Json key <{fk}> is readonly.")

                    self.assertEqual(getattr(mdl, to_snake_case(fk)), manual)
                    self.assertEqual(mdl[jk], manual)

        def test_get_non_exist(self):
            mdl = self.get_constructed_model(manual_default=True, including_optional=True)

            with self.assertRaises(FieldKeyNotExistError):
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
                    self.assertEqual(getattr(mdl, to_snake_case(fk)), auto)
                    self.assertEqual(mdl[jk], auto)

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
            self.assertEqual(mdl_casted.to_json(), mdl_to_cast.to_json())

        def test_cast_model_additional_fields(self):
            expected_mdl_dict = self.get_constructed_model()
            dict_to_cast = self.get_constructed_model().to_json()
            dict_to_cast["abs_n_field"] = "$(*#^%(#^"

            actual_mdl_dict = self.get_model_class().cast_model(dict_to_cast)

            self.assertEqual(actual_mdl_dict, expected_mdl_dict)

        def test_not_equal(self):
            # Different `Model` with same structure
            class CopiedModel(Model):
                pass

            for fk, f in zip(self.get_model_class().model_field_keys(), self.get_model_class().model_fields()):
                setattr(CopiedModel, fk, f)

            mdl = self.get_constructed_model()

            items = [
                # Unrelated different type of model
                DummyModel(),
                # Same structure but different type
                CopiedModel.cast_model(dict(map(lambda x: (x[0][0], x[1]), self.get_required().items()))),
            ]
            # Optional values available - count of keys will differ, model should/will be different
            if self.get_optional():
                items.append(self.get_constructed_model(including_optional=True))
            # Default values available - data should/will be different
            if self.get_default():
                items.append(self.get_constructed_model(manual_default=True))

            for item in items:
                with self.subTest(item=item):
                    self.assertNotEquals(item, mdl)

        def test_is_equal(self):
            items = [
                # Compare two constructed models
                (
                    "Model vs Model / R",
                    self.get_constructed_model(),
                    self.get_constructed_model()
                ),
                # Compare two constructed models with one converted to dict
                (
                    "Model vs mdl2dict / R",
                    self.get_constructed_model(),
                    self.get_constructed_model().to_json()
                ),
                # Compare constructed model and dict with required elements and replaced default values
                (
                    "Model vs dict / R + D",
                    self.get_constructed_model(manual_default=True),
                    dict({k[0]: v for k, v in self.get_required().items()},
                         **{k[0]: v[1] for k, v in self.get_default().items()})
                ),
                # Compare constructed model and dict with the manipulation of 2nd and 3rd
                (
                    "Model vs dict / R + D + O",
                    self.get_constructed_model(including_optional=True, manual_default=True),
                    dict({k[0]: v for k, v in self.get_required().items()},
                         **dict({k[0]: v[1] for k, v in self.get_default().items()},
                                **{k[0]: v for k, v in self.get_optional().items()}))
                )
            ]

            # No default value means no autofill
            if not self.get_default():
                # Compare constructed model and dict with required elements only
                items.append((
                    "Model vs dict / R",
                    self.get_constructed_model(),
                    {k[0]: v for k, v in self.get_required().items()}
                ))
                # Compare constructed model and dict with required elements and optional elements
                items.append((
                    "Model vs dict / R + O",
                    self.get_constructed_model(),
                    dict({k[0]: v for k, v in self.get_required().items()},
                         **{k[0]: v for k, v in self.get_optional().items()})
                ))

            for msg, a, b in items:
                with self.subTest(msg=msg):
                    self.assertEqual(a, b)
