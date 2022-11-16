import secrets

from fastapi import Depends, FastAPI, HTTPException, status, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, ValidationError, validator
from typing import Union
import json
from api_anonymizer import RequestWithRashedResponse
import os
from typing import List, Union
import re

app = FastAPI()

security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = os.environ.get("USERNAME", "").encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = os.environ.get('PASSWORD', "").encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed authentication!",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username




class ApiCall(BaseModel):
    method: str
    url: str
    headers: dict =None
    payload: Union[str, None] = None
    hashed_filds: list

    @validator('method')
    def method_must_be_valid(cls, v):
        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "COPY", "HEAD", "OPTIONS", "LINK", "UNLINK", "PURGE", "LOCK", "UNLOCK", "PROPFID", "VIEW"]
        if v not in valid_methods:
            raise ValueError('must be one of the valid methods: ' + str(valid_methods))
        return v.title()

class ApiAuth(BaseModel):
    method: str
    url: str
    headers: dict =None
    payload: Union[str, None] = None

    @validator('method')
    def method_must_be_valid(cls, v):
        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "COPY", "HEAD", "OPTIONS", "LINK", "UNLINK", "PURGE", "LOCK", "UNLOCK", "PROPFID", "VIEW"]
        if v not in valid_methods:
            raise ValueError('must be one of the valid methods: ' + str(valid_methods))
        return v.title()


@app.post("/set_foreign_auth_header/")
async def set_foreign_auth(api: ApiAuth, username: str = Depends(get_current_username)):


    url = api.url
    if api.payload:
        payload=api.payload
    else:
        payload={}
    
    headers = api.headers

    response = RequestWithRashedResponse.request(api.method, url, headers=headers, data=payload)


    if response.status_code==200:
        auth_header = response.request.headers["Authorization"]
        os.environ["FOREIGN_AUTH_HEADER"] = auth_header
        return "AUTHORIZATION VALIDATED!, Now set to: 'Authorization': '" + auth_header + "'"
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="ERROR AUTHORIZATION NOT SET! Foreign api message: " + response.text,
            headers={"WWW-Authenticate": "Basic"},
        )


@app.post("/api/")
async def forward_api(api: ApiCall, username: str = Depends(get_current_username)):

    hashed_filds=api.hashed_filds

    url = api.url
    if api.payload:
        payload=api.payload
    else:
        payload={}
    
    headers = api.headers


    foreign_auth_header = os.environ["FOREIGN_AUTH_HEADER"]
    if headers!=None:
        if "Authorization" in headers:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Authentication of the foreign api must be set by the endpoint /set_foreign_auth_header. Remove the Authorization key from headers",
                headers={"WWW-Authenticate": "Basic"},
            )
    else:
        headers={}

    headers["Authorization"]=foreign_auth_header


    response = RequestWithRashedResponse.request(api.method, url, headers=headers, data=payload, hashed_filds=hashed_filds)

    if response.status_code==200:
        return json.loads(response.text)
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="Foreign api message: " + response.text,
            headers={"WWW-Authenticate": "Basic"},
        )


@app.get("/api/")
async def forward_api(
    x_method: str = Header(),
    x_url: str = Header(),
    x_headers: str = Header(default=None),
    x_hashed_filds: str = Header(default=None),
    x_payload: str = Header(default=None)
    ):



    hashed_filds=json.loads(x_hashed_filds)

    url = x_url
    if x_payload:
        payload=json.loads(x_payload)
    else:
        payload={}

    
    
    foreign_auth_header = os.environ["FOREIGN_AUTH_HEADER"]
    regex = re.compile("\"Authorization\":.*\"(?P<value>.*?)\"", re.IGNORECASE)
    if len(regex.findall(x_headers))>0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Authentication of the foreign api must be set by the endpoint /set_foreign_auth_header. Remove the Authorization key from x-headers",
            headers={"WWW-Authenticate": "Basic"},
        )

    headers = json.loads(x_headers)
    headers["Authorization"]=foreign_auth_header
    response = RequestWithRashedResponse.request(x_method, url, headers=headers, data=payload, hashed_filds=hashed_filds)

    if response.status_code==200:
        return json.loads(response.text)
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="Foreign api message: " + response.text,
            headers={"WWW-Authenticate": "Basic"},
        )