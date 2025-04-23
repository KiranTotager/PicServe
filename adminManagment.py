from email.policy import default

from fastapi import APIRouter,UploadFile,File,HTTPException
from fastapi.params import Depends
from aiomysql import Cursor
from pydantic import BaseModel,field_validator
import re

from starlette.responses import JSONResponse

from dbconfig import get_db_conn
from typing import Optional,Literal
import bcrypt

router=APIRouter()

class AdminRegistration(BaseModel):
    name:str
    role:Literal["admin","guest"]
    bio:Optional[str]
    contact:str
    password:str

    @field_validator("contact")
    def validate_contact(self,value):
        if not re.fullmatch(r'\d{10}',value):
            return ValueError("contact must should contain only 10 digits")
        return value


    @field_validator("password")
    def validate_passoword(self,value):
        if len(value)<8 or  not re.search(r'[A-za-z]',value) or not re.search(r'\d',value) or re.search(r'[_@]',value):
            return ValueError("password must contain at least 8 characters,at least one letter,at least one digit and atleast one special character")
        return value



@router.post("api/create")
async def createAdmin(admin:AdminRegistration,cursor:Cursor=Depends(get_db_conn)):
    # this block is contain the logic for the creation of the admins
    # test="test"
    hashedPassword=bcrypt.hashpw(admin.password.encode("utf-8"),bcrypt.gensalt())
    if admin.bio is not None:
        query=f"insert into photographers(name,bio,contact_info,password,role) values('{admin.name}','{admin.bio}','{admin.contact}','{hashedPassword}','{admin.role}')"
    else:
        query=f"insert into photographers(name,contact_info,password,role) values('{admin.name}','{admin.contact}','{hashedPassword}','{admin.role}')"
    try:
        await cursor.execute(query)
        return JSONResponse(content=f"{admin.name} registered successfully")
    except Exception as e:
        raise HTTPException(status_code=500,detail="internal server error can you please try after some time")

@router.post("api/update/user")
async def updateUser():
    return "update user"

@router.delete("api/deleteuser")
async def deletUser():
    return "delete user"


@router.post("api/upload/profilepic")
async def uploadProfilePic(profilePic:UploadFile=File(...)):
    if profilePic is None:
        raise HTTPException(status_code=400,detail="profile pic is required")