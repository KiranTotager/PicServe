from fastapi import FastAPI
from dbconfig import init_db_pool,close_db_pool
from contextlib import asynccontextmanager
from adminManagment import router

# app=FastAPI()

@asynccontextmanager
async def lifespan(app:FastAPI):
    # print("application is sarted")
    await init_db_pool()
    yield
    await close_db_pool()
    # print("application closed")
app=FastAPI(lifespan=lifespan)
app.include_router(router)
@app.get("/api/healthCheck")
async def healthCheck():
    return("yes i am up")