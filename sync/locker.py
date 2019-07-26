import asyncio
from collections import defaultdict
from functools import partial


class ItemBase:
    def __init__(self, locker_factory=asyncio.Lock):
        self._locker = locker_factory()
        self._oplock = asyncio.Lock()

    @classmethod
    def _with_locker(cls, method):
        async def _wrapper(self, *args, **kwargs):
            async with self._oplock:
                return await method(self, *args, **kwargs)

        return _wrapper


class Item(ItemBase):
    @property
    def locked(self):
        return self._locker.locked()

    @ItemBase._with_locker
    async def acquire(self):
        await self._locker.acquire()

    def release(self):
        assert self.locked
        self._locker.release()

    @ItemBase._with_locker
    async def acquire_no_wait(self):
        if self.locked:
            return False

        await self._locker.acquire()

        return True


_items_factory = partial(defaultdict, Item)


class Lock:
    def __init__(self, items_factory=_items_factory):
        self._items = items_factory()

    async def acquire(self, _id):
        await self._items[_id].acquire()
        print(f'Item id={_id} acquired')

    def release(self, _id):
        try:
            self._items[_id].release()
        except AssertionError:
            print(f'Item id={_id} release failed: not locked')
        else:
            print(f'Item id={_id} released')

    async def acquire_no_wait(self, _id):
        return await self._items[_id].acquire_no_wait()
