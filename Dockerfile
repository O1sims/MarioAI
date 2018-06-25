FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Set up apt-get
RUN apt-get -qq update

# Download Python framework and dependencies
RUN apt-get install -qq -y build-essential libffi-dev python3-dev libsdl2-2.0

# Install requirements
RUN mkdir /MarioAI
WORKDIR /MarioAI
ADD requirements.txt /MarioAI/
RUN pip install -r requirements.txt
