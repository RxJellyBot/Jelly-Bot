from extutils.arr import extract_list_action
from tests.base import TestCase

__all__ = ["TestExtractList"]


def action(data):
    for i in range(len(data)):
        data[i] = True

    return data


def action_set_value(data, value):
    for i in range(len(data)):
        data[i] = value

    return data


def action_not_mutate(_):
    return [7]


class TestExtractList(TestCase):
    def test_empty_1d(self):
        data = []
        expected = []

        self.assertEqual(extract_list_action(data, action), expected)
        self.assertEqual(data, expected)

    def test_empty_1d_with_args(self):
        data = []
        expected = []

        self.assertEqual(extract_list_action(data, action_set_value, 5), expected)
        self.assertEqual(data, expected)

    def test_empty_2d(self):
        data = [[]]
        expected = [[]]

        self.assertEqual(extract_list_action(data, action), expected)
        self.assertEqual(data, expected)

    def test_empty_2d_with_args(self):
        data = [[]]
        expected = [[]]

        self.assertEqual(extract_list_action(data, action_set_value, 5), expected)
        self.assertEqual(data, expected)

    def test_empty_3d(self):
        data = [[[]]]
        expected = [[[]]]

        self.assertEqual(extract_list_action(data, action), expected)
        self.assertEqual(data, expected)

    def test_empty_3d_with_args(self):
        data = [[[]]]
        expected = [[[]]]

        self.assertEqual(extract_list_action(data, action_set_value, 5), expected)
        self.assertEqual(data, expected)

    def test_1d(self):
        data = [False, False]
        expected = [True, True]

        self.assertEqual(extract_list_action(data, action), expected)
        self.assertEqual(data, expected)

    def test_1d_with_args(self):
        data = [False, False]
        expected = [5, 5]

        self.assertEqual(extract_list_action(data, action_set_value, 5), expected)
        self.assertEqual(data, expected)

    def test_2d_regular(self):
        data = [[False, False], [False, False]]
        expected = [[True, True], [True, True]]

        self.assertEqual(extract_list_action(data, action), expected)
        self.assertEqual(data, expected)

    def test_2d_irregular(self):
        data = [[False, False], [False, False], [False]]
        expected = [[True, True], [True, True], [True]]

        self.assertEqual(extract_list_action(data, action), expected)
        self.assertEqual(data, [[True, True], [True, True], [True]])

    def test_2d_with_args(self):
        data = [[False, False], [False, False], [False]]
        expected = [[5, 5], [5, 5], [5]]

        self.assertEqual(extract_list_action(data, action_set_value, 5), expected)
        self.assertEqual(data, expected)

    def test_3d(self):
        data = [[[False, False], [False, False]], [[False, False], [False, False]]]
        expected = [[[True, True], [True, True]], [[True, True], [True, True]]]

        self.assertEqual(extract_list_action(data, action), expected)
        self.assertEqual(data, expected)

    def test_3d_not_mutate(self):
        data = [[[False, False], [False, False]], [[False, False], [False, False]]]

        self.assertEqual(extract_list_action(data, action_not_mutate), [[[7], [7]], [[7], [7]]])
        self.assertEqual(data, [[[False, False], [False, False]], [[False, False], [False, False]]])

    def test_3d_with_args(self):
        data = [[[False, False], [False, False]], [[False, False], [False, False]]]
        expected = [[[5, 5], [5, 5]], [[5, 5], [5, 5]]]

        self.assertEqual(extract_list_action(data, action_set_value, 5), expected)
        self.assertEqual(data, expected)
