# mssql-python-pyodbc
# Python runtime with pyodbc to connect to SQL Server
FROM ubuntu:20.04

# apt-get and system utilities
RUN apt-get update && apt-get install -y \
    curl apt-utils apt-transport-https debconf-utils gcc build-essential g++-9\
    && rm -rf /var/lib/apt/lists/*

# adding custom MS repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install SQL Server drivers
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# install SQL Server tools
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"

RUN apt-get update && ACCEPT_EULA=Y apt-get install -y unixodbc-dev

# python
RUN apt-get install -y python3.8

# python libraries
RUN apt-get update && apt-get install -y \
    python3-pip python3-dev python3-setuptools \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# install necessary locales
RUN apt-get update && apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen
RUN pip3 install --upgrade pip

# install SQL Server Python SQL Server connector module - pyodbc

# install additional utilities
#RUN apt-get update && apt-get install gettext nano vim -y

# add sample code

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
COPY . /code/

ENV DJANGO_PEGASUS_SECRET_KEY=secret_key
ENV PEGASUS_SQL_USERNAME=pegasus
ENV PEGASUS_SQL_PASSWORD=8JckUhw$hxj^lxk%uQaWxmB*@lkjPOi90&
ENV PEGASUS_BLOB_NAME=pieteliteblob
ENV PEGASUS_BLOB_KEY=4DZLFy0fZHWiQ3IxC6MLF2hy3ZtmRHLGhW22e9AwQqzak+03oJ3U/2zxSZ0D3rferUg6xdjvZiFZPNeFje1TSA==
ENV AZURE_BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=pieteliteblob;AccountKey=4DZLFy0fZHWiQ3IxC6MLF2hy3ZtmRHLGhW22e9AwQqzak+03oJ3U/2zxSZ0D3rferUg6xdjvZiFZPNeFje1TSA==;EndpointSuffix=core.windows.net

RUN python3 /code/manage.py collectstatic --noinputx
