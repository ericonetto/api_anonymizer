"""MIT Licence

Copyright © 11 December 2022, Erico NETTO
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the “Software”), to deal in the Software without restriction, including without 
limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
the Software, and to permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
 of the Software.

The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited
 to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event 
 shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an 
 action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or
  other dealings in the Software.

Except as contained in this notice, the name of the Erico NETTO shall not be used in advertising or otherwise
 to promote the sale, use or other dealings in this Software without prior written authorization from the 
 Erico NETTO."""


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


class ApiCallAuth(BaseModel):
    method: str
    url: str
    headers: dict ={"Authorization":"Basic "}
    payload: Union[str, None] = None
    hashed_fields: list

    @validator('method')
    def method_must_be_valid(cls, v):
        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "COPY", "HEAD", "OPTIONS", "LINK", "UNLINK", "PURGE", "LOCK", "UNLOCK", "PROPFID", "VIEW"]
        if v not in valid_methods:
            raise ValueError('must be one of the valid methods: ' + str(valid_methods))
        return v.title()


class ApiCall(BaseModel):
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



@app.post("/config_foreign_api/")
async def set_foreign_api_authentication_and_hashed_fields(api: ApiCallAuth, username: str = Depends(get_current_username)):
    hashed_fields=api.hashed_fields

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
        os.environ["HASHED_FIELDS"] = str(hashed_fields)
        return "AUTHORIZATION VALIDATED!, Now set to: 'Authorization': '" + auth_header + "'"
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="ERROR AUTHORIZATION NOT SET! Foreign api message: " + response.text,
            headers={"WWW-Authenticate": "Basic"},
        )


@app.post("/api/")
async def foreign_api(api: ApiCall, username: str = Depends(get_current_username)):

    url = api.url
    if api.payload:
        payload=api.payload
    else:
        payload={}
    
    headers = api.headers

    if headers!=None:
        if "Authorization" in headers:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Authentication of the foreign api must be set by the endpoint /config_foreign_api. Remove the Authorization key from headers",
                headers={"WWW-Authenticate": "Basic"},
            )
    else:
        headers={}

    if not "FOREIGN_AUTH_HEADER"  in os.environ:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Authentication of the foreign api must be set by the endpoint /config_foreign_api",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not "HASHED_FIELDS" in os.environ:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="hashed_fields of the foreign api must be set by the endpoint /config_foreign_api",
            headers={"WWW-Authenticate": "Basic"},
        )


    foreign_auth_header = os.environ["FOREIGN_AUTH_HEADER"]
    hashed_fields=json.loads(os.environ["HASHED_FIELDS"].replace("'","\""))
    headers["Authorization"]=foreign_auth_header


    response = RequestWithRashedResponse.request(api.method, url, headers=headers, data=payload, hashed_fields=hashed_fields)

    if response.status_code==200:
        return json.loads(response.text)
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="Foreign api message: " + response.text,
            headers={"WWW-Authenticate": "Basic"},
        )


@app.get("/api/")
async def foreign_api(
    x_method: str = Header(),
    x_url: str = Header(),
    x_headers: str = Header(default=None),
    x_payload: str = Header(default=None)
    ):


    url = x_url
    if x_payload:
        payload=json.loads(x_payload)
    else:
        payload={}

    
    regex = re.compile("\"Authorization\":.*\"(?P<value>.*?)\"", re.IGNORECASE)
    if len(regex.findall(x_headers))>0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Authentication of the foreign api must be set by the endpoint /config_foreign_api. Remove the Authorization key from x-headers",
            headers={"WWW-Authenticate": "Basic"},
        )

    headers = json.loads(x_headers)

    if not "FOREIGN_AUTH_HEADER" in os.environ:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Authentication of the foreign api must be set by the endpoint /config_foreign_api",
            headers={"WWW-Authenticate": "Basic"},
        )


    if not "HASHED_FIELDS" in os.environ:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="hashed_fields of the foreign api must be set by the endpoint /config_foreign_api",
            headers={"WWW-Authenticate": "Basic"},
        )


    foreign_auth_header = os.environ["FOREIGN_AUTH_HEADER"]
    headers["Authorization"]=foreign_auth_header
    hashed_fields=jjson.loads(os.environ["HASHED_FIELDS"].replace("'","\""))
    response = RequestWithRashedResponse.request(x_method, url, headers=headers, data=payload, hashed_fields=hashed_fields)

    if response.status_code==200:
        return json.loads(response.text)
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="Foreign api message: " + response.text,
            headers={"WWW-Authenticate": "Basic"},
        )