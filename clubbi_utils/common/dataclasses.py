# This is a workaround for pylance issue of not autocompleting when using
# pydantic.dataclasses.dataclass instead of BaseModel
# more info here: https://github.com/microsoft/python-language-server/issues/1898#issuecomment-743645817
from typing import TYPE_CHECKING

if TYPE_CHECKING: # pragma: no cover
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass as dataclass
