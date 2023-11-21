import asyncio
import traceback
from asyncio import sleep
from copy import deepcopy
from time import time
from typing import Union, Type, Optional, TypeVar

import aiomysql
from pymysql import OperationalError

sql_config = {
    'host': 'rudy.zzz.com.ua',
    'user': 'anderskiy',
    'password': 'SoL_4_5-FlkJk_-0',
    'db': 'anderskiy',
    'autocommit': True
}

async def create_pool():
    global sql_connection_pool
    if 'sql_connection_pool' in globals():
        sql_connection_pool.close()
        await sql_connection_pool.wait_closed()

    sql_connection_pool = await aiomysql.create_pool(0, **sql_config)


asyncio.get_event_loop().run_until_complete(create_pool())
A = TypeVar('A', bound='AbstractSQLObject')


async def _abstract_sql(query, *params, fetch=False, fetchall=False, last_row=False) -> Union[list, dict, int, None]:
    async with sql_connection_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params)
            if fetchall:
                return await cur.fetchall()
            elif fetch:
                return await cur.fetchone()
            elif last_row:
                return cur.lastrowid


async def abstract_sql(*args, **kwargs):
    try:
        return await _abstract_sql(*args, **kwargs)
    # костыль ебаный
    except (aiomysql.InternalError, BrokenPipeError, OperationalError):
        old_pool = sql_connection_pool
        await create_pool()
        old_pool.close()
        return await _abstract_sql(*args, **kwargs)


async def abstract_fetch(fetch_all, table, keys=None, keys_values=None, fields=None,
                         raw_keys='', order_by=None, order_desc=False, limit=None, schema=None, matches_all=True):
    if keys_values is None:
        keys_values = []
    fields = f'{", ".join(fields)}' if fields else '*'
    delim = ' AND ' if matches_all else ' OR '
    keys = ' WHERE ' + delim.join([f'`{key}`=%s' for key in keys]) if keys else ''
    if not keys and raw_keys:
        keys = ' WHERE ' + raw_keys
    elif raw_keys:
        keys = keys + delim + raw_keys
    table = f'`{table}`' if not schema else f'`{schema}`.`{table}`'
    if order_by:
        order = f' ORDER BY {order_by}' + ' DESC' if order_desc else f' ORDER BY {order_by}'
    else:
        order = ''
    if limit:
        limit = f' LIMIT {limit}'
    else:
        limit = ''
    statement = (f"SELECT {fields} FROM {table}{keys}{order}{limit}", *keys_values)
    return await abstract_sql(*statement, fetch=True, fetchall=fetch_all)


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

        self.original = deepcopy(data)
        self.original_attrs = set(data.keys())
        for k, v in data.items():
            setattr(self, k, v)

    def flatten(self, d, parent_key='', sep='_') -> dict:
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @property
    def current(self) -> dict:
        return self.__dict__.copy()

    @property
    def incremental(self) -> list[str]:
        return []

    def apply_changed(self, changes):
        for key, change in changes:
            if key in self.incremental:
                self.original[key] += change
            else:
                self.original[key] = change

    def get_changed(self) -> tuple:
        org = self.original
        cur = self.flatten(self.current)
        res = []
        for key in self.original_attrs:
            if org[key] != cur[key]:
                if key in self.incremental:
                    res.append((key, cur[key] - org[key]))
                else:
                    res.append((key, cur[key]))
        self.apply_changed(res)
        return tuple(zip(*res)) or ()

    async def dump(self) -> bool:
        new = self.get_changed()
        if not new:
            return False
        print(new)
        changed, values = new
        changes = ', '.join(changed)
        filler = ', '.join(['%s'] * len(changed))
        updates = ', '.join(
            [f'`{change}`=`{change}`+%s' if change in self.incremental else f'`{change}`=%s' for change in changed])
        await abstract_sql(
            f'INSERT INTO `{type(self).table}` ({type(self).key_column}, {changes}) VALUES (%s, {filler}) ON DUPLICATE KEY UPDATE {updates}',
            *[getattr(self, type(self).key_column)] + list(values) * 2)
        return True

    async def force_update(self)->bool:
        new = self.get_changed()
        if not new:
            return False
        print(new)
        changed, values = new
        changes = ', '.join(changed)
        filler = ', '.join(['%s'] * len(changed))
        updates = ', '.join(
            [f'`{change}`=`{change}`+%s' if change in self.incremental else f'`{change}`=%s' for change in changed])
        await abstract_sql(
            f'UPDATE `{type(self).table}` SET {updates} WHERE {type(self).key_column} = %s',
            *list(values) + [getattr(self, type(self).key_column)])
        return True

    @classmethod
    async def create_default(cls: Type[A], user_id, username) -> A:
        await abstract_sql(
            f'INSERT INTO `{cls.table}` ({cls.key_column}) VALUES (%s) ON DUPLICATE KEY UPDATE {cls.key_column}=%s',
            user_id, user_id)
        await abstract_sql('UPDATE users SET username=%s WHERE user_id=%s', username,
                           user_id)
        return await cls.select(user_id)

    @classmethod
    async def select(cls: Type[A], user_id=None) -> Optional[A]:
        data = await abstract_sql(f'SELECT * FROM `{cls.table}` WHERE `{cls.key_column}`=%s', user_id, fetch=True)
        if not data:
            return None
        aya = cls(data)
        return aya

    @classmethod
    async def select_all(cls: Type[A]) -> list[A]:
        data = await abstract_sql(f'SELECT * FROM `{cls.table}`', fetchall=True)
        return [cls(item) for item in data]


class NestedAbstractSQLObject(AbstractSQLObject):
    def __init__(self, data):
        super().__init__({})
        self.original = deepcopy(data)
        self.original_attrs = set(data.keys())
        nested = self.nest_dict(data)
        for k, v in nested.items():
            setattr(self, k, v)

    def nest_dict(self, flat) -> dict:
        result = {}
        for k, v in flat.items():
            self._nest_dict_rec(k, v, result)
        return result

    def _nest_dict_rec(self, k, v, out):
        k, *rest = k.split('_', 1)
        if rest:
            self._nest_dict_rec(rest[0], v, out.setdefault(k, {}))
        else:
            out[k] = v


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
            except Exception as e:
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