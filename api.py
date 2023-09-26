import time

from flask import Flask
from gunicorn.app.base import Application
from gunicorn.config import Config


flask_app = Flask(__name__)


@flask_app.route("/ok-1s")
def ok():
    time.sleep(1)
    return "Ok"


class CustomGunicornApplication(Application):
    def do_load_config(self):
        self.cfg = Config()
        self.cfg.set("bind", "localhost:8011")
        self.cfg.set("workers", 1)

    def load(self):
        return flask_app


if __name__ == "__main__":
    gunicorn_app = CustomGunicornApplication().run()
