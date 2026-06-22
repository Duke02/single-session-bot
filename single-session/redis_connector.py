from typing import Any

import redis


class RedisConnector:
    """Main connection interface with Redis."""

    def __init__(self, redis_url: str, redis_port: int):
        """Creates the connection to the Redis database.

        Args:
            redis_url (str): The URL to the redis database.
            redis_port (int): The port to use to connect to the redis database.
        """
        self.redis_url: str = redis_url
        self.redis_port: int = redis_port

        self.redis_conn: redis.Redis = redis.Redis(
            host=self.redis_url, port=self.redis_port, decode_responses=True)

    def _create_hash_table(self, hash_name: str, data: dict[str, Any]):
        """Create the hash table for the given name.

        Args:
            hash_name (str): The name for the hash table.
            data (dict[str, Any]): The data to add to the hash table.
        """
        self.redis_conn.hset(name=hash_name, mapping=data)

    def _query_hash_table(self, hash_name: str, field: str) -> None | str:
        return self.redis_conn.hget(name=hash_name, key=field)

    def _get_user_hash(self, user_name: str) -> str:
        return f'USER:{user_name}'

    def get_position_for_user(self, user_name: str) -> int | None:
        """Get the position for the user in the queue.

        The position is not how many turns until that user's turn. It's an absolute value that does not change.

        Args:
            user_name (str): The ID for the user to use.

        Returns:
            int | None: If the user was added to the queue, an integer representation of the user's queue location. If the user did not add themselves to the queue, then this is None.
        """
        return self._query_hash_table(self._get_user_hash(user_name), 'position')

    def get_num_users_in_queue(self) -> int:
        """Get the current number of users within the queue.

        Returns:
            int: The number of users within the queue.
        """
        return self.redis_conn.hlen('USER')

    def add_user_to_queue(self, user: str):
        """Add the provided user to the queue.

        Args:
            user (str): The ID to use for the user.

        Raises:
            ValueError: raises error if the user is already in the table.
        """
        num_users_so_far: int = self.get_num_users_in_queue()
        if self.get_position_for_user(user) is not None:
            raise ValueError(
                f'User with name {user} is already in USER table.')
        self.redis_conn.hset(f'USER:{user}', 'position', num_users_so_far + 1)
