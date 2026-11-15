FROM python:3.12-slim
WORKDIR /srv
COPY server.py /srv/server.py
COPY initial.json /srv/initial.json
RUN mkdir -p /state && chmod 700 /state
EXPOSE 8000
CMD ["python", "/srv/server.py"]
