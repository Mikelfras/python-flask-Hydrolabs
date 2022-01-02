import requests
api_url='http://192.168.1.2:5004'

def test_get():
    assert requests.get(api_url).status_code==200
def test_get_token():
    #tests the sign in functionality
    response = requests.get(api_url+'/api/sign_in', params={'password':'wrangler23','email':'mikelflarson@gmail.com'})
    assert response.status_code==200
def test_get_token_reject():
    response = requests.get(api_url+'/api/sign_in', params={'password':'steve','email':'junk'})
    assert response.status_code==200
