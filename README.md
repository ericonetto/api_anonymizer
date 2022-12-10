# API Anonymizer

## A simple middleware API that hash specific fields of a foreign API

During my work as tech consultant I was many times faced by privacy issues regarding GDPR.

One client once wanted to make a report of its clients using his system using  a API and PowerBI.
The problem is that the report always came out with sensitive information, like name and email, etc. Those where fields from the API call that didn't obfuscated those sensitive fields.
While would be easy to simply remove those fields that was not an option because each data needed to be individually distinguished at the final report.

Since this client didn't owned or wanted to change the code of the API he was consulting it was impossible to change the API behaviour.

So I came up with an idea: hash the sensitive field value with an intermediary API layer.

Hashing provides a unique string representing the field value thus enabling data analysis without really revealing the sensitive data.

So I developed this server-less API layer that could be configured to obfuscate certain fields returned by the foreign API.

# How to set it up

Important file
.env
here you set up the authentication for this middleware API with this two variables
`USERNAME=yourusername` 
`PASSWORD=yourpassword` 


The easiest way would be to use Docker
Copy the Dockerfile and then:

    docker build -t api_anonymizer . && docker run -p 4557:4557 -it api_anonymizer

Acess: http://localhost:4557/docs

Or via Heroku
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/ericonetto/api_anonymizer)

## Swagger docs
http://localhost:4557/docs


## Configuring this middleware API 

You have to set up the authentication of the foreign API at the same time you set up the fields to be hashed.
If the middleware receives a HTTP 200 response from the foreign API then  hashed_fields configuration is accepted.
Call  `/config_foreign_api` 
In the headers you pass the basic authentication of this middleware API.

In the **JSON body** you pass the parameters to authenticate to the foreign API

**method**:  GET, POST

**url**: the url of the foreign API

**headers**: this is the headers of to authenticate the foreign API. DONT mistake with the headers of the middleware API.

**payload**: If needed in the process of authentication of the foreign API

**hashed_fields**: a JSON list object with the names of the fields to be obfuscated of any response from the foreign API.

With that done, you use one of those middleware API endpoints:

GET `/api` 
Passing these foreign API parameters in the this middleware header parameters:
x-method 

x-url

x-headers

x-payload

POST `/api`
Passing these foreign API parameters in the JSON body:
{
  "method": "string",
  "url": "string",
  "headers": {},
  "payload": "string"
}

*The authentication with the foreign API will be done in the background using the authentication configured on the configuration step, **so you dont need to pass it again**.*

The response will be the same response from the foreign API but will all the fields configured `/config_foreign_api` at the field  **hashed_fields** .


.

 Now you share with your team this middleware API and its authentication.
 The authentication for your team will  be with the middleware API instead of the foreign API we are obfuscating the fields.

Only a admin person with the correct authentication to the foreign API will be able to modify the fields obfuscated.

# Licence
MIT Licence

**Copyright © 11 December 2022, Erico NETTO**
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.

Except as contained in this notice, the name of the **Erico NETTO** shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the **Erico NETTO**. 
