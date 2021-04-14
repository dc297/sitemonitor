import firebase_admin
from firebase_admin import credentials, messaging, firestore

tokens = []
db = None

def load_tokens():
    db = firestore.client()
    reg_tokens = db.collection(u'registration_tokens').stream()
    
    for reg_token in reg_tokens:
        tokens.append(reg_token.to_dict()["token"])
    

def init(cert_path):
    cred = credentials.Certificate(cert_path)
    firebase_admin.initialize_app(cred)
    load_tokens()


def send_message(topic, title, text):
    if len(tokens) == 0:
        print('No device registered!')
        return
    # See documentation on defining a message payload.
    message = messaging.MulticastMessage(
        tokens=tokens,
        data={
            'title': title,
            'text': text,
            'topic': topic
        }
    )

    # Send a message to the devices subscribed to the provided topic.
    response = messaging.send_multicast(message)
    # Response is a message ID string.
    print('{0} messages were sent successfully'.format(response.success_count))

def get_conf_sites():
    sites = []
    if db is not None:
        sites_stream = db.collection(u'sites').stream()
        for site in sites_stream:
            sites.append(site.to_dict())
    return sites

def set_new_length(url, length):
    if db is not None:
        data = {
            u'content-length': length
        }
        db.collection(u'sites').document(url).set(data)