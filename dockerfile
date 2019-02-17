FROM python:3.6
ADD requirements.txt /app/requirements.txt
ADD ./simulationservice/ /app/
WORKDIR /app/
RUN pip3 install -r requirements.txt
ENTRYPOINT celery -A app worker --loglevel=info --pool=solo --without-heartbeat -n simulationservice@%h -Q simulation