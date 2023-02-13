# Step 1: Use official lightweight Python image as base OS.
FROM python:3-alpine

ARG USERNAME
ARG PASSWORD
ENV USERNAME=$USERNAME
ENV PASSWORD=$PASSWORD

RUN apk update && apk add git

ENV APP_HOME /app
WORKDIR $APP_HOME

RUN apk update
RUN apk add git

# Clone the conf files into the docker container
RUN git clone https://github.com/ericonetto/api_anonymizer.git

WORKDIR $APP_HOME/api_anonymizer

# Step 3. Install production dependencies.
RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "api_interface:app", "--host", "0.0.0.0", "--port", "4557", "--workers", "3"]


