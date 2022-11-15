import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, ValidationError, validator
from fastapi.security import APIKeyQuery
from typing import Union
import json
from api_anonymizer import RequestWithRashedResponse


app = FastAPI()

security = HTTPBasic()


def authenticate(credentials: APIKeyQuery = Depends(security)):
    current_username_bytes = credentials..username.encode("utf8")
    correct_username_bytes = b"stanleyjobson"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"swordfish"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username




class ApiCall(BaseModel):
    method: str
    url: str
    headers: dict
    payload: Union[str, None] = None
    hashed_filds: list

    @validator('method')
    def method_must_be_valid(cls, v):
        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "COPY", "HEAD", "OPTIONS", "LINK", "UNLINK", "PURGE", "LOCK", "UNLOCK", "PROPFID", "VIEW"]
        if v not in valid_methods:
            raise ValueError('must be one of the valid methods: ' + str(valid_methods))
        return v.title()


@app.post("/api/")
async def forward_api(api: ApiCall, authenticated: bool = Depends(authenticate)):



    hashed_filds=api.hashed_filds

    url = api.url
    if api.payload:
        payload=api.payload
    else:
        payload={}
    
    headers = api.headers

    response = RequestWithRashedResponse.request(api.method, url, headers=headers, data=payload, hashed_filds=hashed_filds)


    return json.loads(response.text)

