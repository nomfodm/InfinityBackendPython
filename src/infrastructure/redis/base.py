from redis.asyncio import Redis


class RedisManager:
    def __init__(self, host: str, port: int, db: int):
        self.client = Redis(host=host, port=port, db=db, decode_responses=True)
