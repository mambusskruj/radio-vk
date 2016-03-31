import requests
import json
import random
import time

access_token = ''
public_id = ''

info = json.loads(open('account-vk.json').read())

for member_info in info:
	access_token = member_info['token']
	public_id = member_info['public id']


list_audio = []
list_random_playlist = []
random.seed(version=2)

rq = requests.get('https://api.vk.com/method/audio.get?owner_id='+public_id+'&album_id=0&v=5.45&access_token='+access_token).json()


def outJson(listdict_from_request):
	f_listdict_from_req = open('songs-from-public.json', 'w')
	f_listdict_from_req.write(json.dumps(listdict_from_request, sort_keys = True, indent = 4))
	f_listdict_from_req.close()

def getAudioList():
	#rq = requests.get('https://api.vk.com/method/audio.get?owner_id='+public_id+'&album_id=0&v=5.45&access_token='+access_token).json()
	listdict_from_request = []
	dict_request = {}
	id_list = []

	for audio in rq['response']['items']:
		dict_request = {'id' : audio['id'], 'owner' : audio['owner_id'], 'artist' : audio['artist'], 'title' : audio['title'] }
		listdict_from_request.append(dict_request)
		id_list.append(dict_request['id'])


	outJson(listdict_from_request)

	return id_list

def smartSaveList(playlist):
	#удаляем из составленного списка 80% объектов, возвращает список созраненных
	save_list = []
	remove_list = playlist

	#TODO: проверить условие
	if len(playlist)<50:
		save_list=''
	else:
		while len(save_list)<10:
			save_list.append(random.choice(playlist))

	return save_list

def getRandomList(list_from_request, save_list=''):
	random_list = []
	choice = 0

	#TODO: протестить условие
	if len(list_from_request) < 50:
		random_list.append(random.choice(list_from_request))
	else:
		while len(random_list) < 50-len(save_list):
			choice = random.choice(list_from_request)
			if choice not in random_list:
				random_list.append(choice)

		for id in save_list:
			random_list.append(id)

	return random_list 


def randomPlay(random_playlist):
	#рандом без повторений, пока есть неспетые песни
	time_dict = {}
	for audio in rq['response']['items']:
		if audio['id'] in random_playlist:
			time_dict[audio['id']] = audio['duration']

	for song in random_playlist:
		rq2 = requests.get('https://api.vk.com/method/audio.setBroadcast?audio='+public_id+'_'+str(song)+'&target_ids='+public_id+'&v=5.45&access_token='+access_token).json()
		time.sleep(time_dict[song])


def removePastSongs(song_list, past_playlist):
	for song in past_playlist:
		if song in song_list:
			song_list.remove(song) 

	return song_list




list_audio = getAudioList()
random_playlist = getRandomList(list_audio)
play = randomPlay(random_playlist)


while (len(list_audio) > 0):
	# удаляем 80% проигранных аудиофайлов, переопределяем плейлист - 80% новых + 20% из прошлого
	save_list = smartSaveList(random_playlist)
	list_audio = removePastSongs(list_audio, random_playlist)
	random_playlist = getRandomList(list_audio, save_list)
	play = randomPlay(random_playlist)

#TODO: проверить работу скрипта, когда плейлист <50 песен. все ли функции работают корректно, и нормально ли заверщается работа скрипта.