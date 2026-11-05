# server.py - QUADE & SONS Backend - Ireen's Girly Corner
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time, json, os

app = FastAPI(title="Ireen's Girly Corner API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_FILE = "db.json"
def load_db():
    if os.path.exists(DB_FILE):
        return json.load(open(DB_FILE))
    return {
        "products": [
            {"id":1,"name":"Pink Satin Slip Dress","price":350,"cat":"Dresses","tag":"NEW","color":"pink","img":"https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600","desc":"Silky, classy"},
            {"id":2,"name":"White Crop + Skirt Set","price":280,"cat":"Sets","tag":"HOT","color":"blue","img":"https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600","desc":"2-piece set"},
        ],
        "users": [{"name":"Ireen Admin","phone":"0977000000","password":"1234","role":"admin"}],
        "orders": []
    }
def save_db(db): json.dump(db, open(DB_FILE,"w"), indent=2)

class UserIn(BaseModel):
    name: Optional[str] = ""
    phone: str
    password: str
    address: Optional[str] = ""

class ProductIn(BaseModel):
    name: str; price: int; cat: str = "Dresses"; tag: str = "NEW"; color: str = "pink"; img: str = ""; desc: str = ""

class OrderIn(BaseModel):
    phone: str; items: List[dict]; total: int; addr: str; pay: str = "MoMo"

@app.get("/")
def root(): return {"status":"Quade & Sons API Live","app":"Ireen's Girly Corner"}

@app.post("/auth/signup")
def signup(u: UserIn):
    db=load_db()
    if any(x["phone"]==u.phone for x in db["users"]): raise HTTPException(400,"Phone exists")
    db["users"].append({"name":u.name,"phone":u.phone,"password":u.password,"address":u.address,"role":"user"})
    save_db(db); return {"ok":True,"name":u.name,"phone":u.phone}

@app.post("/auth/login")
def login(u: UserIn):
    db=load_db()
    user=next((x for x in db["users"] if x["phone"]==u.phone and x["password"]==u.password),None)
    if not user: raise HTTPException(401,"Wrong phone or password")
    return {"ok":True,"name":user["name"],"phone":user["phone"],"role":user.get("role","user")}

@app.get("/products")
def get_products(): return load_db()["products"]

@app.post("/products")
def add_product(p: ProductIn):
    db=load_db(); d=p.dict(); d["id"]=int(time.time()*1000); db["products"].insert(0,d); save_db(db); return d

@app.put("/products/{pid}")
def edit_product(pid:int,p: ProductIn):
    db=load_db()
    for x in db["products"]:
        if x["id"]==pid: x.update(p.dict()); save_db(db); return x
    raise HTTPException(404,"Not found")

@app.delete("/products/{pid}")
def del_product(pid:int):
    db=load_db(); db["products"]=[x for x in db["products"] if x["id"]!=pid]; save_db(db); return {"ok":True}

@app.get("/orders")
def get_orders(): return load_db()["orders"]

@app.post("/orders")
def create_order(o: OrderIn):
    db=load_db(); order={"id":int(time.time()*1000),**o.dict(),"status":"Packing","date":time.strftime("%Y-%m-%d %H:%M")}; db["orders"].insert(0,order); save_db(db); return order

@app.get("/stats")
def stats():
    db=load_db(); return {"products":len(db["products"]),"orders":len(db["orders"]),"sales":sum(x["total"] for x in db["orders"]),"users":len(db["users"])}
