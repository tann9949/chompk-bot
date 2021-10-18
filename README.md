# Daily Crypto Telegram Dashboard
A personal helper for telegram bot that will send daily market sentiment from the following data:
- Altcoin-season index
- Aggregated Open Interest
Also, the bot will compute buy/sell from given indicator (in this case fixed on CDC Action Zone V3)

## Usage
To use this bot, first you need to 
### Run on local
Install dependencies by running
```bash
$ pip install -r requirements.txt
```
Then, instantiate the bot by running `main.py` via the following command:
```bash
$ python main.py
```

### Run on Docker
Build an image and run a docker using the following command
```bash
$ docker-compose --build
```

## Author
Chompakorn Chaksangchaichot