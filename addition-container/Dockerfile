FROM python:3.9
WORKDIR /app
COPY addition.py .
CMD ["python", "addition.py"]
# Add this to your Dockerfile to create the /data directory with the correct permissions
RUN mkdir -p /data && chmod 755 /data

