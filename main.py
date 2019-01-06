from flask import Flask, render_template
from flask_restful import Api
from flask_cors import CORS
from query import GQuery
from test import HelloWorld

app = Flask(__name__)
CORS(app, supports_credentials=True)
api = Api(app)
api.add_resource(GQuery, "/query")


@app.route('/')
def index():
# 网页不知道怎么用restful的方式
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0")

