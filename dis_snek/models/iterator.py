import asyncio
from abc import ABC, abstractmethod
from asyncio import QueueEmpty
from collections.abc import AsyncIterator as _AsyncIterator
from typing import List, Any

from dis_snek.const import MISSING, Absent
from dis_snek.models.snowflake import to_snowflake, Snowflake_Type


class AsyncIterator(_AsyncIterator, ABC):
    def __init__(self, limit: int = 50):
        self._queue: asyncio.Queue = asyncio.Queue()
        """The queue of items in the iterator"""

        self._limit: int = limit if limit else MISSING
        """the limit of items to retrieve"""

        self.last: Absent[Any] = MISSING
        """The last item retrieved"""

        self._retrieved_objects: List = []
        """All items this iterator has retrieved"""

    @property
    def _continue(self):
        if not self._limit:
            return True
        return not len(self._retrieved_objects) >= self._limit

    @property
    def get_limit(self):
        """Get how the maximum number of items that should be retrieved"""
        return min(self._limit - len(self._retrieved_objects), 100) if self._limit else 100

    async def add_object(self, obj):
        """Add an object to iterator's queue"""
        return await self._queue.put(obj)

    @abstractmethod
    async def fetch(self) -> list:
        """
        Fetch additional objects.

        Your implementation of this method *must* return a list of objects.
        If no more objects are available, raise QueueEmpty

        Returns:
            List of objects
        Raises:
              QueueEmpty when no more objects are available.
        """
        ...

    async def _get_items(self) -> None:
        if self._continue:
            data = await self.fetch()
            [await self.add_object(obj) for obj in data]
        else:
            raise QueueEmpty

    async def __anext__(self):
        try:
            if self._queue.empty():
                await self._get_items()
            self.last = self._queue.get_nowait()

            # add the message to the already retrieved objects, so that the search function works when calling it multiple times
            self._retrieved_objects.append(self.last)

            return self.last
        except QueueEmpty as e:
            raise StopAsyncIteration from e

    async def flatten(self) -> List:
        """Flatten this iterator into a list of objects"""
        return [elem async for elem in self]

    async def search(self, target_id: "Snowflake_Type") -> bool:
        """Search the iterator for an object with the given ID"""
        target_id = to_snowflake(target_id)

        if target_id in [o.id for o in self._retrieved_objects]:
            return True

        async for o in self:
            if o.id == target_id:
                return True
        return False
