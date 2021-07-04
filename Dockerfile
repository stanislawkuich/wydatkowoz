FROM python:latest
WORKDIR /app
ENV FLASK_APP=resources/restApi.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY  [ ".", "./" ]
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["flask", "run"]