import requests
from pathlib import Path
base_path = Path(__file__).parent
pass_path = (base_path / "passCase.JPG").resolve()
fail_case = (base_path / "image.JPG").resolve()

#addr = 'https://api.hydrolabs.com'
#addr = 'http://172.18.0.3:5000/'
url = addr + '/api/process'
def test_image():
    passCase = 200
    img = {'image': open(pass_path,'rb')}
    payload= {'bodyweight' : 165, 'duration': 150,'id':100}
    response = requests.post(url, files=img, data=payload)
    print(response.json())
    assert(response.status_code==passCase)
    #assert(response.json=={})
    img['image'].close()
#test response
def test_response():
    assert requests.get(url).status_code == 405
   
def test_image_failed():
    passCase = 500
    img = {'image': open(fail_case,'rb')}
    payload= {'bodyweight' : 10, 'duration': 40, 'id':'test'}
    response = requests.post(url, files=img, data=payload)
    img['image'].close()
    assert response.status_code==passCase
#test response
def test_empty():
    passCase = 400
    response = requests.post(url)
    assert response.status_code==passCase
#test noPayload
def test_no_payload():
    passCase = 400
    img = {'image': open(pass_path,'rb')}
    response = requests.post(url, files=img)
    img['image'].close()
    assert response.status_code==passCase

def test_no_image():
    passCase = 400;
    payload= {'bodyweight' : 10, 'type': '100'}
    response = requests.post(url, data=payload)
    assert response.status_code==passCase

def test_get():
    passCase = 405
    response = requests.get(url)
    assert response.status_code==passCase
          