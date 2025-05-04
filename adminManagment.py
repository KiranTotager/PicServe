import datetime
from datetime import timedelta
from email.policy import default
from SecurityConfiguration import get_current_user
from fastapi import Depends,HTTPException,status
from fastapi import APIRouter,UploadFile,File,HTTPException,status
from fastapi.openapi.models import OAuth2
from fastapi.params import Depends
from aiomysql import Cursor
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, field_validator, EmailStr
import re
from jose import jwt,JWTError
# from starlette.responses import JSONResponse
from fastapi.responses import JSONResponse
from dbconfig import get_db_conn
from typing import Optional, Literal, Any, Self
import bcrypt
from mailHandling import send_reset_email

router=APIRouter()

class AdminRegistration(BaseModel):
    name:str
    role:Literal["admin","guest"]
    bio:Optional[str]="-"
    contact:str
    email:EmailStr
    password:str

    @field_validator("contact")
    def validate_contact(cls,value):
        if not re.fullmatch(r'\d{10}',value):
            raise ValueError("contact must should contain only 10 digits")
        else:
            return value

    @field_validator("password")
    def validate_password(cls,value):
        # return value
        if value is None or len(value)<8 or  not re.search(r'[A-za-z]',value) or not re.search(r'\d',value) or not re.search(r'[_@]',value):
            raise ValueError("password must contain at least 8 characters,at least one letter,at least one digit and atleast one special character")
        else:
            return value


class password_update(BaseModel):
    name:str
    new_password: str


class profileUpdate(BaseModel):
    name: str
    bio: Optional[str]="-"
    contact: str


class login(BaseModel):
    name:str
    password:str

class forgotPasswords(BaseModel):
    email:str



secretKey="SECRET_KEY"
algorithm="HS256"


secure_router=APIRouter(
    prefix="/api",
    dependencies=[Depends(get_current_user)]
)

@router.post("/createUser")
async def createAdmin(admin:AdminRegistration):
    # return "hitting"
    hashedPassword=bcrypt.hashpw(admin.password.encode("utf-8"),bcrypt.gensalt())
    queryParams=[]
    checkUserQuery="select * from photographers where name=%s"
    query=f"insert into photographers(name,bio,contact_info,email,password,role) values(%s,%s,%s,%s,%s,%s)"
    queryParams=[admin.name,admin.bio,admin.contact,admin.email,hashedPassword,admin.role]

    try:
        async with get_db_conn() as cursor:
            await cursor.execute(checkUserQuery,(admin.name,))
            user=await cursor.fetchone()
            if(user is not None):
                return HTTPException(detail=f"user {admin.name} already exist",status_code=400)
            await cursor.execute(query,tuple(queryParams))

        return JSONResponse(content=f"{admin.name} registered successfully")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"internal server error can you please try after some time {e}")

@secure_router.put("/update/user/{id}")
async def updateUser(payload:profileUpdate,id:int):
    checkUserQuery = "select * from photographers where id=%s"
    try:
        async with get_db_conn() as cursor:
            await cursor.execute(checkUserQuery,(id,))
            user = await cursor.fetchone()
            if (user is None):
                return HTTPException(detail=f"user with id {id} not exist", status_code=400)
            query="update photographers set name=%s,bio=%s,contact_info=%s where id=%s"
            query_params=(payload.name,payload.bio,payload.contact,id)
            await cursor.execute(query,query_params)
        return JSONResponse(status_code=200,content="user details updated successfully")
    except Exception as e:
        return HTTPException(detail=e,status_code=500)





#to update the user password

@secure_router.put("/update/user")
async def updatePassword(requestData:password_update,currentUser:dict=Depends(get_current_user)):
    try:
       # payload=jwt.decode(requestData.token,secretKey,algorithm)
       userId=currentUser["id"]

       if userId is None :
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalide token")

       async with get_db_conn() as cursor:

           hashedPassword=bcrypt.hashpw(requestData.new_password.encode("utf-8"),bcrypt.gensalt())
           await cursor.execute("UPDATE photographers set password=%s ,name=%s where id=%s",(hashedPassword,requestData.name,userId))
           return JSONResponse(content={"message":"password updated successfully"},status_code=status.HTTP_201_CREATED)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT,detail={"error":e})





@secure_router.delete("/deleteuser")
async def deletUser(currentUser:dict=Depends(get_current_user)):
    id = currentUser["id"]
    query="delete from photographers where id=%s"
    try:
        async with get_db_conn() as cursor:
            await cursor.execute(query, (id))
        return JSONResponse(content="user deleted successfully",status_code=200)
    except Exception as e:
        return HTTPException(status_code=500,detail=f"internal server error please try again after some time or contact devloper {e}")


@secure_router.post("/upload/profilepic")
async def uploadProfilePic(profilePic:UploadFile=File(...)):
    if profilePic is None:
        raise HTTPException(status_code=400,detail="profile pic is required")

@secure_router.get("/getusers")
async def getUsers():
    try:
        async  with get_db_conn() as cursor:
            await cursor.execute("select id,name,contact_info,role,bio from photographers")
            users = await cursor.fetchall()

        return JSONResponse(status_code=200,content=users)
    except Exception as e:
        return HTTPException(status_code=500,detail=e)

@secure_router.get("/getuser/{id}")
async def getUser(id:int):
    try:

        async with get_db_conn() as cursor:
            query="select id,name,contact_info,role,bio from photographers where id=%s"
            await cursor.execute(query,(id,))
            user=await cursor.fetchone()
            if(user is not None):
                return JSONResponse(content=user,status_code=200)
            else:
                return JSONResponse(content="user not found",status_code=404)
    except Exception as e:
        return JSONResponse(content=e,status_code=500)


@router.post("/login")
async def userLogin(payload:login):
    #admin login functionality
    async with get_db_conn() as cursor:
        await cursor.execute("select * from photographers where name=%s",(payload.name,))
        user=await cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not exist")
        if not bcrypt.checkpw(payload.password.encode("utf-8"),user["password"].encode("utf-8")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="wrong password")
        expires=int((datetime.datetime.utcnow()+timedelta(hours=24)).timestamp())
        responsePayload={
            "id":user["id"],
            "name":user["name"],
            "expires":expires
        }
        token=jwt.encode(responsePayload,key=secretKey,algorithm=algorithm)
        return JSONResponse(
            status_code=200,
            content={
                "access_token":token,
                "token_type":"bearer",
                "user":{
                    "id":user["id"],
                    "name":user["name"],
                    "email":user["email"]
                }
            }
        )


@router.post("/api/forgot-password")
async def forgot_password(forgotPassword:forgotPasswords):
    async with get_db_conn() as cursor:
        await cursor.execute("select * from photographers where email=%s",(forgotPassword.email,))
        user=await cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")

        payload={
            "user_id":user["id"],
            "exp":int((datetime.datetime.utcnow()+timedelta(minutes=30)).timestamp())
        }

        resettoken=jwt.encode(payload,secretKey,algorithm)
        resetlink=f"https://demo.com/reset-password?token={resettoken}"
        try:
            res=await send_reset_email(forgotPassword.email, resetlink)

            if res:
               return JSONResponse(content={"message": "reset message has been sent to your email,please check it...!"},
                                   status_code=status.HTTP_201_CREATED)
        except Exception as e:
           raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="internval server error")
