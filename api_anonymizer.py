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

import hashlib
import re
from requests import sessions



class RequestWithRashedResponse:
    
    def request(method, url, **kwargs):
        
        if "hashed_fields" in kwargs:
            hashed_fields=kwargs["hashed_fields"]
            del kwargs["hashed_fields"]

            with sessions.Session() as session:
                response =  session.request(method=method, url=url, **kwargs)


                hashed_response_text = response.text
                for field in hashed_fields:

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



