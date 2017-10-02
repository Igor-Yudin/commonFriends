import json
import requests
import base64


class RequestException(Exception):
	def __init__(self, message):
		self.message = message


class SocialNetAPI():
	def  __init__(self, access_token):
		self.access_token = access_token

	def get_friends(self, user_id):
		raise NotImplementedError

	def check_user_id(self, user_id):
		raise NotImplementedError

	def reformat(self, friends):
		raise NotImplementedError

	def get_common_friends(self,
						  first_user_id,
						  second_user_id):

		a_friends = self.get_friends(first_user_id)
		b_friends = self.get_friends(second_user_id)

		common_friends = [friend for friend in a_friends if friend in b_friends]
		return common_friends


class VK_API(SocialNetAPI):
	
	def check_user_id(self, user_id):
		params = {'access_token': self.access_token,
				  'v': '5.68',
				  'user_id': user_id}
		url = 'https://api.vk.com/method/{method_name}'.format(
														method_name='users.get')
		r = requests.get(url, params=params)

		if r.ok:
			response = r.json().get('response')
			if response:
				is_active = not response[0].get('deactivated')
				return is_active
			return bool(response)
		else:
			raise RequestException(
				'Cannot proove existence of user with id={user_id}.'.format(
																	user_id=user_id))

	def get_friends(self, user_id):
		url = 'https://api.vk.com/method/friends.get'

		params = {'access_token': self.access_token,
				  'v': '5.68',
				  'user_id': user_id,
				  'fields': 'nickname,domain,photo_100,sex'}

		r = requests.get(url, params=params)

		if r.ok:
			friends = self.reformat(r.json().get('response').get('items'))
			return friends
		else:
			raise RequestException(
				'Cannot get list of friends of user with id={user_id}.'.format(
																		user_id=user_id))

	def reformat(self, friends):
		reformated = []
		for friend in friends:
			f = {'id': friend['id'],
				 'name': '%s %s' % (friend['first_name'], friend['last_name']),
				 'sex': 'female' if friend['sex'] == 1 else 'male',
				 'photo': friend['photo_100']}
			reformated.append(f)
		return reformated


class TW_API(SocialNetAPI):
	
	@staticmethod
	def get_bearer_token(consumer_key, consumer_secret):
		token = '{consumer_key}:{consumer_secret}'.format(
			consumer_key=consumer_key,
			consumer_secret=consumer_secret)

		encoded = base64.b64encode(token.encode('ascii')).decode('ascii')

		url = 'https://api.twitter.com/oauth2/token'
		auth_token = 'Basic {encoded}'.format(encoded=encoded)
		content_type = 'application/x-www-form-urlencoded;charset=UTF-8'
		data = 'grant_type=client_credentials'

		headers = {
			'Authorization': auth_token,
			'Content-Type': content_type,
		}

		r = requests.post(url, headers=headers, data=data)

		access_token = r.json().get('access_token')

		return access_token

	def check_user_id(self, user_id):
		url = 'https://api.twitter.com/1.1/users/show.json'
		auth_token = 'Bearer {access_token}'.format(access_token=self.access_token)

		headers = {
			'Authorization': auth_token,
		}

		params = {
			'user_id': user_id,
		}

		r = requests.get(url, params, headers=headers)

		if not r.ok:
			errors = r.json().get('errors')
			if errors:
				code = errors[0].get('code')
				if code in [50, 63]:
					return False
			raise RequestException(
				'Cannot proove existense of user with id={user_id}'.format(
															user_id=user_id))

		return r.ok

	def get_friends(self, user_id):
		url = 'https://api.twitter.com/1.1/friends/list.json'
		auth_token = 'Bearer {access_token}'.format(access_token=self.access_token)

		headers = {
			'Authorization': auth_token,
		}

		params = {
			'user_id': user_id,
		}

		r = requests.get(url, params, headers=headers)

		if r.ok:
			friends = r.json().get('users')
			return self.reformat(friends)
		else:
			raise RequestException(
				'Cannot get list of friends of user with id={user_id}.'.format(
																		user_id=user_id))

	def reformat(self, friends):
		reformated = []
		for friend in friends:
			f = {'id': friend['id'],
				 'name': friend['name'],
				 'sex': 'male',
				 'photo': friend['profile_image_url']}
			reformated.append(f)
		return reformated