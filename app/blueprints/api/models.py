from datetime import datetime as dt, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	content = db.Column(db.Text)
	created = db.Column(db.DateTime, default=dt.utcnow)
	updated = db.Column(db.DateTime, onupdate=dt.utcnow)

	def __init__(self, user_id, content):
		self.user_id = user_id
		self.content = content

	def __repr__(self):
		return f'Message({self.id}; {self.user_id}: {self.content})'

	def save(self):
		db.session.add(self)
		db.session.commit()

	def edit(self, content):
		self.content = content
		self.save()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String)
	password = db.Column(db.String)
	token = db.Column(db.String, unique=True, index=True)
	token_exp = db.Column(db.DateTime)
	messages = db.relationship('Message', backref='author', lazy='dynamic')
	
	@staticmethod
	def from_username(username):
		return User.query.filter_by(username=username).first()

	@staticmethod
	def from_token(token):
		user = User.query.filter_by(token=token).first()
		if user is None or user.token_exp < dt.utcnow():
			return None
		return user

	def __init__(self, username, password):
		self.username = username
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def get_token(self):
		time = dt.utcnow()
		if self.token and self.token_exp > time + timedelta(seconds=3600):
			return self.token
		self.token = secrets.token_urlsafe(32)
		self.token_exp = time + timedelta(seconds=86400)
		self.save()
		return self.token

	def __repr__(self):
		return f'User({self.id}; {self.username})'

	def save(self):
		db.session.add(self)
		db.session.commit()