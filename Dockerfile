FROM python:3.8-bullseye
RUN apt-get update 
RUN apt-get install -y libgeos-dev 
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./req_docker.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt
COPY ./ /app
WORKDIR /app
