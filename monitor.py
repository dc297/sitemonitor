import argparse
import validators
import requests
import json
import sys
import firebase_client

CONTENT_LENGTH_KEY = 'content-length'

parser = argparse.ArgumentParser(description='Site monitor.')
parser.add_argument("-c", "--firebase_cert", help="Path to the Firebase certificate", required=True)
args = parser.parse_args()

firebase_client.init(args.firebase_cert)


def alert(title, message):
    firebase_client.send_message("sitemonitor", title, message)

sites = firebase_client.get_conf_sites()

if sites is None or len(sites) < 1:
    print('No sites configured!')
else:
    for site in sites:
        x = site['id']
        if validators.url(x):
            r = requests.get(x)
            content_len = len(r.text)
            curr_content_len = site[CONTENT_LENGTH_KEY]
            if curr_content_len != content_len:
                alert("URL changed from " + str(curr_content_len) + " to " + str(content_len), x)
                firebase_client.set_new_length(x, content_len)