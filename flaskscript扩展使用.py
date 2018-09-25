#!-*-coding:utf-8-*-
# !@Date: 2018/9/19 20:12
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
1. Flask Script扩展提供向Flask插入外部脚本的功能，
2. 包括运行一个开发用的服务器，一个定制的Python shell
	设置数据库的脚本，cronjobs，及其他运行在web应用之外的命令行任务,使得脚本和系统分开；

Flask Script和Flask本身的工作方式类似，只需定义和添加从命令行中被Manager实例调用的命令；

官方文档: http://flask-script.readthedocs.io/en/latest/
"""

from flask import Flask
from flask_script import Manager

app = Flask(__name__)

# 将Manager类和应用程序实例关联
manager = Manager(app)


@app.route('/')
def index():
	return 'Index Page'


if __name__ == '__main__':
	# app.run(debug=True)
	manager.run()