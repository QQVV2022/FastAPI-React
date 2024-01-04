from fastapi import FastAPI, Request
from  redis_om import get_redis_connection, HashModel
import redis
import json


app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['*'],
#     allow_methods=['*'],
#     allow_headers=['*']
# )

rd = redis.Redis(host='localhost', port=6379, db=5)

class Delivery(HashModel):
    budget: int = 0
    notes: str = ''

    class Meta:
        database = rd

class Event(HashModel):
    delivery_id: str = None
    type: str
    data: str

    class Meta:
        database = rd


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/deliveries/create")
async def create(request: Request):
    body = await request.json()
    delivery = Delivery(budget=body['data']['budget'], notes=body['data']['notes']).save()
    event = Event(delivery_id=delivery.pk, type=body['type'], data=json.dumps(body['data'])).save()
    return event
