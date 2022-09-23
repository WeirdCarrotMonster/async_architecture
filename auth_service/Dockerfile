FROM python:3.10.6

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD auth_service auth_service/

ENV PYTHONPATH="/app:$PATH"
CMD ["python", "-m", "auth_service"]