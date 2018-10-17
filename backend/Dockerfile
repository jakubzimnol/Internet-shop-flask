FROM python:3.6

ENV BACKEND_PATH /backend

WORKDIR ${BACKEND_PATH}

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .
