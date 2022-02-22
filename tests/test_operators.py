from typing import Callable, Optional
from unittest import TestCase

from clubbi_utils.operators import none_coalesce, none_assertion, ValueIsNoneError


class TestOperators(TestCase):

    def test_none_coalesce(self):
        ans = none_coalesce(1, 2, 3, default=4)
        self.assertEqual(ans, 1)
    
    def test_none_coalesce_with_single_none(self):
        ans = none_coalesce(None, 2, 3, default=4)
        self.assertEqual(ans, 2)
    
    def test_none_coalesce_with_default_non_none(self):
        ans = none_coalesce(None, None, None, default="a")
        self.assertEqual(ans, "a")
    
    def test_none_coalesce_with_default_none(self):
        ans = none_coalesce(None, None, None, default=None)
        self.assertIsNone(ans)
    
    def test_none_assertion(self):
        f: Callable[[Optional[int]], int] = lambda v: none_assertion(v)+1
        ans = f(1)
        self.assertEqual(ans, 2)

        with self.assertRaises(ValueIsNoneError):
            f(None)
        

