import firebase_admin
from firebase_admin import credentials, messaging, firestore

def load_tokens():
    db = firestore.client()
    tokens = []
    reg_tokens = db.collection(u'registration_tokens').stream()
    
    for reg_token in reg_tokens:
        tokens.append(reg_token.to_dict()["token"])
    return tokens
    

def init(cert_path):
    cred = credentials.Certificate(cert_path)
    firebase_admin.initialize_app(cred)


def send_message(topic, title, text):
    tokens = load_tokens()
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
    db = firestore.client()
    if db is not None:
        sites_stream = db.collection(u'sites').stream()
        for site in sites_stream:
            site_elem = site.to_dict()
            site_elem['id'] = site.id
            sites.append(site_elem)
    return sites

def set_new_length(id, url, length):
    db = firestore.client()
    if db is not None:
        data = {
            u'url': url,
            u'content-length': length
        }
        db.collection(u'sites').document(id).set(data)