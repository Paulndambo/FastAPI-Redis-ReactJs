from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel

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

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get("/products")
def products():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
    }


@app.post("/products")
def create_product(product: Product):
    return product.save()


@app.get("/products/{pk}")
def get_product(pk: str):
    product = Product.get(pk)
    return product


@app.delete("/products/{pk}")
def delete_product(pk: str):
    return Product.delete(pk)
