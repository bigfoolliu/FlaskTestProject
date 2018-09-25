#!-*-coding:utf-8-*-
# !@Date: 2018/9/19 16:01
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
1. session会话的设置
2. session会话的密钥设置
"""

from flask import Flask, session

app = Flask(__name__)
# 设置密钥
app.config['SECRET_KEY'] = '123123123'


@app.route('/')
def index():
	return 'Index Page'


@app.route('/login')
def login():
	# 设置session
	session['user_name'] = 'John'
	session['user_id'] = '1'
	return 'Login succeed!'


if __name__ == '__main__':
	app.run(debug=True)
