import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()

dev = []

class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool

@app.get("/devices")
def get_devices():
    return(list(devices.find({}, {"_id": 0})))

@app.get("/devices/{name}")
def get_devices(name:str):
    dev = devices.find_one({"name":name}, {"_id": 0})
    if dev is None:
        raise HTTPException(status_code=404, detail="No device named " + name + " was found")
    return(dev)

@app.post("/devices", status_code = 201)
def add_device(device: Device):
    new_device = device.model_dump()
    if devices.find_one({"name": new_device["name"]}) is not None:
        raise HTTPException(status_code=409, detail="Device called " + new_device["name"] + " already exists")
    else:
        devices.insert_one(new_device)
        new_device.pop("_id")
    return new_device

@app.put("/devices/{name}")
def device_update(name:str, update_device: Device):
    dev_update = update_device.model_dump()
    if (devices.find_one({"name":name}, {"_id": 0})) is not None:
       devices.update_one(({"name":name}),{"$set": dev_update})
    else:
        devices.insert_one(dev_update)
        raise HTTPException(status_code=201, detail="Device named " + name + " created")
    return(dev_update) 
