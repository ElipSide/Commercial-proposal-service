from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, conninfo: str, min_size: int = 1, max_size: int = 30):
        self.pool = AsyncConnectionPool(conninfo, min_size=min_size, max_size=max_size, open=False)

    async def open(self):
        await self.pool.open()

    async def close(self):
        await self.pool.close()

    async def fetchrow(self, query: str, *params):
        """
        Выполняет запрос и возвращает одну строку (первую) результата.
        """
        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchone()
        
    @asynccontextmanager
    async def get_connection(self):
        async with self.pool.connection() as conn:
            yield conn

    async def execute_select_statement_non_params_prep(self, query_name):
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"EXECUTE {query_name}")
                    result = await cursor.fetchall()
        except Exception as e:
            logger.error(f"Error executing SELECT prepared statement: {query_name}")
            logger.error(e)
        return result

    async def execute_statement(self, query, params):
        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
     

    async def execute_select_statement(self, query, params = None):
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    result = await cursor.fetchall()
        except Exception as e:
            logger.error(f"Error statement: {query}")
            logger.error(e)
            return None
        return result

    async def execute_func(self, params):
        result = None
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    # await cursor.execute('public.get_file_name_contacts_or_invoice', params)
                    query = 'SELECT get_file_name_contacts_or_invoice(%s, %s, %s, %s)'
                    await cursor.execute(query, params)
                    result = await cursor.fetchone()
                    if result:
                        await conn.commit()
                        return result[0]
                    else:
                        print("ERROR.ERROR.ERROR.ERROR.ERROR.ERROR.ERROR.")
                        return None

        except Exception as e:
            logging.error("Error executing SELECT prepared statement: get_file_name_contacts_or_invoice")
            logging.error(e)

        return result

