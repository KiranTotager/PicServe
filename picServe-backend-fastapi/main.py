from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from dbconfig import init_db_pool,close_db_pool
from contextlib import asynccontextmanager
from adminManagment import router, secure_router
from photosHandling import delete_expired_photos

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler=AsyncIOScheduler()


from photosHandling import photo_Secure_router,get_photos_router
# app=FastAPI()

async def run_async_job():
    # loop=asyncio.get_event_loop()
    # asyncio.create_task(delete_expired_photos())
    await delete_expired_photos()

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("application is sarted")
    await init_db_pool()
    print("🚀 Lifespan started")
    scheduler.add_job(
        run_async_job,IntervalTrigger(seconds=15),
        id="delete_expired",
        replace_existing=True
    )
    if not scheduler.running:
        scheduler.start()
    yield
    await close_db_pool()
    # print("application closed")
app=FastAPI(lifespan=lifespan)
app.include_router(router)
app.include_router(secure_router)
app.include_router(photo_Secure_router)
app.include_router(get_photos_router)

app.mount("/photos",StaticFiles(directory="uploadedPhotos"),name="photos")
@app.get("/api/healthCheck")
async def healthCheck():
    return("yes i am up")