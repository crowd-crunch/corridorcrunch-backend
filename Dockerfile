FROM python:3.8-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update
RUN apt-cache search mariadb
RUN apt-get install -y libmariadb-dev mariadb-client gcc python3-dev musl-dev default-mysql-client

# copy project
COPY src/ /usr/src/app/

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


#RUN addgroup -S app && adduser -S app -G app
#USER app

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
