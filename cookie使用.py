#!-*-coding:utf-8-*-
# !@Date: 2018/9/19 15:35
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
1. 设置cookies
2. 获取cookies
"""


from flask import Flask, make_response, request

app = Flask(__name__)


@app.route('/')
def index():
	# 获取cookie中的内容
	user_name = request.cookies.get('user_name')
	user_id = request.cookies.get('user_id')

	return 'Index Page.\nuser_name: {}\nuser_id: {}'.format(user_name, user_id)


@app.route('/login')
def login():
	# 1. 创建一个响应对象
	response = make_response('login response')
	# 2. 设置cookie(key, value, 过期时长,单位为秒)
	response.set_cookie('user_name', 'John', max_age=60)
	response.set_cookie('user_id', '1', max_age=60)
	# 3. 返回响应对象
	return response


if __name__ == '__main__':
	app.run(debug=True)
