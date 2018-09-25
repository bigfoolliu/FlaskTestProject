#!-*-coding:utf-8-*-
# !@Date: 2018/9/19 16:16
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
1. 错误处理之@errorhandler()
2. 自引发错误abort()
"""

from flask import Flask, redirect, abort

app = Flask(__name__)


@app.route('/')
def index():
	# 一访问就会捕获404的异常
	# abort(404)
	return 'Index Page'


@app.route('/error_page')
def error_page():
	html = '''
	<!DOCTYPE html>
	<html>
		<head>
			<meta charset="UTF-8">
			<title>Error Page</title>
		</head>
		<body>
			<h1>Error 404...</h1>
			<a href="/">Home</a>
		</body>
	</html>
	'''
	return html


# 主要发生了访问了不存在的页面就会处理
@app.errorhandler(404)
def error(e):
	# 打印出错误
	print(e)
	return redirect('/error_page')


if __name__ == '__main__':
	app.run(debug=True)
