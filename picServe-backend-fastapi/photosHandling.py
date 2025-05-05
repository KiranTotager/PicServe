import datetime
import os

import aiofiles
from fastapi import APIRouter,Depends,UploadFile,File,status,HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request

from SecurityConfiguration import get_current_user
from typing import List
from dbconfig import get_db_conn

photo_Secure_router=APIRouter(
    prefix="/api",
    dependencies=[Depends(get_current_user)]
)

get_photos_router=APIRouter()
UPLOAD_FOLDER="uploadedPhotos"
os.makedirs(UPLOAD_FOLDER,exist_ok=True)


@photo_Secure_router.post("/hitphotos")
async def photosHealthCheck():
    return "hello ,photos section is up"


@photo_Secure_router.post("/upload/photo")
async def uploadPhotos(files:List[UploadFile]=File(...),currentUser:dict=Depends(get_current_user)):
    userName=currentUser["name"]
    photographerId=currentUser.get("id")
    folder_path=os.path.join(UPLOAD_FOLDER,userName)
    os.makedirs(folder_path,exist_ok=True)
    uploaded_files=[]
    try:

        async with get_db_conn() as (cursor,conn):
            for file in files:
                timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                filename = f"{timestamp}_{file.filename}"
                file_path = os.path.join(folder_path, filename)

                async with aiofiles.open(file_path, 'wb') as out_file:
                    content = await file.read()
                    await out_file.write(content)
                    expires_at=datetime.datetime.utcnow()+datetime.timedelta(hours=24)
                    relativeUrl=f"{userName}/{filename}"
                    insert_query="INSERT INTO photos (photographer_id,url,uploaded_at,expires_at,likes_count) VALUES(%s,%s,%s,%s,%s)"
                    await cursor.execute(insert_query,(photographerId,relativeUrl,datetime.datetime.now(),expires_at,0))
                    await conn.commit()
                    uploaded_files.append(filename)

        return JSONResponse(content={
            "message":"file uploaded successfully",
            "files":relativeUrl
        }, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(detail=f"error while uploading the file {e}",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)




async def delete_expired_photos():
    print("deleting the expired photos")
    async with get_db_conn() as (cursor,conn):
        await cursor.execute("SELECT pf.id,pf.url,ph.name FROM photos pf INNER JOIN photographers ph ON ph.id=pf.photographer_id WHERE expires_at <=NOW()")
        expired_photos=await cursor.fetchall()
        print("entering the first await block")

        for photo in expired_photos:
            print("entering the for loop")
            print(photo)
            file_path=os.path.join(UPLOAD_FOLDER,photo.get("url"))
            print(file_path)
            try:
                if os.path.exists(file_path):
                    print(f"deleting the {file_path}")
                    os.remove(file_path)
            except Exception as e:
                raise HTTPException(detail=f"while deleting the expired photos {e}",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


            await cursor.execute("DELETE FROM photos WHERE id=%s",(photo.get("id")))
            await  conn.commit()

@get_photos_router.get("/get/photos")
async def get_all_photos(request:Request):
    try:
        async with get_db_conn() as (cursor,conn):
            await cursor.execute("SELECT pf.id,pf.url,ph.name FROM photos pf INNER JOIN photographers ph ON ph.id=pf.photographer_id WHERE expires_at > NOW() ORDER BY uploaded_at DESC")
            rows=await cursor.fetchall()

            base_url=request.base_url._url.rstrip("/")
            for row in rows:
                row["url"]=f"{base_url}/photos/{row["url"]}"
            return JSONResponse(content=rows,status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(detail=f"error while fetching the photos metadata {e}",
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


