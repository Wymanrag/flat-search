#! /usr/bin/python
#flat-serach.py v1
#
#Search for houses on some sites

#START
import ConfigParser
import subprocess
import json
import hashlib
import logging
import os

# def cleanOLX(j2clean):
#  	nr=0
#  	j2clean_aux = j2clean
#  	for a in j2clean_aux["results"]:
#  		if "all" in a:
#  			nr=nr+1
#  			print a["all"].encode('utf-8')
#  			print nr
#  		else:
#  			#j2clean["results"].pop(nr)
#  			del j2clean["results"][nr]
#  			#print j2clean["results"][nr]
#  	return j2clean

def cleanOLX(j2clean):
 	nr=0
 	j2clean_aux = []
 	for a in j2clean["results"]:
 		if "all" in a:
 			j2clean_aux.append(a)
 	return j2clean_aux

def main():
	logging.basicConfig(level=logging.INFO)
	
	logging.info('STARTED flat-serach.py...')
	
	#READ settings.conf
	parser = ConfigParser.ConfigParser ()
	parser.read('settings.conf')
	user_guid = parser.get('OLX', 'USER_GUID')
	urlencoded_api_key = parser.get('OLX', 'urlencoded_api_key')
	extractor_guid = parser.get('OLX', 'extractor_guid')
	logging.info('LOADED settings.conf')
	logging.debug ("user_guid = %s\nurlencoded_api_key = %s\nextractor_guid = %s" % (user_guid, urlencoded_api_key, extractor_guid))

	#run API bash
	#rc = subprocess.call("./bashtractor.sh %s %s %s urls.txt data.json", shell = True)

	#parse JSON
	jsonfile = open('data.json.bkp',  'rb')
	jdata = json.load(jsonfile)
	jsonfile.close()

	#clean OLX null objects
	jdata = cleanOLX(jdata)
	
	#debug
	for a in jdata:
		logging.debug(a["all"])
	#print jdata[0]["all"].encode('utf-8')
	#print jdata[1]["all"].encode('utf-8')

	#
	#create aged DB..
	#
	dataux = {}
	if os.path.isfile('dbhash.json'): 
		jdbfile = open ('dbhash.json', 'r+')
		logging.warning('Opened dbhash.json')
	else:
		jdbfile = open ('dbhash.json', 'wb')
		logging.warning('Created dbhash.json')
		jdb = json.dumps(dataux)
	jdbfilesize = os.stat('dbhash.json').st_size
	logging.warning("dbhash.json SIZE = %d", jdbfilesize)

	hash_object = hashlib.md5(jdata[0]["all"].encode('utf-8')+jdata[0]["preco"].encode('utf-8'))
	logging.warning(hash_object.hexdigest())
	dataux[hash_object.hexdigest()] = '0'
	logging.warning(dataux)
	jdb = json.dumps(dataux)
	logging.warning(jdb)
	json.dump(jdb, jdbfile)

	#teste

	logging.warning(jdb)
	logging.warning(jdbfile)
	jdbfile.close()

	logging.info('... ENDED flat-serach.py')

if __name__ == "__main__":
    main()
