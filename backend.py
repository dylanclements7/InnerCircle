from flask import Flask, redirect, url_for, request, make_response, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask import render_template
import jwt
import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'this'

db = SQLAlchemy(app)

class User(db.Model):
	user_name: Mapped[str] = mapped_column()
	user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	emotion: Mapped[str] = mapped_column()
	password_hash: Mapped[str] = mapped_column()

class Group(db.Model):
	group_name: Mapped[str] = mapped_column()
	group_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	is_anonymous: Mapped[bool] = mapped_column()
	passcode: Mapped[str] = mapped_column()
	interval: Mapped[int] = mapped_column()
	owner_id: Mapped[int] = mapped_column()
	
class Link(db.Model):
	user_id: Mapped[int] = mapped_column(primary_key=True)
	group_id: Mapped[int] = mapped_column()


def verify_token(token):
	success = True
	decoded_token = {}
	try:
		decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
		if decoded_token['exp'] > int(time.time()):
			# response = app.response_class(
			# 	response=json.dumps({"message": "User created successfully!", "token": token}),
			# 	status=200,
			# 	mimetype='application/json'
			# )
			# response.set_cookie('login_token', token, httponly=True, max_age=3600)

			token = generate_login_token(decoded_token['user_id'])
			decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
	except jwt.ExpiredSignatureError:
		success = False
	except jwt.InvalidTokenError:
		success = False
	
	result = jsonify({
		'success': success,
		'token': token
	})

	return result

@app.route('/check_token', methods=['POST'])
def check_token():
	token = request.form
	return verify_token(token)

@app.route('/')
def index():
	print('index')
	# check if token exists, if not log in
	# return render_template('test.html')
	token = request.cookies.get('login_token')
	# Connect using token if present
	if (token):
		token = verify_token(token)
		return render_template('dashboard.html')
		# return render_template('login.html')
		# return render_template('test.html')
	else:
		return render_template('login.html')
		# return render_template('test.html')
		
# link the new group to the creator, generate a group passkey
@app.route('/create_group', methods=['POST'])
def create_group():
	print("\ncreate_group\n")
	group_name = request.form['group_name']
	is_anonymous = 'is_anonymous' in request.form
	passcode = request.form['passcode']
	interval = request.form['interval']
	owner_id = get_user_id()
	new_group = Group(group_name=group_name, is_anonymous=is_anonymous, passcode=passcode, interval=interval, owner_id=owner_id)
	db.session.add(new_group)
	db.session.commit()
	group_id = new_group.group_id
	user_id = get_user_id()
	new_link = Link(user_id=user_id, group_id=group_id)
	db.session.add(new_link)
	db.session.commit()
	return json.dumps({"message": "Group created successfully!"})

def generate_login_token(user_id):
	expiration = int(time.time()) + 3600
	return jwt.encode({"user_id": user_id, "exp": expiration}, app.config['SECRET_KEY'], algorithm="HS256")
	
def get_user_groups(user_id):
	print("get_user_groups")
	user_groups = Link.query.filter_by(user_id=user_id).all()
	group_ids = [link.group_id for link in user_groups]
	return group_ids

def get_group_users(group_id):
	print("get_group_users")
	group_users = Link.query.filter_by(group_id=group_id).all()
	user_ids = [link.user_id for link in group_users]
	return user_ids

@app.route('/create_user', methods=['POST'])
def create_user():
	print("\ncreate_user\n")
	success = True
	values = request.get_json()
	print(f"values: {values}")
	try:
		user_name = values['user_name']
		password = values['password']
		password_hash = generate_password_hash(password)
		# print(f"user_name: {user_name}")
		# print(f"password: {password}")
		emotion = "happy"
		new_user = User(user_name=user_name, emotion=emotion, password_hash=password_hash)
	except:
		success = False
	print(f"success: {success}")
	db.session.add(new_user)
	db.session.commit()

	user_id = new_user.user_id
	token = generate_login_token(user_id= user_id)
	# response = make_response(render_template('dashboard.html'))
	# response.set_cookie('login_token', token, httponly=True, max_age=3600)

	response = jsonify({
		'success': success,
		'token': token
	})
	print(f"response: {response}")
	return response

@app.route('/login', methods=['POST'])
def login():
	print("\nlogin\n")
	success = True
	values = request.get_json()
	user_name = values['user_name']
	password = values['password']
	print(f"user_name: {user_name}")
	print(f"password: {password}")
	user = User.query.filter_by(user_name=user_name).first()
	if not user:
		success = False
	if not check_password_hash(user.password_hash, password):
		success = False
	print(f"success: {success}")

	token = generate_login_token(user.user_id)
	# response = make_response(render_template('dashboard.html'))
	response = jsonify({
		'success': success,
		'token': token
	})
	# response.set_cookie('login_token', token, httponly=True, max_age=3600)
	return response

#join a group, enter a groupname and passcode, link you to that group
@app.route('/join_group', methods=['POST'])
def join_group():
	print("join_group")
	user_id = get_user_id()
	# group_name = request.form["group_name"]
	# group_passkey = request.form["group_passkey"]
	values = request.get_json
	group_name = values['group_name']
	group_passkey = values['group_passkey']

	success = True
	try:
		group = Group.query.filter_by(group_name=group_name).first()
		if not group:
			# return json.dumps({"message":"Group does not exist"})
			success = False
		if group.passcode != group_passkey:
			# return json.dumps({"message":"Incorrect passcode"})
			success = False
		new_link = Link(user_id=user_id, group_id=group.group_id)
		db.session.add(new_link)
		db.session.commit()
	except:
		success = False

	result = jsonify({
		'success': success
	})
	return result

#leave group
@app.route('/leave_group', methods=['POST'])
def leave_group():
	print("\nleave_group\n")
	success = True
	user_id = get_user_id()
	try:
		group_name = request.form['group_name']
		group_id = Group.query.filter_by(group_name=group_name).first().group_id
		link = Link.query.filter_by(user_id=user_id, group_id=group_id).first()
		if link:
			db.session.delete(link)
			db.session.commit()
			return json.dumps({"message": "User left group successfully!"})
		else:
			return json.dumps({"message": "User not in group!"})
	except:
		success = False

	result = jsonify({
		'success': success
	})

	return result


#delete group
@app.route('/delete_group', methods=['POST'])
def delete_group():
	print("\ndelete_group\n")
	group_name = request.form['group_name']
	group_id = Group.query.filter_by(group_name=group_name).first().group_id
	owner_id = Group.query.filter_by(group_id=group_id).first().owner_id
	user_id = get_user_id()
	if owner_id != user_id:
		return json.dumps({"message": "User not owner of group!"})
	links = Link.query.filter_by(group_id=group_id).all()
	for link in links:
		db.session.delete(link)
	db.session.commit()
	group = Group.query.filter_by(group_id=group_id).first()
	db.session.delete(group)
	db.session.commit()
	return json.dumps({"message": "Group deleted successfully!"})


def get_user_id():
	token = request.cookies.get('login_token')
	decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
	return decoded_token['user_id']
	

# change emoji of a user
@app.route('/change_emoji', methods=['POST'])
def change_emoji():
	print("\nchange_emoji\n")
	success = True
	user_id = get_user_id()
	try:
		new_emoji = request.form['new_emoji']
		user = User.query.filter_by(user_id=user_id).first()
		user.emotion = new_emoji
		db.session.commit()
	except:
		success = False

		result = jsonify({
			'success': success
		})
	return result

if __name__ == '__main__':
	with app.app_context():
		db.create_all() 
	app.run(debug=True, host= '140.232.178.49', port=8080)