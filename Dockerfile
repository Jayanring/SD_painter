FROM python:3.8-slim-bullseye

WORKDIR /sd

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

COPY u2net.onnx /root/.u2net/

COPY main.py ./
COPY repaint_task.py ./
COPY merge_task.py ./
COPY inpaint_task.py ./
COPY preset_task.py ./
COPY sd_api.py ./
COPY util.py ./

CMD [ "python", "main.py" ]