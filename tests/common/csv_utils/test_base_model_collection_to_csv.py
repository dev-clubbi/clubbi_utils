from unittest import IsolatedAsyncioTestCase
from pydantic import BaseModel

from clubbi_utils.common.csv_utils.base_model_collection_to_csv import base_model_collection_to_csv


class Model1(BaseModel):
    n: int
    s: str


class Model2(BaseModel):
    test: str


class TestBaseModelCollectionToCsv(IsolatedAsyncioTestCase):
    async def test_successful_conversion(self):
        collection = [Model1(n=1, s="a"), Model1(n=2, s="b")]
        self.assertEqual(base_model_collection_to_csv(Model1, collection), "n,s\r\n1,a\r\n2,b\r\n")

    async def test_invalid_collection(self):
        collection = [Model2(test="hi")]
        with self.assertRaises(ValueError) as e:
            base_model_collection_to_csv(Model1, collection)

        self.assertEqual(
            e.exception.args[0],
            "Each objects in collection must be of type <class 'csv_utils.test_base_model_collection_to_csv.Model1'>",
        )

    async def test_invalid_model_type(self):
        with self.assertRaises(ValueError) as e:
            base_model_collection_to_csv(dict, [])  # type: ignore

        self.assertEqual(
            e.exception.args[0],
            "model_type parameter must be a subclass of BaseModel",
        )

    async def test_empty_collection(self):
        self.assertEqual(base_model_collection_to_csv(Model1, []), "n,s\r\n")
