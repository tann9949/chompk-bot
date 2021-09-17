FROM python:3.8

WORKDIR /workspace

COPY ../requirements.txt ./
RUN pip3 install python-telegram-bot
RUN pip3 install -r requirements.txt

COPY .. .

ENTRYPOINT [ "python3", "main.py" ]