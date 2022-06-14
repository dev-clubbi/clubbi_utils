from unittest import TestCase
from copy import copy, deepcopy
from clubbi_utils.common.undefined import UNDEFINED, Undefined


class TestUndefined(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._undefined = UNDEFINED

    def test_should_be_falsy(self):
        self.assertFalse(self._undefined)

    def test_should_equal_itself_only(self):
        self.assertEqual(self._undefined, Undefined())
        self.assertNotEqual(self._undefined, None)
        self.assertNotEqual(self._undefined, 0)
        self.assertNotEqual(self._undefined, False)

    def test_copy_should_return_itself(self):
        self.assertEqual(copy(self._undefined), self._undefined)
        self.assertEqual(deepcopy(self._undefined), self._undefined)
        self.assertEqual(deepcopy(dict(field=Undefined())), dict(field=self._undefined))

    def test_should_be_hashable(self):
        self.assertEqual(list(set((self._undefined, Undefined()))), [self._undefined])
        self.assertEqual(list(set((Undefined(), None))), [None, self._undefined])
