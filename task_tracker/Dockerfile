FROM python:3.10.6

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD task_tracker task_tracker/

ENV PYTHONPATH="/app:$PATH"
CMD ["python", "-m", "backend"]