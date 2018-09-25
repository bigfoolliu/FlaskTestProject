#!-*-coding:utf-8-*-
# !@Date: 2018/9/22 11:26
# !@Author: Liu Rui
# !@github: bigfoolliu


from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def csrf_attack():
    return render_template('csrf_attack.html')


if __name__ == '__main__':
    app.run(debug=True, port=9000)
