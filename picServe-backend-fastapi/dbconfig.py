import aiomysql
from contextlib import asynccontextmanager

mysql_pool=None

async def init_db_pool():
    global mysql_pool
    mysql_pool=await aiomysql.create_pool(
        host="localhost",
        port=3306,
        user="root",
        password="kiran",
        db="photography_platform",
        autocommit=True,
        minsize=1,
        maxsize=5
    )

async def close_db_pool():
    global mysql_pool
    if mysql_pool:
        mysql_pool.close()
        await mysql_pool.wait_closed()

@asynccontextmanager
async def get_db_conn():
    async with mysql_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            yield cursor,conn


