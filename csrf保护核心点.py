#!-*-coding:utf-8-*-
# !@Date: 2018/9/22 8:52
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
csrf跨站请求伪造攻击原理:
	1. 用户登录了A网站在浏览器产生cookies
	2. 用户未退出A在session未过期就进入了攻击网站B
	3. 用户点击攻击网站B的带有恶意代码的链接(链接至A)
	4. 该链接可携带cookies(因为请求的目的页面是A,符合同源策略)使A网站误认为是用户的操作,从而完成攻击

A网站解决方法之一:
	增加csrf保护机制,在每一次请求的时候增加csrf验证,步骤为:
	1. 请求当前页面的时候,后台服务器生成一个csrf_token的值并放在cookies
	2. 另外后台服务器也将csrf_token值作为隐藏字段放在表单
	3. 提交表单时,后台对比着两个值,相同则可以提交

	攻击网站B不能csrf攻击原因:
		1. B即使有链接至A的代码,可携带cookies,但是却不能获取A表单中的csrf_token隐藏字段
		2. csrf_token值在每次请求时都随机生成
"""

from flask import Flask, render_template, make_response
from flask import redirect
from flask import request
from flask import url_for

# 用于csrf验证
import base64
import os


class Config(object):
	DEBUG = True


app = Flask(__name__)
app.config.from_object(Config)


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		# 两个参数都不能为空
		if not all([username, password]):
			print('参数不能为空!')
		else:
			print(username, password)
			if username == 'ray' and password =='123456':
				print('验证成功!')
				response = redirect(url_for('transfer'))
				response.set_cookie('username', username)
				return response
			else:
				print('参数错误!')
	return render_template('index.html')


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
	username = request.cookies.get('username', None)
	# 未获取到用户则未登录,直接返回主页面
	if not username:
		return redirect(url_for('index'))

	# 用户登录,且输入了转账账户和金额,返回成功
	if request.method == 'POST':
		to_account = request.form.get('to_account')  # 目的账户
		money = request.form.get('money')  # 转账金额

		# 添加csrf验证机制
		from_csrf_token = request.form.get('csrf_token')
		cookie_csrf_token = request.cookies.get('csrf_token')
		if from_csrf_token != cookie_csrf_token:  # 两者不同
			return 'csrf_token校验失败,不能转账!'

		return '%s 向账户 %s 转账 %s 元成功.' % (username, to_account, money)

	# 用户登录,未输入信息,即默认显示页面,将csrf_token值嵌入其中
	csrf_token = bytes.decode(base64.b64encode(os.urandom(48)))  # 生成了48位的csrf_token值
	response = make_response(render_template(
		'transfer.html',
		csrf_token=csrf_token
	))
	# 另外将csrf_token值写入cookie中
	response.set_cookie('csrf_token', csrf_token)
	return response


if __name__ == '__main__':
	app.run(debug=True)
