#!-*-coding:utf-8-*-
# !@Date: 2018/9/21 19:59
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
使用flask_sqlalchemy库
	1. 连接数据库相关配置
	2. 简单的数据库ORM操作
	3. 一对多的关系映射中,多方定义外键,一方定义关系
"""


from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# import pymysql
#
#
# # 将pymysql和mysql融合为pymysql
# pymysql.install_as_MySQLdb()


class Config(object):
	"""配置类"""
	DEBUG = True
	"""
	连接MySQL数据库格式:
	mysql://账号:密码@ip地址:端口号/数据库名称
	"""
	SQLALCHEMY_DATABASE_URI = 'mysql://tonyliu:liu941103@127.0.0.1:3306/flask_test'
	# 跟踪数据库修改操作
	SQLALCHEMY_TRACK_MODIFICATIONS = True


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)  # 创建数据库操作实例


class Role(db.Model):
	"""
	角色模型(数据库中的一张表),继承于数据库中Model类
	每一个角色可以对应多个用户,即'一对多'中的'一'
	"""
	__tablename__ = 'roles'  # 没有设置表名的话,会默认将类名小写设置为表名
	id = db.Column(db.Integer, primary_key=True)  # 设置了主键就不必设置unique
	name = db.Column(db.String(64), unique=True)
	# 定义关系型字段,不是表的一列
	# 定义users之后可访问role.users,直接显示一个role对应的所有users
	# backref表示反向引用,user.role,直接显示一个user上的role
	users = db.relationship('User', backref='role')

	def __repr__(self):
		"""
		自定义格式化输出该模型的信息
		比如: <<print(role)
		"""
		return 'Role: %s %s' % (self.id, self.name)


class User(db.Model):
	"""用户模型(表)"""
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	# 创建外键,将User与Role分别对应
	# 即让User多一个字段role_id,其中的内容为Role.id,所以其数据类型应一致
	role_id = db.Column(db.Integer, db.ForeignKey(Role.id))

	def __repr__(self):
		return 'User: %s %s' % (self.id, self.name)


@app.route('/')
def index():
	return 'Index Page'


if __name__ == '__main__':

	# 删除数据库所有表(慎用,之后会用数据迁移代替)
	db.drop_all()
	# 初始化创建表格
	db.create_all()
	app.run()

