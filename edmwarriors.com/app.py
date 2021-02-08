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




def get_pages_data(url, range_form=1, range_to=1):
	all_data_pages = []

	for iter_page in range(range_form, range_to+1 ):
		url_page = f'{url}{iter_page}' 
		print(f'_________________  ______________  ________________   ___\n')

		print(f'--------------------now on page - {url_page}------------------\n')
		req = requests.get( url_page )
		soup = BeautifulSoup(req.text, 'html.parser')

		all_trecks = soup.find("div", {'class': 'grid-5__sm-2__xs-1'}).find_all('div',{'class':'col'})
		# print(all_trecks)
		for card_track in all_trecks: 
			img_src = card_track.find('div',{'class':'BeatItem_Top'}).find('img').attrs['src']

			# https://s3-eu-west-1.amazonaws.com/myghostmarket/img/cover/track/5379.jpg -> 5379.jpg -> 5379
			img_id = img_src.split('/')[-1].split('.')[0]

			card_data = {
				"last_update" : strftime("%d %B %Y ", gmtime()),
				"id": img_id,
				"name" : valid_file_name( card_track.find('a', {'class':'name'}).string.strip() ),
				"sale": '',
				"url_to" : "https://s3-eu-west-1.amazonaws.com/myghostmarket/track/" + img_id + ".ogg",
			}

			try: 
				card_data['sale'] = [ i.string if i != None else '' for i in card_track.select('.beatItem_soldLayer') ][0]
			except IndexError: 
				card_data['sale'] = False

			# print(f'find - {card_data}')

			all_data_pages.append(card_data)

	return all_data_pages

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


def download_audio(data_list) :
	now_dir = get_script_dir() + '\\'
	if not os.path.exists( 'audio' ):
		os.mkdir( "audio" )
	for track in data_list:
		if track['sale'] == 'SOLD' and track["url_to"] != '':
			
			audio = requests.get( track["url_to"], stream = True )
			file_type = track["url_to"].split('.')[-1]
			if not os.path.exists( now_dir + 'SOLD\\'+ track['id'] + '_' + track['name']+'.'+file_type ):
				with open(now_dir +'audio\\' + "\\" +  track['id'] + '_' +  track['name']+'.'+file_type, 'wb') as f:
					f.write(audio.content)
				print(f'|++ downloaded: {track["id"]}_{track["name"]}.ogg ++|')
			else :
				print(f'|-- Track: {track["id"]}_{track["name"]}.ogg - already created --|')


def write_to_excel(data_list) : 
	import pyexcel
	print(f'///// now let\'s write everything in rept.xlsx\\\\\\\\\\')
	
	pyexcel.save_as(records=data_list, dest_file_name="./rept.xlsx")


print('----------------HERE WE MEAN PAGINATION------------')
while True: 
	try:
		range_from_ = int(input('Enter from which page to start checking?\n'))
		break
	except:
		print("Need number :\\")


while True: 
	try:
		range_to_ = int(input('Enter on which page to finish?\n'))
		break
	except:
		print("Need number :\\")
all_data_from_site = get_pages_data(url='https://edmwarriors.com/tracks?page=', range_form=range_from_, range_to=range_to_)
update_data = get_update_data( all_data_from_site )


write_to_excel( update_data )
download_audio( update_data )



