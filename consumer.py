import json
from fastapi import HTTPException

def create_delivery(state, event):
    data = json.loads(event.data)
    return {
        "id": event.delivery_id,
        "budget": int(data["budget"]),
        "notes": data["notes"],
        "status": "ready"
    }

def start_delivery(state, event):
    if state['status'] != 'ready':
        raise HTTPException(status_code=400, detail='Delivery has started!')
    state["status"] = "active"
    return state

def pickup_products(state, event):
    if state['status'] != 'active':
        raise HTTPException(status_code=400, detail='Product has been picked!')
    data = json.loads(event.data)
    new_budget = state["budget"] - int(data["purchase_price"]) * data["quantity"]
    if new_budget < 0:
        raise HTTPException(status_code=400, detail='Budget not enough!')
    return state | {
        "budget": new_budget,
        "sell_price": int(data["purchase_price"]),
        "quantity": data["quantity"],
        "status": "collected"
    }

def deliver_products(state, event):
    if state['status'] != 'collected':
        raise HTTPException(status_code=400, detail='Transaction is completed!')
    data = json.loads(event.data)
    new_budget = state["budget"] + int(data["sell_price"]) * data["quantity"]
    new_quantity = state["quantity"] - data["quantity"]
    return state | {
        "budget": new_budget,
        "sell_price": int(data["sell_price"]),
        "quantity": new_quantity,
        "status": "completed"
    }


CUSUMER = {
    "CREATE_DELIVERY": create_delivery,
    "START_DELIVERY": start_delivery,
    "PICKUP_PRODUCTS": pickup_products,
    "DELIVER_PRODUCTS": deliver_products
}