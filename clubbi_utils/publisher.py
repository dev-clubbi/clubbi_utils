from asyncio import Protocol
from typing import Any, Optional, Dict


class Publisher(Protocol):
    async def publish(self, message: Any, attributes: Optional[Dict[str, str]] = None) -> None:
        """Protocol function"""
