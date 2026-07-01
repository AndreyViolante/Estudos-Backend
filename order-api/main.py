import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI

from app import database
from app.messaging import kafka_producer, rabbitmq
from app.routes.orders import router

logger = logging.getLogger(__name__)


async def _retry(fn: Callable, retries: int = 15, delay: float = 3.0) -> None:
    for attempt in range(retries):
        try:
            await fn()
            return
        except Exception as exc:
            if attempt == retries - 1:
                raise
            logger.warning(
                "Attempt %d/%d failed (%s). Retrying in %.0fs…",
                attempt + 1,
                retries,
                exc,
                delay,
            )
            await asyncio.sleep(delay)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _retry(database.connect)
    await _retry(rabbitmq.connect)
    await _retry(kafka_producer.start)

    yield

    await database.close()
    await rabbitmq.close()
    await kafka_producer.stop()


app = FastAPI(title="Order Management API", version="1.0.0", lifespan=lifespan)
app.include_router(router)
