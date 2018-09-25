#!-*-coding:utf-8-*-
# !@Date: 2018/9/24 13:24
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
所对多映射关系:
	1. 核心点是要创建第三张'数据关联关系表'
	2. 以另外的表的主键作为字段一一对应
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
	SQLALCHEMY_DATABASE_URI = 'mysql://tonyliu:liu941103@127.0.0.1:3306/flask_test2'
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

manager.add_command('db', MigrateCommand)


"""
利用数据库的Table类来创建'数据关联关系表'
"""
tb_author_book = db.Table(
	'tb_author_book',  # 创建的表名
	db.Column('author_id', db.Integer, db.ForeignKey('authors.id')),  # 注意外键里面的'authors'是自定义的表名
	db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
)


class Author(db.Model):
	"""多对多映射关系中的"""
	__tablename__ = 'authors'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)

	"""
	建立与Book的联系,使可以访问author.books以及book.author
	因此Author需要一个books的属性
	:param: Book,表明这个关系的另一端是哪个模型
	:param: backref='author',向Book添加author属性,从而定义反向关系
	"""
	books = db.relationship(
		'Book',
		secondary=tb_author_book,
		lazy='dynamic',
		backref='author')  # 如果是一对一的关系可以传递参数uselist=False

	def __repr__(self):
		return 'Author: %s' % self.name


class Book(db.Model):
	"""多对多映射中的多"""
	__tablename__ = 'books'
	id = db.Column(db.Integer, primary_key=True)
	# 书籍的名字有可能相同
	name = db.Column(db.String(64))

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
			# 判断数据库中是否已经有该书籍
			book = Book.query.filter(Book.name==book_name).first()
			# 如果有该书籍直接添加关联,否则需要先创建该书籍
			if book:
				author.books.append(book)
			else:
				book = Book(name=book_name)
				db.session.add(book)
				# 向第三张表里添加数据
				author.books.append(book)

			db.session.commit()
			message = '添加作者 %s 成功, 添加书籍 %s 成功.' % (author_name, book_name)
			flash(message)

		# 该作者已经存在,查找对应关系时应该在第三张表里查找
		else:
			book = Book.query.filter(Book.name==book_name).first()
			if book in author.books:  # 该作者已经写过该书籍
				flash('不能重复添加书籍!')
			else:
				book = Book(name=book_name)
				author.books.append(book)
				db.session.add(book)
				db.session.commit()

	# 获取需要传入模板的数据
	authors = Author.query.all()
	return render_template(
		'book_manage_index.html',
		authors=authors
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
				db.session.delete(author)
				db.session.commit()
			except Exception as e:
				flash(e)

	return redirect(url_for('index'))


@app.route('/delete_book/<book_id>&<author_id>')
def delete_book(book_id, author_id):
	"""删除书籍"""
	try:
		book = Book.query.get(book_id)
		author = Author.query.get(author_id)
	except Exception as e:
		flash(e)
	else:
		if not book:
			flash('书籍不存在,无法删除!')
			return redirect(url_for('index'))
		else:
			# 删除该书籍时,首先应该是删除关联关系
			try:
				author.books.remove(book)
				db.session.commit()
			except Exception as e:
				flash(e)
				# 删除时发生异常,将数据库回滚
				db.session.rollback()
	return redirect(url_for('index'))


if __name__ == '__main__':
	db.drop_all()
	db.create_all()

	# 添加数据
	au1 = Author(name='au1')
	au2 = Author(name='au2')
	au3 = Author(name='au3')

	bk1= Book(name='bk1')
	bk2= Book(name='bk2')
	bk3= Book(name='bk3')
	bk4= Book(name='bk4')

	au1.books = [bk4, bk3, bk1]
	au2.books = [bk2, bk3]
	au3.books = [bk2, bk3, bk1]

	db.session.add_all([au1, au2, au3])
	db.session.add_all([bk1, bk2, bk3, bk4])
	db.session.commit()

	manager.run()
