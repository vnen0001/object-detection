FROM python:3.11
WORKDIR /app
COPY requirements.txt /app
COPY . .

RUN apt-get update -y \
	&&  apt-get install -y  libsm6 libxext6 libxrender-dev libgl1-mesa-glx libglib2.0-0 

RUN python3 -m venv venv \
    && venv/bin/pip install --no-cache-dir -r requirements.txt
EXPOSE 5050
CMD ["venv/bin/python3","object_detection.py"]

