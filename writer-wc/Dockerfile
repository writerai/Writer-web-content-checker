FROM python:3.10-bullseye
RUN apt-get update -y && mkdir /app
RUN apt-get install build-essential cmake python3-dev -y
COPY . /app
WORKDIR /app
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main
ENTRYPOINT [ "streamsync", "run" ]
EXPOSE 5000
CMD [ ".",  "--port", "5000", "--host", "0.0.0.0" ]

