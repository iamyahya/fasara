FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

CMD /wait && \
    alembic upgrade head && \
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
