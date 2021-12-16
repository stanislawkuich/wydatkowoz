FROM python:latest
WORKDIR /app
RUN useradd -u 1999 -d /app bot && chown -R bot /app
ENV FLASK_APP=resources/restApi.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY  [ ".", "./" ]
RUN pip3 install -r requirements.txt
RUN chown -R bot:bot .
USER bot
EXPOSE 5000
EXPOSE 8025
CMD ["sh","-c","python wrapper_emailServer.py & flask run  "]