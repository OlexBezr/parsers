from bs4 import BeautifulSoup
import requests 
import os
import inspect
import sys
from openpyxl import load_workbook
import json
from time import gmtime, strftime
import pyexcel

print('\n I\'ll leave it here :) https://t.me/bezrodnyy_olexei\n')

def valid_file_name(name_f): 
	forbidde_symbols = ['\\','?','/',':','*','"','<','>','|','%','!','@','+','.' ]
	valid_name = name_f
	for symb in forbidde_symbols : 
		valid_name = valid_name.replace(symb, '_')
	return valid_name

def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


def get_pages_data(url_page):
	all_data_pages = []

	print(f'_________________  ______________  ________________   ___\n')

	print(f'--------------------now on page - {url_page}------------------\n')
	req = requests.get( url_page, headers={
		"content-encoding": "br",
		"content-type": "text/html; charset=UTF-8",
	})
	soup = BeautifulSoup(req.text, 'html.parser')

	all_trecks = soup.find_all("div", {'class': 'dzs-layout-item'})
	for card_track in all_trecks: 
		
		card_data = {
			"last_update" : strftime("%Y %H:%M:%S", gmtime()),
			"name" : '',
			"sale": '',
			"url_to" : ''
		}
		try: 
			card_data['url_to'] = card_track.find('div', {'class': 'audioplayer-tobe'}).attrs['data-source']
		except AttributeError: 
			card_data['url_to'] = ''
		try: 
			card_data['name'] = card_track.find('div', {'class':'feed-song-name'}).string.strip()
		except AttributeError: 
			card_data['name'] = card_track.find('div', {'class': 'label-artist'}).find('a').string.strip()
		try: 
			card_data['sale'] = [ i.string if i != None else '' for i in card_track.select('.solde') ][0]
		except IndexError: 
			card_data['sale'] = False

		print(f'find - {card_data}')

		all_data_pages.append(card_data)

	return all_data_pages


def download_audio(data_list) :
	now_dir = get_script_dir() + '\\'
	if not os.path.exists( 'audio' ):
		os.mkdir( "audio" )
	for track in data_list:
		if track["url_to"] != '' and track["sale"] == 'SOLD':
			audio = requests.get( track["url_to"], stream = True )
			file_type = track["url_to"].split('.')[-1]

			if not os.path.exists( now_dir +'audio\\' + "\\"+ track['name']+'.'+file_type ):
				with open(now_dir +'audio\\' + "\\" + track['name']+'.'+file_type, 'wb') as f:
					f.write(audio.content)
				print(f'|++ downloaded: {track["name"]}.mp3 ++|')
			else :
				print(f'|-- Track: {track["name"]}.mp3 - already created --|')

def get_update_data(new_data_) : 
	try : 
		old_data = pyexcel.get_sheet(file_name="./rept.xlsx",name_columns_by_row=0)
	except FileNotFoundError: 
		print("FileNotFoundError")
		return new_data_

	records = old_data.to_records()

	def find_track_by_name(name, list_) : 
		for item in list_  :
			if name == item['name'] :
				return item
		return False
	
	l_old_data = []
	for record in records:
		keys = sorted(record.keys())
		temp_data = {}
		for key in keys:
			temp_data[key] = record[key]
		l_old_data.append(temp_data)

	update_data = []	

	for track_o in l_old_data :
		# ищю в файле exel трек из входных данных, и если он есть я обновляю данные 
		# и удаляю етот трек из входящих данных
		track_in_new = find_track_by_name( track_o['name'], new_data_)
		if track_in_new:
			track_o['sale']        = track_in_new['sale']
			track_o['last_update'] = track_in_new['last_update']
			new_data_.remove( track_in_new )
		update_data.append( track_o )

	for track_n in new_data_ : 
		# добавляю оставшыеся новые данные в update_data
		update_data.append( track_n )

	return update_data


def write_to_excel(data_list) : 
	import pyexcel
	print(f'///// now let\'s write everything in rept.xlsx\\\\\\\\\\')
	
	pyexcel.save_as(records=data_list, dest_file_name="./rept.xlsx")


print('---------------- THERE IS NO PAGINATION ON THIS SITE, ALL TRACKS WILL BE CHECKED ------------')

all_data_from_site = get_pages_data(url_page='https://www.ghost-nation.com/all-tracks/')
update_data = get_update_data( all_data_from_site )

write_to_excel( update_data )
download_audio( update_data )



# all_data_from_site = get_pages_data(url='https://edmwarriors.com/tracks?page=')
# download_audio( all_data_from_site )
# write_to_excel(all_data_from_site)
# print(all_data_from_site)



