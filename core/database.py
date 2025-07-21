from aiosqlite import connect as db_connect

async def create_tables():
    async with db_connect("brounis.db") as conn:
        await conn.executescript(open("./sql/create_tables.sql").read())
