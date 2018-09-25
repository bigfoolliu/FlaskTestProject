#!-*-coding:utf-8-*-
# !@Date: 2018/9/22 21:53
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
数据库版本更新,迁移等
"""


from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy

# 为数据库迁移引入
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager


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

	SECRET_KEY = 'session_secret_key'


app = Flask(__name__)
app.config.from_object(Config)


# 创建数据库对象,并绑定app
db = SQLAlchemy(app)

migrate = Migrate(app, db)

"""
1. 创建迁移对象并将应用和数据库绑定至迁移对象
2. manager是Flask-Script的实例，在flask-Script中添加一个db命令,即'迁移命令'
"""
manager = Manager(app)

# 将MigrateCommand命令命名为'db'并注册到manager管理对象里
manager.add_command('db', MigrateCommand)


class Author(db.Model):
	"""一对多映射关系中的一"""
	__tablename__ = 'authors'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	gender = db.Column(db.String(64))

	"""
	建立与Book的联系,使可以访问author.books以及book.author
	因此Author需要一个books的属性
	:param: Book,表明这个关系的另一端是哪个模型
	:param: backref='author',向Book添加author属性,从而定义反向关系
	"""
	books = db.relationship('Book', backref='author')

	def __repr__(self):
		return 'Author: %s' % self.name


class Book(db.Model):
	"""一对多中的多"""
	__tablename__ = 'books'
	id = db.Column(db.Integer, primary_key=True)
	# 书籍的名字有可能相同
	name = db.Column(db.String(64))
	# author_id字段表明该书属于哪个作者,是书籍的外键
	author_id = db.Column(db.Integer, db.ForeignKey(Author.id))

	def __repr__(self):
		return 'Book: %s: %s' %(self.id, self.name)


@app.route('/', methods=['GET', 'POST'])
def index():
	"""可添加作者和书籍至数据库并显示
	思路:
		1. 获取表单中提交的数据
		2. 判断提交的数据是否合法
		3. 判断提交的作者以及书籍是否在数据库中
			3.1 作者存在则直接将书籍关联
			3.2 作者不存在则首先创建一个新的作者,然后同理处理书籍
		4. 提示不能提交或者可以提交,并将数据保存至数据库显示
	"""
	if request.method == 'POST':
		author_name = request.form.get('author')
		book_name = request.form.get('book')

		# 只要有一个为空都不能提交
		if not all([author_name, book_name]):
			flash('参数不足,不能提交!')
			return redirect(url_for('index'))

		# else:
		# 判断数据库中是否已经有该作者
		author = Author.query.filter(Author.name==author_name).first()
		if not author:
			author = Author(name=author_name)
			db.session.add(author)
			db.session.commit()

			book = Book(name=book_name, author_id=author.id)
			db.session.add(book)
			db.session.commit()
		# 该作者已经存在
		else:
			"""改变自己的观念,现在是操作数据库相关"""
			# # 首先判断该作者是不是已经有该书了
			# for old_book in author.books:
			# 	if not old_book.name == book_name:
			# 		# 将书籍关联该作者
			# 		book = Book(name=book_name, author_id=author.id)
			# 		db.session.add(book)
			# 		db.session.commit()
			# 		break

			book = Book.query.filter(Book.name==book_name).first()
			if book:  # 该作者已经写过该书籍
				flash('不能重复添加书籍!')
			else:
				book = Book(name=book_name, author_id=author.id)
				db.session.add(book)
				db.session.commit()

	# 获取需要传入模板的数据
	authors = Author.query.all()
	return render_template(
		'book_manage_index.html',
		authors=authors,
		# books=books
	)


@app.route('/delete_author/<author_id>')
def delete_author(author_id):
	"""访问该视图函数,将url对应id的作者删除
	思路:
		1. 首先判断要删除的是否在数据库
			1.1 当用户不存在于数据库
				1.1.1 产生异常信息并将其显示给用户
			1.2 当用户存在于数据库
				1.2.1 首先删除当前用户的所有的书籍
				1.2.2 然后删除该作者
		2. 默认直接重定向至主页

	"""
	# 判断删除的作者是不是在数据库,为了防止恶意修改的url的访问,产生意外错误
	try:
		# 找出数据库中对应id的作者
		author = Author.query.get(author_id)  # 注意参数
		# print('找到的首个作者为: ', author)
	except Exception as e:
		# 将错误信息闪现给用户
		flash(e)
	else:
		# 如果作者不存在
		if not author:
			flash('删除的作者不存在,不能删除')
			return
		else:
			try:
				# 作者存在
				for book in author.books:
					db.session.delete(book)
				# db.session.commit()  # 这一句可省略,在下面一起提交
				db.session.delete(author)
				db.session.commit()
			except Exception as e:
				flash(e)

	return redirect(url_for('index'))


@app.route('/delete_book/<book_id>')
def delete_book(book_id):
	"""删除书籍"""
	try:
		book = Book.query.get(book_id)
	except Exception as e:
		flash(e)
	else:
		if not book:
			flash('书籍不存在,无法删除!')
			return redirect(url_for('index'))
		else:
			try:
				db.session.delete(book)
				db.session.commit()
			except Exception as e:
				flash(e)
				# 删除时发生异常,将数据库回滚
				db.session.rollback()
	return redirect(url_for('index'))


if __name__ == '__main__':
	# # 删除表格(之后用数据库迁移代替)
	# db.drop_all()
	# # 创建表格
	# db.create_all()
	#
	# # 向表格添加数据
	# au1 = Author(name='赵')
	# au2 = Author(name='钱')
	# au3 = Author(name='孙')
	# au4 = Author(name='李')
	#
	# """
	# 注意:
	# 	必须先提交Author,再提交Book,因为Book有外键链接至Author
	# """
	# # 提交数据给用户会话
	# db.session.add_all([au1, au2, au3, au4])
	# # 提交会话,存储进数据库
	# db.session.commit()
	#
	# """注意此处au_book只是列的标题,实际参数应该是定义的author.id"""
	# bk1 = Book(name='小赵游记', author_id=au1.id)
	# bk2 = Book(name='钱钱钱', author_id=au2.id)
	# bk3 = Book(name='读书少就要多读书', author_id=au3.id)
	# bk4 = Book(name='创造百万财富', author_id=au4.id)
	# bk5 = Book(name='寻找自我', author_id=au1.id)
	# bk6 = Book(name='摄影大师是如何摄影的', author_id=au2.id)
	#
	# db.session.add_all([bk1, bk2, bk3, bk4, bk5, bk6])
	# db.session.commit()

	# app.run(debug=True)
	manager.run()
