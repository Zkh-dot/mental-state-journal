""""sql database model for communication with the SQLite database"""

import aiosqlite
import asyncio, nest_asyncio
import os
import bcrypt
from singleton_logger import Logger

logger = Logger().get_logger()

def async_to_sync(future, as_task=True):
    """
    A better implementation of `asyncio.run`.

    :param future: A future or task or call of an async method.
    :param as_task: Forces the future to be scheduled as task (needed for e.g. aiohttp).
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no event loop running:
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(loop.create_task(future))
    else:
        nest_asyncio.apply(loop)
        return loop.run_until_complete(loop.create_task(future))

class sql_connection:
    """class to handle sql connection: open, create tables, close"""
    def __init__(self, db_link: str = "sqlite.db"):
        self._db_link = db_link
        async_to_sync(self.connect_sql())

    async def connect_sql(self):
        """
        Connect to the SQLite database. Need to be called before any other method.
        """
        if not os.path.isfile(self._db_link):
            self.sql = await aiosqlite.connect(self._db_link)
            await self.sql.executescript(f"""CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                );
                CREATE TABLE salt (
                    id INTEGER PRIMARY KEY,
                    salt BLOB NOT NULL
                );
                CREATE TABLE journal (
                    id INTEGER PRIMARY KEY,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                    line_mark INTEGER DEFAULT 0,
                    line_text TEXT NOT NULL,
                    line_time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
                    """
            )  
            await self.sql.commit()
            logger.debug("commited")
        self.sql = await aiosqlite.connect(self._db_link)
        logger.info("sql connection opened")
    
    def __str__(self) -> str:
        return self._db_link

    async def close_sql(self):
        """
        Close the SQLite database connection.
        """
        await self.sql.close()
        logger.info("sql connection closed")

    def __del__(self):
        async_to_sync(self.close_sql())


class salt_table:
    def __init__(self, db_link: str = "sqlite.db") -> None:
        self._sql = sql_connection(db_link)

    async def add_salt(self, user_id: int, salt: bytes) -> bool:
        """
        Add a salt to the database.

        :param user_id: The user ID of the salt.
        :param salt: The salt.
        """
        await self._sql.sql.execute("INSERT INTO salt (id, salt) VALUES (?, ?)", (user_id, salt))
        await self._sql.sql.commit()
        logger.info(f"Added salt for user {user_id}")
        return True
    
    async def get_salt(self, user_id: int) -> bytes:
        """
        Get the salt from the database.
        
        :param user_id: The user ID of the salt.
        :return: The salt.
        """
        async with self._sql.sql.execute("SELECT salt FROM salt WHERE id = ?", (user_id,)) as cursor:
            return (await cursor.fetchone())[0]
        

class user_table:
    def __init__(self, db_link: str = "sqlite.db") -> None:
        self._sql = sql_connection(db_link)
        self._salt_table = salt_table(db_link)

    async def add_user(self, username: str, password: str, user_id: int = None,) -> bool:
        """
        Add a new user to the database.

        :param username: The username of the new user.
        :param password: The password of the new user.
        :param user_id: The user ID of the new user.
        """
        if user_id is None:
            user_id = hash(username)
        salt = bcrypt.gensalt()
        self._salt_table.add_salt(user_id, salt)
        password = bcrypt.hashpw(password.encode("utf-8"), salt)
        
        await self._sql.sql.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", (user_id, username, password))
        await self._sql.sql.commit()
        logger.info(f"Added user {username}")
        return True

    async def get_user(self, username: str = None, user_id: int = None):
        """
        Get a user from the database.

        :param username: The username of the user.
        :param user_id: The user ID of the user.
        :return: The user.
        """
        if username is not None:
            async with self._sql.sql.execute("SELECT id, username FROM users WHERE username = ?", (username,)) as cursor:
                return await cursor.fetchone()
        elif user_id is not None:
            async with self._sql.sql.execute("SELECT id, username FROM users WHERE id = ?", (user_id,)) as cursor:
                return await cursor.fetchone()
        else:
            return None
        
    async def check_password(self, password: str, id: int) -> bool:
        """
        Check if the password is correct.

        :param password: The password to check.
        :param id: The user ID of the user.
        :param username: The username of the user.
        :return: True if the password is correct, False otherwise.
        """
        async with self._sql.sql.execute("SELECT password FROM users WHERE id = ?", (id,)) as cursor:
            db_password = (await cursor.fetchone())[0]
        async with self._sql.sql.execute("SELECT salt FROM salt WHERE id = ?", (id,)) as cursor:
            salt = (await cursor.fetchone())[0]
        
        if bcrypt.hashpw(password.encode("utf-8"), salt) == db_password:
            return True
        return False
    
    async def delete_user(self, username: str = None, user_id: int = None) -> bool: 
        """
        Delete a user from the database.

        :param username: The username of the user.
        :param user_id: The user ID of the user.
        """
        if username is not None:
            async with self._sql.sql.execute("DELETE FROM users WHERE username = ?", (username,)) as cursor:
                await cursor.fetchone()
            logger.info(f"Deleted user {username}")
            return True
        elif user_id is not None:
            async with self._sql.sql.execute("DELETE FROM users WHERE id = ?", (user_id,)) as cursor:
                await cursor.fetchone()
            logger.info(f"Deleted user {user_id}")
            return True
        return False
    
    async def update_username(self, username: str, user_id: int) -> bool:
        """
        Update a user in the database.

        :param username: The username of the user.
        :param user_id: The user ID of the user.
        """
        async with self._sql.sql.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id)) as cursor:
            await cursor.fetchone()
        logger.info(f"Updated user {username}")
        return True
    
    async def update_password(self, password: str, user_id: int) -> bool:
        """
        Update a user in the database.

        :param password: The password of the user.
        :param user_id: The user ID of the user.
        """
        salt = bcrypt.gensalt()
        self._salt_table.add_salt(user_id, salt)
        password = bcrypt.hashpw(password.encode("utf-8"), salt)
        async with self._sql.sql.execute("UPDATE users SET password = ? WHERE id = ?", (password, user_id)) as cursor:
            await cursor.fetchone()
        logger.info(f"Updated user {user_id}")
        return True
    

class journal_table:
    def __init__(self) -> None:
        self._sql = sql_connection()

    def __del__(self):
        async_to_sync(self._sql.close_sql())
    
    