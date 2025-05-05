
from fastapi import APIRouter,UploadFile,File,HTTPException,status

from fastapi.params import Depends

from fastapi.security import OAuth2PasswordBearer

from jose import jwt,JWTError




secretKey="SECRET_KEY"
algorithm="HS256"

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_current_user(token:str=Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(token,secretKey,algorithms=algorithm)
        username=payload.get("name")
        # id=payload.get("id")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid or expired token")
