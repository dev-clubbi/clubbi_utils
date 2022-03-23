
from unittest import TestCase

from clubbi_utils.common.iter_as_chunks import iter_as_chunks
class TestIterasChunks(TestCase):

    def test_as_chunks(self):
        self.assertEqual(list(iter_as_chunks([1,2,3,4], 2)), [[1,2], [3,4]])
    
    def test_as_chunks_odd(self):
        self.assertEqual(list(iter_as_chunks([1,2,3,4,5], 2)), [[1,2], [3,4], [5]])

        

