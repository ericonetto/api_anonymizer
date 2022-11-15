import hashlib
import re
from requests import sessions



class RequestWithRashedResponse:
    
    def request(method, url, **kwargs):
        
        if "hashed_filds" in kwargs:
            hashed_filds=kwargs["hashed_filds"]
            del kwargs["hashed_filds"]

            with sessions.Session() as session:
                response =  session.request(method=method, url=url, **kwargs)


                hashed_response_text = response.text
                for field in hashed_filds:

                    regex = re.compile("\"" + field + r"\":\"(?P<value>.*?)\"", re.IGNORECASE)
                    list_to_hash=regex.findall(hashed_response_text)#.group("value")
                    for to_hash in list_to_hash:
                        hashed_value= hashlib.sha256(str(to_hash).encode('utf-8')).hexdigest()
                        regex_replace = re.compile("\"" + field + "\":\"" + to_hash + "\"", re.IGNORECASE)
                        hashed_response_text = regex_replace.sub("\"" + field +  "\":\"%s\"" % hashed_value, hashed_response_text)

                response.encoding, response._content = response.encoding, hashed_response_text.encode(response.encoding)

                return response
        else:
            with sessions.Session() as session:
                return session.request(method=method, url=url, **kwargs)



