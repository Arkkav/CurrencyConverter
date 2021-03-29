FROM python:latest
COPY . .
EXPOSE 5000
CMD python main.py