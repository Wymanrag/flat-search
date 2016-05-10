#! /usr/bin/python
#flat-serach.py v1
#
#Search for houses on some sites
#START
import ConfigParser
import subprocess
import json

print "STARTED...\n"

def cleanOLX(j2clean):
	for a in j2clean["results"]:
		if "all" in a:
			print a["all"].encode('utf-8')
		else:
			del a
#		if a["link"] is 'null':
#			j2clean.pop["results"][a]

#READ .conf
# with open('importioapi.conf') as f:
# 	lines = f.readlines()
#lines = [line.rstrip('\n') for line in open('importioapi.conf')]
parser = ConfigParser.ConfigParser ()
parser.read('settings.conf')

user_guid = parser.get('OLX', 'USER_GUID')
urlencoded_api_key = parser.get('OLX', 'urlencoded_api_key')
extractor_guid = parser.get('OLX', 'extractor_guid')
#print ("user_guid = %s\nurlencoded_api_key = %s\nextractor_guid = %s" % (user_guid, urlencoded_api_key, extractor_guid))

#run API bash
#rc = subprocess.call("./bashtractor.sh %s %s %s urls.txt data.json", shell = True)

#parse JSON
jsonfile = open('data.json.bkp',  'rb')
jdata = json.load(jsonfile)
jsonfile.close()

#clean OLX null objects
cleanOLX(jdata)
# print jdata["outputProperties"][0]["name"]

# for i in jdata["outputProperties"]:
# 	print i["name"]
	
#create aged DB..

print "\n...DONE"

