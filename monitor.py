import argparse
import validators
import requests
import json
import sys
import notify_android

CONTENT_LENGTH_KEY = 'content-length'

parser = argparse.ArgumentParser(description='Site monitor.')
parser.add_argument("-l", "--list", type=argparse.FileType('r'), help="Path to file containing list of urls to monitor", required=True)
parser.add_argument("-d", "--db_file", help="Path to file where data will be stored in json format", required=True)
parser.add_argument("-c", "--firebase_cert", help="Path to the Firebase certificate", required=True)
args = parser.parse_args()

result = {}

notify_android.init(args.firebase_cert)


try:
    result_file = open(args.db_file, mode='r')
    result = json.load(result_file)
    result_file.close()
except:
    # running for the first time
    print("failed to load file")
    print(sys.exc_info())
    pass

def alert(title, message):
    notify_android.send_message("sitemonitor", title, message)

for x in args.list:
    x = x.strip()
    if validators.url(x):
        r = requests.get(x)
        content_len = len(r.text)
        if x not in result:
            result[x] = {}
            alert("Registered new URL", x)
        else:
            if CONTENT_LENGTH_KEY in result[x]:
                curr_content_len = result[x][CONTENT_LENGTH_KEY]
                if curr_content_len == content_len:
                    continue
                else:
                    alert("URL changed from " + str(curr_content_len) + " to " + str(content_len), x)
            else:
                alert("Registered new URL", x)
        result[x][CONTENT_LENGTH_KEY] = content_len

result_file = open(args.db_file, mode='w')
result_file.write(json.dumps(result))