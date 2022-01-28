import dataclasses
import os
from datetime import datetime
from decimal import Decimal
from enum import Enum

import pydantic.dataclasses
import pytz
from pydantic import BaseModel
import time

os.environ['TZ'] = 'Europe/London'
time.tzset()
TEXT_COMPLEX = "~𝘈Ḇ𝖢𝕯٤ḞԍНǏ𝙅ƘԸⲘ𝙉০Ρ𝗤Ɍ𝓢ȚЦ𝒱Ѡ𝓧ƳȤѧᖯć𝗱ễ𝑓𝙜Ⴙ𝞲𝑗𝒌ļṃŉо𝞎𝒒ᵲꜱ𝙩ừ𝗏ŵ𝒙𝒚ź1234567890!@#$%^&*()-_=+[{]};:'\",<.>/?"

LOADS_EXAMPLE = """
[{
"text": "~𝘈Ḇ𝖢𝕯٤ḞԍНǏ𝙅ƘԸⲘ𝙉০Ρ𝗤Ɍ𝓢ȚЦ𝒱Ѡ𝓧ƳȤѧᖯć𝗱ễ𝑓𝙜Ⴙ𝞲𝑗𝒌ļṃŉо𝞎𝒒ᵲꜱ𝙩ừ𝗏ŵ𝒙𝒚ź1234567890!@#$%^&*()-_=+[{]};:'\",<.>/?"
"simple_text": "tedmouiasn dsnuisad nd asdqwd"
"double": 18.1
"list": [1, 2.0, '3.0', 5.0]
"integer": 111,
}]
"""

class MyEnum(Enum):
    One = 1
    Two = 'dwsqada'


class StrEnum(str, Enum):
    A = 'asa'
    B = 'dfsadfas'
    C = '´dsadsadop;'


class IntEnum(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3


@dataclasses.dataclass
class DefaultDataclass:
    decimal: Decimal = Decimal('485445.44554544545')
    datetime: datetime = datetime(2021, 6, 21, 6, 6, 6, 666).astimezone()
    name: str = TEXT_COMPLEX
    my_enum: MyEnum = MyEnum.One
    s_enum: StrEnum = StrEnum.A
    i_enum: IntEnum = IntEnum.TWO


@pydantic.dataclasses.dataclass
class PydanticDataclass:
    decimal: Decimal = Decimal('485445.654645645')
    field_datetime: datetime = datetime(2021, 6, 21, 6, 6, 6, 666).astimezone(pytz.timezone('America/Sao_Paulo'))
    name: str = TEXT_COMPLEX
    my_enum: MyEnum = MyEnum.Two
    s_enum: StrEnum = StrEnum.B
    i_enum: IntEnum = IntEnum.ONE


class Model(BaseModel):
    decimal: Decimal = Decimal('485445.64353242314')
    field_datetime: datetime = datetime(2021, 6, 21, 6, 6, 6, 666).astimezone(pytz.timezone('America/Sao_Paulo'))
    name: str = TEXT_COMPLEX
    my_enum: MyEnum = MyEnum.Two
    s_enum: StrEnum = StrEnum.C
    i_enum: IntEnum = IntEnum.THREE


example_data = [
    dict(integer=10, double=1.765, text="Dãsq", datetime=datetime(2021, 6, 21, 6, 6, 6, 666),
         decimal=Decimal("19.6"),
         date=datetime(2021, 6, 21).date()),
    dict(test=1),
    DefaultDataclass(),
    PydanticDataclass(),
    Model(),
]

loads_to_compare = [
    dict(integer=10, double=1.765, text="Dãsq", datetime="2021-06-21T06:06:06.000666",
         decimal="19.6",
         date="2021-06-21"),
    dict(test=1),
    dict(decimal="485445.44554544545",
         datetime="2021-06-21T06:06:06.000666+01:00",
         name=TEXT_COMPLEX,
         my_enum=MyEnum.One.value,
         s_enum=StrEnum.A.value,
         i_enum=IntEnum.TWO.value),
    dict(decimal="485445.654645645",
         field_datetime="2021-06-21T02:06:06.000666-03:00",
         name=TEXT_COMPLEX,
         my_enum=MyEnum.Two.value,
         s_enum=StrEnum.B.value,
         i_enum=IntEnum.ONE.value,
         ),
    dict(decimal="485445.64353242314",
         field_datetime="2021-06-21T02:06:06.000666-03:00",
         name=TEXT_COMPLEX,
         my_enum=MyEnum.Two.value,
         s_enum=StrEnum.C.value,
         i_enum=IntEnum.THREE.value,
         )
]
