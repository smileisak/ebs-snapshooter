# Note that ebs_snapshooter depends on aws creadentials that should be provided via ENV VARS
# Basing the Requirements Image 
FROM python:2.7-alpine

# Creating the code directory
RUN mkdir /code
WORKDIR /code

# Coping ebs_snapshooter and requirements to code dir
COPY ebs_snapshooter.py /code
COPY requirements.txt /code

# Install requirements
RUN pip install -r requirements.txt

# RUN ebs_snapshooter as an ENTRYPOINT in docker container
ENTRYPOINT ["python", "ebs_snapshooter.py"]