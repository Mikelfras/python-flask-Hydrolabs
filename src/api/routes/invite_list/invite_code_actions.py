import requests

databaseURL = 'https://hydrosis-beta.firebaseio.com/inviteCodes'
def get_users(r):
    payload = {'auth':'value'}
    resp = requests.get(databaseURL,params=payload)
    response = resp.url
    return response

def update_invite_codes(db):
    ref = db.reference('userInfo')
    mainDict = ref.get()
    resp_dic = {}
    for key in mainDict:
        resp_dic[key] = key.keys()
    return ref.get()