from flask import make_response, request

from . import bp as api
from .models import User, Message

@api.post('/new_user')
def new_user():
	body = request.get_json()
	username = body['username']
	password = body['password']
	if username and password:
		if User.from_username(username) is None:
			user = User(username, password)
			user.save()
			return make_response('user created', 200)
	else:
		return make_response('username and password must be provided', 400)
	return make_response('user already exists', 409)

@api.get('/login')
def login():
	body = request.get_json()
	username = body.get('username')
	password = body.get('password')
	if username and password:
		user = User.from_username(username)
		if not user:
			return make_response('user does not exist', 404)
		if not user.check_password(password):
			return make_response('incorrect password', 401)
		return make_response({'token': user.get_token()}, 200)
	return make_response('username and password must be provided', 400)

@api.post('/message')
def post_message():
	body = request.get_json()
	token = body.get('token')
	content = body.get('content')
	if not token or not content:
		return make_response('token and content must be provided', 400)
	user = User.from_token(token)
	if user:
		msg = Message(user.id, content)
		msg.save()
		return make_response('message has been posted', 200)
	return make_response('invalid or expired token', 401)

@api.patch('/message')
def patch_message():
	body = request.get_json()
	token = body.get('token')
	message_id = body.get('message_id')
	content = body.get('content')
	if not token or not content or not message_id:
		return make_response('token, message_id, and content must be provided', 400)
	user = User.from_token(token)
	if not user:
		return make_response('invalid or expired token', 401)
	msg = Message.query.get(message_id)
	if not msg:
		return make_response('message does not exist', 404)
	if user.id != msg.user_id:
		return make_response('user is not the author of the message', 403)
	msg.edit(content)
	return make_response('message edited', 200)

@api.delete('/message')
def delete_message():
	body = request.get_json()
	token = body.get('token')
	message_id = body.get('message_id')
	if not token or not message_id:
		return make_response('token and message_id must be provided', 400)
	user = User.from_token(token)
	if not user:
		return make_response('invalid or expired token', 401)
	msg = Message.query.get(message_id)
	if not msg:
		return make_response('message does not exist', 404)
	if user.id != msg.user_id:
		return make_response('user is not the author of the message', 403)
	msg.delete()
	return make_response('message deleted', 200)

@api.get('/messages')
def messages():
	token = request.get_json().get('token')
	user = User.from_token(token)
	if not user:
		return make_response('invalid or expired token', 401)
	msgs = Message.query.order_by(Message.created.desc()).all()
	response = []
	for msg in msgs:
		response.append({
			'id': msg.id,
			'user_id': msg.author.id,
			'username': msg.author.username,
			'content': msg.content,
			'created': msg.created,
			'updated': msg.updated
		})
	return make_response({'messages': response}, 200)