import requests
from pathlib import Path
base_path = Path(__file__).parent
fail_case = (base_path / "image.JPG").resolve()

#addr = 'https://api.hydrolabs.com'
addr = 'http://192.168.1.2:5004'
url = addr + '/api/process'
def test_image_1_pass():
    passCase = 200
    image_path = (base_path / "image_1_pass.jpeg").resolve()
    img = {'image': open(image_path,'rb')}
    payload= {'bodyweight' : 165, 'duration': 150,'id':100}
    response = requests.post(url, files=img, data=payload)
    assert response.status_code == passCase 
    print(response.text)
    #assert(response.json=={})
    img['image'].close()
#test response
def test_image_2_pass():
    passCase = 200
    image_path = (base_path / "image_2_pass.jpeg").resolve()
    img = {'image': open(image_path,'rb')}
    payload= {'bodyweight' : 165, 'duration': 120,'id':200}
    response = requests.post(url, files=img, data=payload)
    assert response.status_code == passCase 
    print(response.text)
    #assert(response.json=={})
    img['image'].close()
#test response
def test_image_3_pass():
    passCase = 200
    image_path = (base_path / "image_3_pass.jpeg").resolve()
    img = {'image': open(image_path,'rb')}
    payload= {'bodyweight' : 165, 'duration': 120,'id':300}
    response = requests.post(url, files=img, data=payload)
    assert response.status_code == passCase 
    print(response.text)
    #assert(response.json=={})
    img['image'].close()
#test response
def test_image_4_fail():
    passCase = 500
    image_path = (base_path / "image_4_fail.jpeg").resolve()
    img = {'image': open(image_path,'rb')}
    payload= {'bodyweight' : 165, 'duration': 120,'id':400}
    response = requests.post(url, files=img, data=payload)
    assert response.status_code == passCase 
    print(response.text)
    #assert(response.json=={})
    img['image'].close()
#test response
def test_image_5_fail():
    passCase = 500
    image_path = (base_path / "image_5_fail.jpeg").resolve()
    img = {'image': open(image_path,'rb')}
    payload= {'bodyweight' : 165, 'duration': 120,'id':500}
    response = requests.post(url, files=img, data=payload)
    assert response.status_code == passCase 
    print(response.text)
    #assert(response.json=={})
    img['image'].close()
#test response
def test_image_6_pass():
    passCase = 200
    image_path = (base_path / "image_6_pass.jpeg").resolve()
    img = {'image': open(image_path,'rb')}
    payload= {'bodyweight' : 165, 'duration': 150,'id':600}
    response = requests.post(url, files=img, data=payload)
    assert response.status_code == passCase 
    print(response.text)
    #assert(response.json=={})
    img['image'].close()
#test response
def test_response():
    assert requests.get(url).status_code == 405
   
def test_empty():
    passCase = 400
    response = requests.post(url)
    assert response.status_code==passCase
#test noPayload
def test_no_payload():
    passCase = 400
    image_path = (base_path / "image_6_pass.jpeg").resolve()
    img = {'image': open(image_path,'rb')}
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
          