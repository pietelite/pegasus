FROM python:3
ENV PYTHONUNBUFFERED=1


RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

# ssh
#ENV WEBSITES_PORT 8000
#ENV SSH_PASSWD "root:Docker!"
#RUN apt-get update \
#        && apt-get install -y --no-install-recommends dialog \
#        && apt-get update \
#	&& apt-get install -y --no-install-recommends openssh-server \
#	&& echo "$SSH_PASSWD" | chpasswd
#
#COPY sshd_config /etc/ssh/
#
#EXPOSE 8000 2222
