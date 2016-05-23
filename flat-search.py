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
		logging.debug(newaux)
		newlist.append(newaux)
	return newlist


def queryAPI(userguid, apikey, extractor, url):
	#return json with apartments
	headers = {'Content-Type': 'application/json',}
	data = '{"input":{"webpage/url":"%s"}}' %(url)
	logging.debug("data is "+data)
	posturl = ("https://api.import.io/store/connector/%s/_query?_user=%s&_apikey=%s" % (extractor, userguid, apikey))
	
	results = {}
	counter1 = 0
	while "results" not in results:
		counter1 += 1
		rc = requests.post(posturl, headers=headers, data=data)
		logging.info("request status_code: %d" % (rc.status_code))
		results = rc.json()
		if counter1 is 5:
			logging.info("UPS...Could retrieve data from %s" % (rc.url) )
			break
	return results

def send_email(user, pwd, recipient, subject, body):
    import smtplib

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    print type(TO)
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
        logging.debug("FROM: %s - type %s; TO: %s; gmail_user: %s - type %s" % (FROM, type(FROM), TO, gmail_user, type(gmail_user)))

    except:
        logging.info("failed to send mail")
        logging.debug("FROM: %s - type %s; TO: %s; gmail_user: %s - type %s" % (FROM, type(FROM), TO, gmail_user, type(gmail_user)))


def db_init():
	dictaux = {}
	if os.path.isfile(os.path.dirname(os.path.abspath(__file__))+'/dbhash.json'): 
		jdbfile = open (os.path.dirname(os.path.abspath(__file__))+'/dbhash.json', 'r')
		jdbfilesize = os.stat('dbhash.json').st_size
		logging.debug("dbhash.json SIZE = %d", jdbfilesize)
		if jdbfilesize != 0:
			jdbinit = json.load(jdbfile)
			jdbfile.close()
			logging.debug(jdbinit)
		else:
			jdbinit = dictaux
	else:
		jdbinit = dictaux
	logging.info("db has %d entries!", len(jdbinit))
	return jdbinit

def db_update(dbref):
	jdbfile = open (os.path.dirname(os.path.abspath(__file__))+'/dbhash.json', 'wb')
	json.dump(dbref, jdbfile)
	logging.info("dumped jdb to file")
	logging.debug(jdbfile)
	jdbfile.close()


def db_clean_old():
	pass

def search4apart(configs):
	user_guid = configs.get('IMPORT_IO', 'your_user_guid')
	urlencoded_api_key = configs.get('IMPORT_IO', 'your_urlencoded_api_key')
	#extractor_guid = configs.get('OLX', 'extractor_guid')
	#logging.debug ("user_guid = %s\nurlencoded_api_key = %s\nextractor_guid = %s" % (user_guid, urlencoded_api_key, extractor_guid))
	sites_supported = ["OLX", "IMOVIRTUAL", "BPI", "TESTE"]

	#initiate database
	jdb = db_init()

	#CORE engine
	jdata = {}
	newstuff = []
	for site in sites_supported:
		logging.info("Now looking at site %s" % (site))
		urllist = json.loads(configs.get(site, 'url'))
		logging.info("URLs: %s " % (urllist))
		if urllist: 
			for url in urllist:
				logging.info("Now will get data from url: %s" % (url))
				extractor_guid = configs.get('API_EXTRACTORS', site)
				logging.debug("extractor_guid = %s " % extractor_guid)
				rc = queryAPI(user_guid, urlencoded_api_key, extractor_guid, url)
				jdata = rc

				if "results" in jdata and site is "OLX":
					jdata = cleanOLX(jdata)
				else:
					logging.info("UPS...no results in json")
					logging.debug(jdata)

				for obj in jdata:
				#hash_object = hashlib.md5(jdata[0]["all"].encode('utf-8')+jdata[0]["preco"].encode('utf-8'))
					hash_object = hashlib.md5(obj["all"].encode('utf-8')+obj["preco"].encode('utf-8'))
					#logging.warning(hash_object.hexdigest())
					dictaux = {hash_object.hexdigest():"date"}
					if hash_object.hexdigest() not in jdb:
						jdb.update(dictaux)
						logging.debug(hash_object.hexdigest())
						newstuff.append(obj)
	db_update(jdb)
	#exit("Exiting for debug")


	#clean OLX null objects
	# if "results" in jdata:
	# 	jdata = cleanOLX(jdata)
	# else:
	# 	logging.info("UPS...no results in json")
	# 	logging.warning(jdata)

	return newstuff

def main():
	logging.basicConfig(level=logging.INFO)
	
	logging.info('STARTED flat-serach.py...')
	

	#READ settings.conf
	parser = ConfigParser.ConfigParser ()
	parser.read(os.path.dirname(os.path.abspath(__file__))+'/settings.conf')
	logging.info('LOADED settings.conf')
	#settings read

	#call search_OLX to sera
	newstuff = search4apart(parser)

	#
	#create aged DB..
	#
	# dictaux = {}
	# newstuff = []
	#check if db exists, else initiate it
	# if os.path.isfile('dbhash.json'): 
	# 	jdbfile = open ('dbhash.json', 'r')
	# 	jdbfilesize = os.stat('dbhash.json').st_size
	# 	logging.debug("dbhash.json SIZE = %d", jdbfilesize)
	# 	jdb = json.load(jdbfile)
	# 	jdbfile.close()
	# 	logging.debug(jdb)
	# else:
	# 	jdb = dictaux

	# for obj in jdata:
	# 	#hash_object = hashlib.md5(jdata[0]["all"].encode('utf-8')+jdata[0]["preco"].encode('utf-8'))
	# 	hash_object = hashlib.md5(obj["all"].encode('utf-8')+obj["preco"].encode('utf-8'))
	# 	#logging.warning(hash_object.hexdigest())
	# 	dictaux = {hash_object.hexdigest():"date"}
	# 	if hash_object.hexdigest() not in jdb:
	# 		jdb.update(dictaux)
	# 		logging.debug(hash_object.hexdigest())
	# 		newstuff.append(obj)


	logging.info("newstuff has %d entries!", len(newstuff))

	# jdbfile = open ('dbhash.json', 'wb')
	# json.dump(jdb, jdbfile)
	# logging.info("dumped jdb to file")
	# logging.debug(jdbfile)
	# jdbfile.close()

	newaparts = create_newapart_list(newstuff)
	body = "\n".join(newaparts)

	#teste mail
	#user, pwd, recipient, subject, body
	usr = parser.get('EMAIL', 'usr').encode('ascii')
	pw = parser.get('EMAIL', 'pw')
	recip = json.loads(parser.get('EMAIL', 'recip'))
	subj = parser.get('EMAIL','subj')
	tosendmail = parser.get('EMAIL', 'sendmail') 

	if tosendmail is "true": send_email(usr,pw,recip,subj,body)

	logging.info('... ENDED flat-serach.py')

if __name__ == "__main__":
    main()

'''
notas:

'''