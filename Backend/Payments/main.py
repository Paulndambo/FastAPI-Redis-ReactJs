from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests, time


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = get_redis_connection(
    #host="redis-10463.c8.us-east-1-4.ec2.cloud.redislabs.com",
    host="127.0.0.1",
    port=6379,
    #port=10463,
    #password="TCiWVqwRy1Vnq0AQ0Buh5nZqtUPNZqGC",
    decode_responses=True
)
app = FastAPI()

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int 
    status: str #pending, completed, refunded

    class Meta:
        database = redis


@app.get("/orders")
def orders():
    return [format(pk) for pk in Order.all_pks()]

@app.get("/orders/{pk}")
def get_order(pk: str):
    return Order.get(pk)



@app.post("/orders")
async def create_order(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()

    req = requests.get("http://localhost:8000/products/%s" % body['product_id'] )
    product = req.json()

    order = Order(
        product_id=body['product_id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total= 1.2 * product['price'],
        quantity=body['quantity'],
        status="pending"
        )
    order.save()

    background_tasks.add_task(
        order_completed, order
    )

    #order_completed(order)

    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = "completed"
    order.save()
    redis.xadd('order_completed', order.dict(), '*')


def format(pk: str):
    order = Order.get(pk)
    return {
        "id": order.pk,
        "product_id": order.product_id,
        "price": order.price,
        "quantity": order.quantity,
        "status": order.status,
    }
