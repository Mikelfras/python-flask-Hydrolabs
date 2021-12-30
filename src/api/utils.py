from flask import Flask
import os
import tempfile
import cv2
app = Flask(__name__)
# verify the request

def request_verification(r):
    if r is None:
        app.logger.error("The request body is null")
        return "The request body is null", 400
    if 'image' not in r.files:
        app.logger.error("you must include an image file labeled as image in the file")
        return 'you must include an image file labeled as image in the file ', 400
    try:
        payload = r.form.to_dict()
    except Exception as e:
        app.logger.error(e)
        return f"No user data is provided {e}", 400
    if not(payload):
        app.logger.error("No payload data included")
        return "No payload data included",400
    return "success"

# authentication of the api key
def verify_hydrolabs_api_key(key):
    API_KEY='someValue'
    if key == API_KEY:
        return 'authenticated',200
    else:
        return 'API Key invalid',401
# authentication of the token

# upload the image to storage
def store_image(storageBucket,uid,image):
    #storage
    #db_ref
    idText = uid
    temp = tempfile.NamedTemporaryFile(delete=False)
    image.save(temp.name)
    blob = storageBucket.blob('{}.jpeg'.format(idText))
    blob.upload_from_filename(temp.name, content_type='image/jpeg')
    os.remove(temp.name)
    app.logger.info('saved image {}'.format(uid))
    return 'success'
def store_array_image(storageBucket, name, data,uid):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg')
    cv2.imwrite(temp.name,data)
    blob=storageBucket.blob('{}.jpeg'.format(uid+name))
    blob.upload_from_filename(temp.name,content_type='image/jpeg')
    os.remove(temp.name)
    app.logger.info('saved image {}'.format(name))
# log the transaction