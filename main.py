from fastapi import FastAPI, Request
from  redis_om import get_redis_connection, HashModel
import redis
import json
import consumer

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

@app.get('/deliveries/{pk}/status')
async def get_state(pk: str):
    state = rd.get(f'delivery:{pk}')
    print("AA",state)
    if state is not None:
        return json.loads(state)
    else:
        state = build_state(pk)
        rd.set(f'delivery:{pk}', json.dumps(state))
        return state

def build_state(pk: str):
    pks = Event.all_pks()
    all_events = [Event.get(pk) for pk in pks]
    events = [event for event in all_events if event.delivery_id == pk]

    state = {}
    for event in events:
        state = consumer.CUSUMER[event.type](state, event)

    return state

@app.post("/deliveries/create")
async def create(request: Request):
    body = await request.json()
    delivery = Delivery(budget=body['data']['budget'], notes=body['data']['notes']).save()
    event = Event(delivery_id=delivery.pk, type=body['type'], data=json.dumps(body['data'])).save()
    state = consumer.CUSUMER[body['type']]({},event)
    rd.set(f'delivery:{delivery.pk}', json.dumps(state))
    return state

@app.post("/event")
async def dispatch(request: Request):
    body = await request.json()
    delivery_id = body['delivery_id']
    event = Event(delivery_id=delivery_id, type=body['type'], data=json.dumps(body['data'])).save()
    state = await get_state(delivery_id)
    new_state = consumer.CUSUMER[body['type']](state, event)
    rd.set(f'delivery:{delivery_id}', json.dumps(new_state))
    return new_state