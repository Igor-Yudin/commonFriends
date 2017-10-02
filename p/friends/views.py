from django.shortcuts import render
from django.http import HttpResponse
import sys
import json
import requests
import base64
from friends.social_net_api import (RequestException, VK_API, TW_API)


TW_CONSUMER_KEY = 'rujZnThe5tMYuyBkAqrpxFhTs'
TW_CONSUMER_SECRET = 'w0QE0aB2LqZxJtfnAKtICRnsWHd5F7SV4XQ1TRKBtaKnR6cJh3'
VK_ACCESS_TOKEN = 'dcebe032dcebe032dcebe032dedcb56f45ddcebdcebe0328522cbdbc58d4fa4cece705d'
TW_ACCESS_TOKEN = TW_API.get_bearer_token(TW_CONSUMER_KEY,
										  TW_CONSUMER_SECRET)

API = {
	'vk': VK_API,
	'tw': TW_API,
}

ACCESS_TOKEN = {
	'vk': VK_ACCESS_TOKEN,
	'tw': TW_ACCESS_TOKEN,
}

# CHECK_FUNC = {
# 	'vk': check_user_vk,
# 	'tw': check_user_tw,
# }

# GET_FRIENDS_FUNC = {
# 	'vk': get_friends_vk,
# 	'tw': get_friends_tw,
# }

# REFORMAT_FUNC = {
# 	'vk': reformat_response_vk,
# 	'tw': reformat_response_tw,
# }


# class RequestException(Exception):
# 	def __init__(self, message):
# 		self.message = message


# def get_bearer_token_tw():
# 	encoded_b =  base64.b64encode('{consumer_key}:{consumer_secret}'.encode('ascii'))
# 	encoded = encoded_b.decode('ascii')

# 	url = 'https://api.twitter.com/oauth2/token'
# 	auth_token = 'Base {encoded}'.format(encoded=encoded)
# 	content_type = 'application/x-www-form-urlencoded;charset=UTF-8'
# 	data = 'grant_type=client_credentials'

# 	headers = {
# 		'Authorization': auth_token,
# 		'Content-Type': content_type,
# 	}

# 	r = requests.post(url, headers=headers, data=data)

# 	access_token = r.json().get('access_token')

# 	if access_token:
# 		return access_token
# 	else:
# 		raise RequestException('Cannot get access to twitter')

def home(request):
	errors = []
	if not TW_ACCESS_TOKEN:
		errors.append('Cannot get access to twitter')
	return render(request, 'friends/home.html', {'errors': errors})

def check_user_id_ajax(request):
	if request.is_ajax() or request.method == 'POST':

		user_id = request.POST.get('userId')
		net = request.POST.get('net')

		try:
			assert net in ['vk', 'tw']
		except:
			return HttpResponse('Bad request', status=400)

		access_token, api = ACCESS_TOKEN[net], API[net]

		r = api(access_token)

		try:
			correct = r.check_user_id(user_id)
			message = 'OK' if correct else 'User with that id did not found.'

			return HttpResponse(json.dumps({'correct': correct,
											'message': message}))
		except RequestException as e:
			return HttpResponse(json.dumps({'correct': False,
											'message': e.message}))
		except Exception as e:
			print('{}: {}'.format(type(e), str(e)))
			return HttpResponse(
				json.dumps({'correct': False,
							'message': 'Something goes wrong with that id...'}))
	else:
		return HttpResponse('Forbidden', status=403)

def get_list_ajax(request):
	if request.is_ajax() or request.method == 'POST':
		
		net = request.POST.get('net')
		first_id = request.POST.get('firstId')
		second_id = request.POST.get('secondId')

		try:
			assert net in ['vk', 'tw']
		except:
			return HttpResponse('Bad request', status=400)

		# get_friends = GET_FRIENDS_FUNC[net]
		# reformat = REFORMAT_FUNC[net]

		access_token, api = ACCESS_TOKEN[net], API[net]

		r = api(access_token)

		try:
			# first_user_friends = get_friends(first_id)
			# second_user_friends = get_friends(second_id)
			# common_friends = get_common_friends(first_user_friends,
			# 									second_user_friends)
			common_friends = r.get_common_friends(first_id,
												  second_id)

		except RequestException as e:
			return HttpResponse(json.dumps({'ok': False,
											'message': e.message}))
		except Exception:
			return HttpResponse(json.dumps({
				'ok': False,
				'message': 'Something goes wrong...'}))

		return HttpResponse(json.dumps({'ok': True,
										'friendsList': common_friends,
										'message': 'All is ok'}))
	else:
		return HttpResponse('Forbidden', status=403)

# def get_common_friends(a_friends, b_friends):
# 	common_friends = [friend for friend in a_friends if friend in b_friends]
# 	return common_friends

# def check_user_tw(uset_id):
# 	url = 'https://api.twitter.com/1.1/users/show.json'
# 	auth_token = 'Bearer {access_token}'.format(access_token=TW_ACCESS_TOKEN)
# 	headers = {
# 		'Authorization': auth_token,
# 	}
# 	params = {
# 		'user_id': user_id,
# 	}
# 	r = requests.get(url, params, headers=headers)

# 	return r.ok

# def check_user_vk(user_id):
# 	params = {'access_token': VK_ACCESS_TOKEN,
# 			  'v': '5.68',
# 			  'user_id': user_id}
# 	url = 'https://api.vk.com/method/{method_name}'.format(
# 													method_name='users.get')
# 	r = requests.get(url, params=params)

# 	if r.ok:
# 		response = r.json().get('response')
# 		if response:
# 			is_active = not response[0].get('deactivated')
# 			return is_active
# 		return bool(response)
# 	else:
# 		raise RequestException(
# 			'Cannot proove existence of user with id={user_id}.'.format(
# 																user_id=user_id))

# def get_friends_tw(user_id):
# 	url = 'https://api.twitter.com/1.1/friends/list.json'
# 	auth_token = 'Bearer {access_token}'.format(access_token=TW_ACCESS_TOKEN)
# 	headers = {
# 		'Authorization': auth_token,
# 	}
# 	params = {
# 		'user_id': user_id,
# 	}

# 	r = requests.get(url, params, headers=headers)

# 	if r.ok:
# 		return r.json().get('users')
# 	else:
# 		raise RequestException(
# 			'Cannot get list of friends of user with id={user_id}.'.format(
# 																	user_id=user_id))

# def get_friends_vk(user_id):
# 	url = 'https://api.vk.com/method/{method_name}'.format(
# 													method_name='friends.get')
# 	params = {'access_token': VK_ACCESS_TOKEN,
# 			  'v': '5.68',
# 			  'user_id': user_id,
# 			  'fields': 'nickname,domain,photo_100,sex'}
# 	r = requests.get(url, params=params)

# 	if r.ok:	
# 		return r.json().get('response').get('items')
# 	else:
# 		raise RequestException(
# 			'Cannot get list of friends of user with id={user_id}.'.format(
# 																	user_id=user_id))

# def reformat_response_tw(friends):
# 	reformated = []
# 	for friend in friends:
# 		f = {'id': friend['id'],
# 			 'name': friend['name'],
# 			 'sex': 'male',
# 			 'photo': friend['profile_image_url']}
# 		reformated.append(f)
# 	return reformated

# def reformat_response_vk(friends):
# 	reformated = []
# 	for friend in friends:
# 		f = {'id': friend['id'],
# 			 'name': '%s %s' % (friend['first_name'], friend['last_name']),
# 			 # 'nickname': friend['nickname'],
# 			 # 'domain': friend['domain'],
# 			 'sex': 'female' if friend['sex'] == 1 else 'male',
# 			 'photo': friend['photo_100']}
# 		reformated.append(f)
# 	return reformated