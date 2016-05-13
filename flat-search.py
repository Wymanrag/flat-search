#! /usr/bin/python
'''
flat-serach.py v1

Search for houses on some sites
'''

#START
import ConfigParser, subprocess, json, hashlib, logging, os, requests


def cleanOLX(j2clean):
 	nr=0
 	j2clean_aux = []
 	for a in j2clean["results"]:
 		if "all" in a:
 			j2clean_aux.append(a)
 	return j2clean_aux

def create_newapart_list(newapart):
	newlist = []
	for obj in newapart:
		newaux = ("%s; %s; %s; %s" % (obj["local"], obj["preco"], obj["link/_text"], obj["link"]))
		logging.warning(newaux)
		newlist.append(newaux)
	return newlist


def queryAPI(userguid, apikey, extractor, url):
	headers = {'Content-Type': 'application/json',}
	data = '{"input":{"webpage/url":"%s"}}' %(url)
	logging.debug("data is "+data)
	posturl = ("https://api.import.io/store/connector/%s/_query?_user=%s&_apikey=%s" % (extractor, userguid, apikey))
	rc = requests.post(posturl, headers=headers, data=data)
	logging.info("request status_code: %d" % (rc.status_code))
	logging.debug(rc.url)
	return rc

def send_email(user, pwd, recipient, subject, body):
    import smtplib

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body.encode('utf8')

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        logging.info("successfully sent the mail") 
    except:
        logging.info("failed to send mail")

def search_OLX(configs):
	user_guid = configs.get('IMPORT_IO', 'your_user_guid')
	urlencoded_api_key = configs.get('IMPORT_IO', 'your_urlencoded_api_key')
	extractor_guid = configs.get('OLX', 'extractor_guid')
	logging.debug ("user_guid = %s\nurlencoded_api_key = %s\nextractor_guid = %s" % (user_guid, urlencoded_api_key, extractor_guid))
	sites2search = ["OLX"]
	url = {}
	for site in sites2search:
		url.update({'OLX':json.loads(configs.get('OLX', 'url'))})
		#url = url[0]
		logging.warning(url)
		exit("Exiting for debug")

	jdata = {}
	#if not url:
	#	for eachurl in url:
		#call import IO API
	counter1 = 1
	while "results" not in jdata:
		logging.info("...Quering import.io for OLX...")
		rc = queryAPI(user_guid, urlencoded_api_key, extractor_guid, url)
		jdata = rc.json()
		counter1 += 1
		#stop if tried 5 times
		if counter1 is 5:
			logging.info("UPS...Could retrieve data from %s" % (rc.url) )
			break
	#else:
	#	break

	#clean OLX null objects
	if "results" in jdata:
		jdata = cleanOLX(jdata)
	else:
		logging.info("UPS...no results in json")
		logging.warning(jdata)

	return jdata


def main():
	logging.basicConfig(level=logging.INFO)
	
	logging.info('STARTED flat-serach.py...')
	
	#READ settings.conf
	parser = ConfigParser.ConfigParser ()
	parser.read('settings.conf')
	logging.info('LOADED settings.conf')
	#settings read


	#call search_OLX to sera
	jdata = search_OLX(parser)

	#
	#create aged DB..
	#
	dictaux = {}
	newstuff = []
	#check if db exists, else initiate it
	if os.path.isfile('dbhash.json'): 
		jdbfile = open ('dbhash.json', 'r')
		jdbfilesize = os.stat('dbhash.json').st_size
		logging.debug("dbhash.json SIZE = %d", jdbfilesize)
		jdb = json.load(jdbfile)
		jdbfile.close()
		logging.debug(jdb)
	else:
		jdb = dictaux

	for obj in jdata:
		#hash_object = hashlib.md5(jdata[0]["all"].encode('utf-8')+jdata[0]["preco"].encode('utf-8'))
		hash_object = hashlib.md5(obj["all"].encode('utf-8')+obj["preco"].encode('utf-8'))
		#logging.warning(hash_object.hexdigest())
		dictaux = {hash_object.hexdigest():"date"}
		if hash_object.hexdigest() not in jdb:
			jdb.update(dictaux)
			logging.debug(hash_object.hexdigest())
			newstuff.append(obj)

	logging.info("db has %d entries!", len(jdb))
	logging.info("newstuff has %d entries!", len(newstuff))

	jdbfile = open ('dbhash.json', 'wb')
	json.dump(jdb, jdbfile)
	logging.info("dumped jdb to file")
	logging.debug(jdbfile)
	jdbfile.close()

	newaparts = create_newapart_list(newstuff)
	body = "\n".join(newaparts)

	#teste mail
	#user, pwd, recipient, subject, body
	usr = parser.get('EMAIL', 'usr')
	pw = parser.get('EMAIL', 'pw')
	recip = json.loads(parser.get('OLX', 'url'))
	#print type(recip)
	subj = parser.get('EMAIL','subj') 
	#body="body"#
	send_email(usr,pw,recip,subj,body)

	logging.info('... ENDED flat-serach.py')

if __name__ == "__main__":
    main()

'''
notas:
importar uma lista de [APIKEYS] com por ex: OLX, extractor
e iterar num array de urls
'''