#!/bin/bash
#
# Run an import.io extractor with URLs provided, then output data to a file
# 
# Dependencies:
# 	curl
# 
# Arguments:
# 	- Your import.io user GUID (https://import.io/data/account)
# 	- Your ***URL encoded*** import.io API key (https://import.io/data/account)
# 		- Note you will need to URL encode your API key first - you can do that here: http://meyerweb.com/eric/tools/dencoder/
# 	- Your extractor GUID (https://import.io/data/mine)
# 	- The file to read URL inputs from (one per line)
# 		- Make sure this file has an empty line at the end!
# 	- The file to write data to
# 
# Example usage:
# 	./bashtractor.sh YOUR_USER_GUID YOUR_URLENCODED_API_KEY 00000000-0000-0000-0000-000000000000 urls.txt data.json
# 

USER_GUID=$1
API_KEY=$2
EXTRACTOR_GUID=$3
URL_FILE=$4
DATA_FILE=$5

while read URL
do
	echo -n $URL
	curl -XPOST -H 'Content-Type: application/json' -s -d "{\"input\":{\"webpage/url\":\"$URL\"}}" "https://api.import.io/store/connector/$EXTRACTOR_GUID/_query?_user=$USER_GUID&_apikey=$API_KEY" >> $DATA_FILE
	sleep 1
	echo "" >> $DATA_FILE
	echo " ...done"
done < $URL_FILE
