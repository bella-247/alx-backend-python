import aiosqlite
import asyncio

async def async_fetch_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()

async def async_fetch_older_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            return await cursor.fetchall()

async def fetch_concurrently():
    all_users, older_users = await asyncio.gather(
        async_fetch_users(), async_fetch_older_users()
    )
    print("All users: ", all_users)
    print("Users older than 40: ", older_users)

if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
