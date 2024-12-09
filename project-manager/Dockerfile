FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY project_manager.py .
CMD ["python", "project_manager.py"]
# Add this to your Dockerfile to create the /data directory with the correct permissions
RUN mkdir -p /data && chmod 755 /data

