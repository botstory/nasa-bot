# NASA bot [![Coverage Status](https://coveralls.io/repos/github/botstory/nasa-bot/badge.svg?branch=develop)](https://coveralls.io/github/botstory/nasa-bot?branch=develop) [![Updates](https://pyup.io/repos/github/botstory/nasa-bot/shield.svg)](https://pyup.io/repos/github/botstory/nasa-bot/) [![Python 3](https://pyup.io/repos/github/botstory/nasa-bot/python-3-shield.svg)](https://pyup.io/repos/github/botstory/nasa-bot/) [![Build Status](https://travis-ci.org/botstory/nasa-bot.svg?branch=master)](https://travis-ci.org/botstory/nasa-bot) 
:globe_with_meridians: made for [Data Concierge challenge](https://2017.spaceappschallenge.org/challenges/ideate-and-create/data-concierge/)

## Run tests

Should have installed pytest

Run inside of docker
```bash
docker-compose -f docker-sync-compose.yaml -f docker-compose-dev.yaml exec bot pytest
```

pure
```bash
pytest
```

## More information

- :memo: [Awesome List of NASA Space Apps Challenge 2017](https://gist.github.com/hyzhak/2586979d8951a6ec508faa58191395fe)
- :rocket: Based on [bot story](https://github.com/botstory/botstory) framework
- :information_desk_person: [Emma (virtual assistant)](https://www.uscis.gov/emma) chatbot which is used in US Citizenship and Immigration Service
