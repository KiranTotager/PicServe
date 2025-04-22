from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
from dbconfig import get_db_conn

router=APIRouter()

class AdminRegistration(BaseModel):
    name:str
    bio:str
    contact:str
    profilePic:str
    password:str


@router.post("api/create")
async def createAdmin(admin:AdminRegistration,conn=Depends(get_db_conn)):
    # this block is contain the logic for the creation of the admins
    test="test"