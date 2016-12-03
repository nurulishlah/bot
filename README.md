# Simple Bot Framework for Workshop

This repository is used as additional files for Qiscus chatbot workshop at Department of Computer Science of Bogor Agricultural University

### Requirements

- Python 2.7
- Git

### Installation

- Clone or download this repos `$ git clone https://github.com/nurulishlah/bot.git`
- Go to the `bot` directory `$ cd bot`
- Install requirement packages `$ pip install -r requirements.txt`
- Since it is intended to be integrated with Facebook Messenger, please provide:
    - `VERIFY_TOKEN`, can be done by running `$ export VERIFY_TOKEN="your_verify_token"`, and
    - `PAGE_ACCESS_TOKEN`, can be done by running `$ export PAGE_ACCESS_TOKEN="your_page_access_token" (get it from FB Developer Dashboard)
- Run the app `$ python app.py`

### Deploy to Heroku

- Make sure you already have Heorku Toolbelt, otherwise please refer to [Heroku Toolbelt](https://devcenter.heroku.com/articles/heroku-cli)
- Create a new heroku app. You can do it in two ways:
    1. Through Heroku Dashboard, then create new app
    2. Through heroku cli, `$ heroku create`
