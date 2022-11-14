FROM python:3.8

WORKDIR /workspace

COPY . .
RUN pip3 install python-telegram-bot
RUN pip3 install -r requirements.txt


ENTRYPOINT [ "python3", "run_bot.py" ]
