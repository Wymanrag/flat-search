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

def dealWithnewapart(newapart):
	for obj in newapart:
		print("%s; %s; %s; %s" % (obj["local"], obj["preco"], obj["link/_text"], obj["link"]))

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
    TEXT = body

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
        print 'successfully sent the mail'
    except:
        print "failed to send mail"

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
	url = "https://olx.pt/imoveis/apartamento-casa-a-venda/apartamentos-arrenda/alvercadoribatejo/?search%5Bdescription%5D=1"
	#run API bash
	#rc = subprocess.call("./bashtractor.sh %s %s %s urls.txt data.json", shell = True)
	rc = queryAPI(user_guid, urlencoded_api_key, extractor_guid, url)

	#parse JSON
	#jsonfile = open('data.json.bkp',  'rb')
	#jdata = json.load(jsonfile)
	#jsonfile.close()
	jdata = rc.json()
	#clean OLX null objects
	if "results" in jdata:
		jdata = cleanOLX(jdata)
	else: logging("UPS...no results in json")
	#debug
	for a in jdata:
		logging.debug(a["all"])
	#print jdata[0]["all"].encode('utf-8')
	#print jdata[1]["all"].encode('utf-8')

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

	dealWithnewapart(newstuff)

	logging.info('... ENDED flat-serach.py')

if __name__ == "__main__":
    main()
