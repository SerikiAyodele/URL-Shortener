FROM  python:3.14-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY v4-app.py ./
CMD ["gunicorn",  "-w",  "4", "v4-app:app", "-b", "0.0.0.0:5001"]

