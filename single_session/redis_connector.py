import os
from typing import Any

import redis


class RedisConnector:
    """Main connection interface with Redis."""

    def __init__(self, redis_url: str | None = None, redis_port: int | None = None):
        """Creates the connection to the Redis database.

        Args:
            redis_url (str): The URL to the redis database.
            redis_port (int): The port to use to connect to the redis database.
        """
        self.redis_url: str = redis_url or os.getenv("REDIS_HOST")
        self.redis_port: int = redis_port or os.getenv("REDIS_PORT")

        self.redis_conn: redis.Redis = redis.Redis(
            host=self.redis_url, port=self.redis_port, decode_responses=True
        )
        self._set_queue_index(0)

    def _create_hash_table(self, hash_name: str, data: dict[str, Any]):
        """Create the hash table for the given name.

        Args:
            hash_name (str): The name for the hash table.
            data (dict[str, Any]): The data to add to the hash table.
        """
        self.redis_conn.hset(name=hash_name, mapping=data)

    def _query_hash_table(self, hash_name: str, field: str) -> None | str:
        return self.redis_conn.hget(name=hash_name, key=field)

    def get_position_for_user(self, user_name: str) -> int | None:
        """Get the position for the user in the queue.

        The position is not how many turns until that user's turn. It's an absolute value that does not change.

        Args:
            user_name (str): The ID for the user to use.

        Returns:
            int | None: If the user was added to the queue, an integer representation of the user's queue location. If the user did not add themselves to the queue, then this is None.
        """
        pos: str | None = self._query_hash_table("USER", user_name)
        if pos:
            return int(pos)
        return None

    def get_num_users_in_queue(self) -> int:
        """Get the current number of users within the queue.

        Returns:
            int: The number of users within the queue.
        """
        return self.redis_conn.hlen("USER")

    def add_user_to_queue(self, user: str):
        """Add the provided user to the queue.

        Args:
            user (str): The ID to use for the user.

        Raises:
            ValueError: raises error if the user is already in the table.
        """
        num_users_so_far: int = self.get_num_users_in_queue()
        if self.get_position_for_user(user) is not None:
            raise ValueError(f"User with name {user} is already in USER table.")
        self.redis_conn.hset("USER", user, num_users_so_far + 1)
        # Set up a reverse index so we can go from user -> position (above)
        # and position -> user (below)
        self.redis_conn.hset("QUEUE", f"pos-{num_users_so_far}", user)

    def _get_curr_index_in_queue(self) -> int:
        return int(self.redis_conn.hget("QUEUE", "pos"))

    def _set_queue_index(self, val: int):
        self.redis_conn.hset("QUEUE", "pos", val)

    def _wrap_queue_index(self):
        curr_loc: int = self._get_curr_index_in_queue()
        if curr_loc >= self.get_num_users_in_queue():
            self._set_queue_index(0)

    def get_curr_location_in_queue(self) -> int:
        """Get the current index of the queue.

        Returns:
            int: _description_
        """
        self._wrap_queue_index()
        return self._get_curr_index_in_queue()

    def next(self):
        """Advances queue index by 1."""
        self.redis_conn.hincrby("QUEUE", "pos", 1)
        self._wrap_queue_index()

    def get_curr_user(self) -> str | None:
        """Get the user located at the current queue index.

        Returns:
            str: The ID of the current user in the queue.
        """
        self._wrap_queue_index()
        q_idx: int = self.get_curr_location_in_queue()
        return self.redis_conn.hget("QUEUE", f"pos-{q_idx}")

    def get_next_user(self) -> str | None:
        self._wrap_queue_index()
        q_idx: int = self.get_curr_location_in_queue()
        return self.redis_conn.hget("QUEUE", f"pos-{q_idx + 1}")

    def get_all_users(self) -> dict[str, int]:
        return {
            user_id: int(idx)
            for user_id, idx in self.redis_conn.hgetall("USER").items()
        }
    
    def set_watch2gether_stream_key(self, stream_key: str):
        self.redis_conn.hset('W2G', key='streamkey', value=stream_key)

    def get_watch2gether_stream_key(self) -> str | None:
        return self.redis_conn.hget('W2G', 'streamkey')
