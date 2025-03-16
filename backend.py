from flask import Flask, redirect, url_for, request, make_response, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask import render_template
import jwt
import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from emoji import emojize


app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization", "login_token"]}})
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'thisss'

db = SQLAlchemy(app)

# Class for storing users in SQLite
class User(db.Model):
	user_name: Mapped[str] = mapped_column()
	user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	emotion: Mapped[str] = mapped_column()
	password_hash: Mapped[str] = mapped_column()

# Class for storing groups in SQLite
class Group(db.Model):
	group_name: Mapped[str] = mapped_column()
	group_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	is_anonymous: Mapped[bool] = mapped_column()
	passcode: Mapped[str] = mapped_column()
	interval: Mapped[int] = mapped_column()
	owner_id: Mapped[int] = mapped_column()
	
# Class for storing user-group links in SQLite
class Link(db.Model):
	user_id: Mapped[int] = mapped_column()
	group_id: Mapped[int] = mapped_column()
	link_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


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

	# Generate login token
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]

	# print(f"\ntoken: {token}\n")

    # # Check if we have a token from JSON body as fallback
	# if token is None and request.is_json:
	# 	data = request.get_json()
	# 	token = data.get('token') or data.get('login_token')
	# if not token:
	# 	return jsonify({'success': False, 'message': 'No token provided'})
	return verify_token(token)

@app.route('/')
def index():
	# print('index')
	# check if token exists, if not log in
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]
	# Connect using token if present

	if (token):
		token = verify_token(token)
		return jsonify({
			'success': True,
			'token': token
		})
	else:
		return jsonify({
			'success': False,
			'token': None
		})
	
# link the new group to the creator, generate a group passkey
@app.route('/create_group', methods=['POST'])
def create_group():
	# print("\ncreate_group\n")
	success = True
	values = request.get_json()
	group_name = values['group_name']
	is_anonymous = (values['is_anonymous'] == 1)
	passcode = values['passcode']
	interval = values['interval']

	if not group_name or not passcode or not interval:
		return jsonify({
			'success': False
		})
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]


	user_id = get_user_id(token)
	new_group = Group(group_name=group_name, is_anonymous=is_anonymous, passcode=passcode, interval=interval, owner_id=user_id)
	db.session.add(new_group)
	db.session.commit()
	group_id = new_group.group_id

	# values = request.get_json()
	# token = values['login_token']
	
	new_link = Link(user_id=user_id, group_id=group_id)
	db.session.add(new_link)
	db.session.commit()

	response = jsonify({
		'success': success
	})
	# print(response)
	return response

def generate_login_token(user_id):
	expiration = int(time.time()) + 3600
	return jwt.encode({"user_id": user_id, "exp": expiration}, app.config['SECRET_KEY'], algorithm="HS256")
	
def get_user_groups(user_id):
	# print("get_user_groups")
	user_groups = Link.query.filter_by(user_id=user_id).all()
	group_ids = [link.group_id for link in user_groups]
	return group_ids

def get_group_users(group_id):
	# print("get_group_users")
	group_users = Link.query.filter_by(group_id=group_id).all()
	user_ids = [link.user_id for link in group_users]
	return user_ids

#join a group, enter a groupname and passcode, link you to that group
@app.route('/join_group', methods=['POST'])
def join_group():
	# print("join_group")
	# group_name = request.form["group_name"]
	# group_passkey = request.form["group_passkey"]
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]
	
	user_id = get_user_id(token)
	values = request.get_json()
	group_name = values['group_name']
	group_passkey = values['passcode']

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
		db.session.flush()
	except Exception as e:
		print(f"Exception: {e}")
		success = False

	response = jsonify({
		'success': success
	})
	# print(f"response: {response}")
	return response

#leave group
@app.route('/leave_group', methods=['POST'])
def leave_group():
	# print("\nleave_group\n")
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

	response = jsonify({
		'success': success
	})
	# print(f"response: {response}")
	return response


#delete group
@app.route('/delete_group', methods=['POST'])
def delete_group():
	# print("\ndelete_group\n")
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
	

# load all groups and users in the groups (names and emotions), storing a a list of dictionaries
@app.route('/load_groups', methods=['POST'])
def load_groups():
	# print("\nload_groups\n")

	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]

	if not token:
		print('No token provided')
		return jsonify({'success': False, 'message': 'No token provided'})
	try:
        # Decode token directly (don't use verify_token here)
		decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
		user_id = decoded_token['user_id']
		# print(f"user_id: {user_id}")

        # Get user groups
		group_ids = get_user_groups(user_id)
		# print(f"group_ids: {group_ids}")

		if not group_ids:
			return jsonify({
				'success': True,
				'groups': []})

		groups_data = []
		# create a list of dictionaries for each group, contains group name, list of users names in group and seperate list of user_emotions
		for group_id in group_ids:
			group_dict = {}
			group = Group.query.filter_by(group_id=group_id).first()
			user_names = []
			emotions= []
			user_ids = get_group_users(group_id)
			for user_id in user_ids:
				user = User.query.filter_by(user_id=user_id).first()
				user_names.append(user.user_name)
				emotions.append(user.emotion)
			group_dict['name'] = group.group_name
			group_dict['users'] = user_names
			group_dict['emotions'] = emotions
			groups_data.append(group_dict)
			# group_dict.append({
            # 	"name": group.group_name,
            # 	"group_id": group.group_id,
            # 	"is_anonymous": group.is_anonymous,
            # 	"users": user_names
        	# })
		
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
	# print("\ncreate_user\n")
	success = True
	values = request.get_json()
	# print(f"values: {values}")
	try:
		user_name = values['user_name']
		password = values['password']
		password_hash = generate_password_hash(password)
		# print(f"user_name: {user_name}")
		# print(f"password: {password}")
		# emotion = ":joy:"
		emotion = "😂"
		new_user = User(user_name=user_name, emotion=emotion, password_hash=password_hash)
	except Exception as e:
		print(f"Exception: {e}")
		response = jsonify({
		'success': False,
		'token': None
		})
		return response
	# print(f"success: {success}")
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
	# print(f"response: {response}")
	return response

@app.route('/login', methods=['POST'])
def login():
	# print("\nlogin\n")
	success = True
	values = request.get_json()
	user_name = values['user_name']
	password = values['password']
	# print(f"user_name: {user_name}")
	# print(f"password: {password}")
	user = User.query.filter_by(user_name=user_name).first()
	if not user:
		response = jsonify({
			'success': False,
			'token': None
		})
		return response
	elif not check_password_hash(user.password_hash, password):
		response = jsonify({
			'success': False,
			'token': None
		})
		return response
	# print(f"success: {success}")

	token = generate_login_token(user.user_id)
	# response = make_response(render_template('dashboard.html'))
	response = jsonify({
		'success': success,
		'token': token
	})
	# print(f"response: {response}")
	# response.set_cookie('login_token', token, httponly=True, max_age=3600)
	return response




def get_user_id(token):
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return decoded_token['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
	
@app.route('/get_emotion', methods=['POST'])
def get_emotion():
	# print("\nget_emotion\n")
	success = True
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]
	
	user_id = get_user_id(token)
	user = User.query.filter_by(user_id=user_id).first()
	emotion = user.emotion
	response = jsonify({
		'success': success,
		'emotion': emotion
	})
	# print(f"response: {response}")
	return response

# change emoji of a user
@app.route('/change_emoji', methods=['POST'])
def change_emoji():
	# print("\nchange_emoji\n")
	success = True
	
	token = None
	auth_header = request.headers.get('Authorization')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]

	user_id = get_user_id(token)
	try:
		new_emoji = request.get_json()['new_emoji']
		# print(f"new_emoji: {emojize(new_emoji)}")
		user = User.query.filter_by(user_id=user_id).first()
		# print(f"Before update - User: {user.user_name}, Current emoji: {user.emotion}")
		user.emotion = new_emoji
		# print(f"After update - User: {user.user_name}, New emoji: {user.emotion}")
		db.session.commit()
		db.session.flush()
		updated_user = User.query.filter_by(user_id=user_id).first()
		# print(f"After commit - User: {updated_user.user_name}, Emoji: {updated_user.emotion}")
	except Exception as e:
		print(f"Exception: {e}")
		success = False

	response = jsonify({
		'success': success
	})
	# print(response)
	return response

if __name__ == '__main__':
	with app.app_context():
		db.create_all() 
	app.run(debug=True, host= '140.232.178.49', port=8080)
	