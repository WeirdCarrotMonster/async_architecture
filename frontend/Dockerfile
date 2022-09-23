FROM python:3.10.6

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD frontend frontend/

ENV PYTHONPATH="/app:$PATH"
CMD ["python", "-m", "frontend"]