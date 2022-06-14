from pydantic import BaseModel
from typing import Iterable, Type, TypeVar
from io import StringIO
from csv import DictWriter


T = TypeVar("T", bound=BaseModel)


def base_model_collection_to_csv(
    model_type: Type[T],
    collection: Iterable[T],
    delimiter: str = ",",
) -> str:
    """Converts a colection of BaseModels to a CSV string,
    ## Example:
    ```
    from pydantic import BaseModel
    class Foo(BaseModel):
        n: int
        s: str

    collection = [Foo(n=1, s="a"), Foo(n=2, s="b")]
    print(base_model_collection_to_csv(Foo, collection))
    # n,s
    # 1,a
    # 2,b
    ```
    Args:
        model_type (Type[BaseModel]): Specific class of the datamodel
        collection (Iterable[BaseModel]): An iterable of the basemodel specified in `model_type`
        delimiter (str, optional): Csv delimiter. Defaults to ",".

    Returns:
        str: CSV as string
    """
    if not issubclass(model_type, BaseModel):
        raise ValueError("model_type parameter must be a subclass of BaseModel")
    f = StringIO()
    writer = DictWriter(
        f=f,
        fieldnames=model_type.schema().get("properties").keys(),  # type: ignore
        delimiter=delimiter,
    )
    writer.writeheader()
    for obj in collection:
        if not isinstance(obj, model_type):
            raise ValueError(f"Each objects in collection must be of type {model_type}")
        writer.writerow(obj.dict())
    return f.getvalue()
