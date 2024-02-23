import asyncio
import traceback
from asyncio import sleep
from copy import deepcopy
from time import time
from typing import Union, Type, Optional, TypeVar

import aiosqlite

sql_connection_pool: aiosqlite.Connection

async def create_pool():
    global sql_connection_pool
    if 'sql_connection_pool' in globals():
        await sql_connection_pool.close()

    sql_connection_pool = await aiosqlite.connect('utils/db/database.db')


asyncio.get_event_loop().run_until_complete(create_pool())
A = TypeVar('A', bound='AbstractSQLObject')


async def _abstract_sql(query, *params, fetch=False, fetchall=False, last_row=False) -> Union[list, dict, int, None]:
    conn = sql_connection_pool
    cur = await conn.execute(query, params)
    await conn.commit()
    if fetchall:
        return await cur.fetchall()
    elif fetch:
        return await cur.fetchone()
    elif last_row:
        return cur.lastrowid


async def abstract_sql(*args, **kwargs):
    try:
        return await _abstract_sql(*args, **kwargs)
    except (aiosqlite.Error, BrokenPipeError, aiosqlite.OperationalError):
        old_pool = sql_connection_pool
        await create_pool()
        await old_pool.close()
        return await _abstract_sql(*args, **kwargs)


class MetaASO(type):
    _table = None
    _key_column = None

    @property
    def table(cls):
        return cls._table

    @property
    def key_column(cls):
        return cls._key_column


class AbstractSQLObject(metaclass=MetaASO):
    def __init__(self, data):
        keys = ['id', 'user_id', 'username', 'result']
        data = dict(zip(keys, data))

        self.original = deepcopy(data)
        self.original_attrs = set(data.items())
        for k, v in data.items():
            setattr(self, k, v)

    @property
    def current(self) -> dict:
        return self.__dict__.copy()

    @property
    def incremental(self) -> list[str]:
        return []

    @classmethod
    async def create_default(cls: Type[A], user_id, username) -> A:
        await abstract_sql(
            f'INSERT OR REPLACE INTO `{cls.table}` ({cls.key_column}) VALUES (?)',
            user_id)
        await abstract_sql(
            f'UPDATE users SET username=? WHERE user_id=?',
            username, user_id)
        return await cls.select(user_id)

    @classmethod
    async def select(cls: Type[A], user_id=None) -> Optional[A]:
        data = await abstract_sql(f'SELECT * FROM `{cls.table}` WHERE `{cls.key_column}`=?', user_id, fetch=True)
        if not data:
            return None
        aya = cls(data)
        return aya


class AbstractCacheManager:
    def __init__(self, loop, cache_lifetime=None):
        self.cache = {}
        self.cache_lifetime = cache_lifetime
        loop.create_task(self.update_cache())

    async def update_cache(self):
        stime = 1
        while True:
            try:
                if not self.cache_lifetime:
                    break
                if self.cache:
                    closest = min(self.cache.keys(), key=lambda x: self.cache[x][1])
                    ts = self.cache[closest][1]
                    if time() >= ts:
                        self.cache.pop(closest, None)
                        continue
                    else:
                        stime = ts - time()
                else:
                    stime = self.cache_lifetime
            except Exception:
                traceback.print_exc()
                stime = 1
            finally:
                await sleep(stime)

    def __setitem__(self, key, value):
        self.cache[key] = [value, time()]

    def __getitem__(self, item):
        self.cache[item][1] = time()
        return self.cache[item][0]

    def __contains__(self, item):
        return item in self.cache

    def __iter__(self):
        return self.cache.__iter__()