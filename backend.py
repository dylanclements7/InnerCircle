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
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization", "login_token"]}})
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
    try:
        # Decode the token
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        
        # Check if token is expired
        if decoded_token['exp'] <= int(time.time()):
            success = False
            return jsonify({'success': False, 'message': 'Token expired'})
            
        # If token is valid, return success
        return jsonify({
            'success': True,
            'user_id': decoded_token['user_id'],
            'token': token  # Return same token if it's still valid
        })
        
    except jwt.ExpiredSignatureError:
        success = False
        return jsonify({'success': False, 'message': 'Token expired'})
    except jwt.InvalidTokenError:
        success = False
        return jsonify({'success': False, 'message': 'Invalid token'})

@app.route('/check_token', methods=['POST'])
def check_token():

	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]

	print(f"\ntoken: {token}\n")

    # Check if we have a token from JSON body as fallback
	if token is None and request.is_json:
		data = request.get_json()
		token = data.get('token') or data.get('login_token')
	if not token:
		return jsonify({'success': False, 'message': 'No token provided'})
	return verify_token(token)

@app.route('/')
def index():
	print('index')
	# check if token exists, if not log in
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]
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

	# values = request.get_json()
	# token = values['login_token']
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]


	user_id = get_user_id(token)
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

# load all groups and users in the groups (names and emotions), storing a a list of dictionaries
@app.route('/load_groups', methods=['POST'])
def load_groups():
	print("\nload_groups\n")

	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]

	if not token:
		return jsonify({'success': False, 'message': 'No token provided'})
	try:
        # Decode token directly (don't use verify_token here)
		decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
		user_id = decoded_token['user_id']
		print(f"user_id: {user_id}")

        # Get user groups
		group_ids = get_user_groups(user_id)
		print(f"group_ids: {group_ids}")

		if not group_ids:
			return jsonify({
				'success': True,
				'groups': []})
		groups_data = []
		
		for group_id in group_ids:
			group = Group.query.filter_by(group_id=group_id).first()
			if not group:
				continue

		group_users = get_group_users(group_id)
		users = []
		for user_id in group_users:
			user = User.query.filter_by(user_id=user_id).first()
			if user:
				users.append({"user_name": user.user_name, "emotion": user.emotion})
        
		groups_data.append({
            "name": group.group_name,
            "group_id": group.group_id,
            "is_anonymous": group.is_anonymous,
            "users": users
        })
		result = jsonify({
            'success': True,
            'groups': groups_data
        })
		print(result)
		return result
	except Exception as e:
		print(f"Error in load_groups: {str(e)}")
		return jsonify({'success': False, 'message': str(e)})

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
	# group_name = request.form["group_name"]
	# group_passkey = request.form["group_passkey"]
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]
	
	user_id = get_user_id(token)
	values = request.get_json()
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
	print(result)
	return result

#leave group
@app.route('/leave_group', methods=['POST'])
def leave_group():
	print("\nleave_group\n")
	success = True

	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]
	
	user_id = get_user_id(token)
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
	
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]

	user_id = get_user_id(token)
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


def get_user_id(token):
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return decoded_token['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
	

# change emoji of a user
@app.route('/change_emoji', methods=['POST'])
def change_emoji():
	print("\nchange_emoji\n")
	success = True
	
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]

	user_id = get_user_id(token)
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
	# app.run(debug=True, host= '192.0.0.2', port=8080)
	