from fastapi import APIRouter, HTTPException
from app.core.database import ALERTS
from pydantic import BaseModel
import uuid

router = APIRouter()


class AlertIn(BaseModel):
    symbol: str
    price: float
    direction: str


@router.get("/alerts")
def list_alerts():
    return ALERTS


@router.post("/alerts")
def create_alert(payload: AlertIn):
    item = payload.dict()
    item["id"] = str(uuid.uuid4())
    ALERTS.append(item)
    return item


@router.delete("/alerts/{id}")
def delete_alert(id: str):
    for i, a in enumerate(ALERTS):
        if a.get("id") == id:
            ALERTS.pop(i)
            return {"deleted": id}
    raise HTTPException(status_code=404, detail="Not found")
