from flask import Flask, jsonify
from zappa.asynchronous import task

from lib.scraper import start_scraping

app = Flask(__name__)


@task
def scrape():
    start_scraping()


@app.route('/scrape')
def index():
    scrape()
    return "Started Scraping", 200


# We only need this for local development.
if __name__ == '__main__':
    app.run()
    