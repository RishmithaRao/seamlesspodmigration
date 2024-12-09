FROM python:3.9-slim

WORKDIR /app

COPY mul_div.py /app/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "mul_div.py"]
