import uuid

from fastapi import APIRouter

from app import database
from app.messaging import kafka_producer, rabbitmq
from app.models import OrderCreate, OrderResponse

router = APIRouter(prefix="/api/v1", tags=["orders"])


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(payload: OrderCreate):
    db = await database.get_database()
    order_id = str(uuid.uuid4())
    doc = {
        "_id": order_id,
        "nome_cliente": payload.nome_cliente,
        "nome_produto": payload.nome_produto,
        "quantidade": payload.quantidade,
        "status": "PENDENTE",
    }
    await db.orders.insert_one(doc)

    msg = {
        "nome_cliente": doc["nome_cliente"],
        "nome_produto": doc["nome_produto"],
        "quantidade": doc["quantidade"],
        "status": doc["status"],
    }
    await rabbitmq.publish_order_created(order_id, msg)
    await kafka_producer.publish_order_event(order_id, msg)

    return OrderResponse(id=order_id, **msg)


@router.get("/orders", response_model=list[OrderResponse])
async def list_orders():
    db = await database.get_database()
    orders = []
    async for doc in db.orders.find():
        orders.append(
            OrderResponse(
                id=doc["_id"],
                nome_cliente=doc["nome_cliente"],
                nome_produto=doc["nome_produto"],
                quantidade=doc["quantidade"],
                status=doc["status"],
            )
        )
    return orders
