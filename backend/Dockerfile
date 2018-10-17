FROM python:3.6

ENV BACKEND_PATH /backend

WORKDIR ${BACKEND_PATH}

COPY requirements.txt ${BACKEND_PATH}

RUN pip install -r requirements.txt

COPY . ${BACKEND_PATH}
