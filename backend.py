from flask import Flask, redirect, url_for, request
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask import render_template
import jwt
from datetime import datetime, timedelta



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'this'

db = SQLAlchemy(app)

class User(db.Model):
	user_name: Mapped[str] = mapped_column()
	user_id: Mapped[int] = mapped_column(primary_key=True)
	emotion: Mapped[str] = mapped_column()

class Group(db.Model):
	group_name: Mapped[str] = mapped_column()
	group_id: Mapped[int] = mapped_column(primary_key=True)
	is_anonymous: Mapped[bool] = mapped_column()
	passcode: Mapped[str] = mapped_column()
	
class Link(db.Model):
	user_id: Mapped[int] = mapped_column(primary_key=True)
	group_id: Mapped[int] = mapped_column()

def verify_token(token):
	decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
	if (datetime(decoded_token['exp']) < datetime.now()):
		return generate_login_token(decoded_token['user_id'])
	return decoded_token

@app.route('/')
def index():
	# check if token exists, if not log in
	token = request.cookies.get('login_token')
	# Connect using token if present
	if (token):
		token = verify_token(token)
		return render_template('dashboard.html')
	else:
		return render_template('login.html')
		
# link the new group to the creator, generate a group passkey
@app.route('/create_group', methods=['POST'])
def create_group():
	group_name = request.json['group_name']
	group_id = request.json['group_id']
	is_anonymous = request.json['is_anonymous']
	passcode = request.json['passcode']
	new_group = Group(group_name=group_name, group_id=group_id, is_anonymous=is_anonymous, passcode=passcode)
	db.session.add(new_group)
	db.session.commit()
	return json.dumps({"message": "Group created successfully!"})

def generate_login_token(user_id):
	expiration = datetime.now() + timedelta(hours=1)
	try:
		token = request.headers.get('Authorization')
		print('\n',token,'\n')
		token = token.split("Bearer ")[1]  # Strip "Bearer " from token
	except jwt.InvalidTokenError:
		return json.dumps({"message": "Invalid token!"})
	return jwt.encode({"user_id": user_id, "exp": expiration}, app.config['SECRET_KEY'], algorithm="HS256")


def get_user_groups(user_id):
	user_groups = Link.query.filter_by(user_id=user_id).all()
	group_ids = [link.group_id for link in user_groups]
	return group_ids

def get_group_users(group_id):
	group_users = Link.query.filter_by(group_id=group_id).all()
	user_ids = [link.user_id for link in group_users]
	return user_ids

@app.route('/create_user', methods=['POST'])
def create_user():
	user_name = request.json['user_name']
	user_id = request.json['user_id']
	emotion = request.json['emotion']
	new_user = User(user_name=user_name, user_id=user_id, emotion=emotion)
	db.session.add(new_user)
	db.session.commit()
	
	token = generate_login_token(user_id= user_id)
	response = app.response_class(
		response=json.dumps({"message": "User created successfully!", "token": token}),
		status=200,
		mimetype='application/json'
	)
	response.set_cookie('login_token', token, httponly=True, max_age=3600)
	return response
	# return json.dumps({"message": "User created successfully!", "token": token})


#join a group, enter a groupname and passcode, link you to that group
@app.route('/join_group', methods=['POST'])
def join_group():
	user_id = get_user_id()
	group_name = request.json["group_name"]
	group_passkey = request.json["group_passkey"]
	group = Group.query.filter_by(group_name=group_name).first()
	if not group:
		return json.dumps({"message":"Group does not exist"})
	if group.passcode != group_passkey:
		return json.dumps({"message":"Incorrect passcode"})
	new_link = Link(user_id=user_id, group_id=group.group_id)
	db.session.add(new_link)
	db.session.commit()
	return json.dumps({"message": "User joined group successfully!"})


def get_user_id():
	token = request.cookies.get('login_token')
	token = verify_token(token)
	return token['user_id']
	

# change emoji of a user
@app.route('/change_emoji', methods=['POST'])
def change_emoji():
	user_id = get_user_id()
	new_emoji = request.json['new_emoji']
	user = User.query.filter_by(user_id=user_id).first()
	user.emotion = new_emoji
	db.session.commit()
	return json.dumps({"message": "Emoji changed successfully!"})

if __name__ == '__main__':
	with app.app_context():
		db.create_all() 
	app.run(debug=True, port=8080)

	