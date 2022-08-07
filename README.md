# Hydrolabs Simple API
Howdy!

Alright, the first time I did this, I didnt do a good job documenting. This time around I 
hope I've done a _little_ better. If you need help, email me: mikel.f.larson@gmail.com
I will help you :) 

To run on your local machine:
You'll need to install docker https://www.docker.com 
Once you have docker running, and you've opened the project run: `docker compose up`

This will start the container, which you can likely access the logs in your console, or through docker.

To test, cd into `src/tests/process`, and run: `pytest`
to run, you may need to change the address to `addr = "http://127.0.0.1:5004"`
all images should pass as is - if they fail for any reason something has gone wrong, and the debugging associated with the test functions may be useful.

To test other images, debug, or otherwise use the api locally, the process_test.py shows several examples on how to run different commands.

A Flask based API starts in src/api/app.py - as requests come in, they are passed down routes. Only one route is complete in this API, the image process route. This uses the image processing library, which can be found in the src/api/routes/process directory.

Deploy steps:
when building to deploy use this if on an M1 mac: --platform linux/amd64
full command:
 `docker build --platform linux/amd64 . --tag gcr.io/hydrosis-beta/hydrolabs_api
 docker push gcr.io/hydrosis-beta/hydrolabs_api` 

Guide: https://cloud.google.com/run/docs/building/containers?authuser=1

SOO much more to do on this:
1. API key verification - anyone can post to this now. Not a problem when we are small
    enough to be anonymous since anyone could use our api 
2. porting over more functionality from firebase, I think we should have a single interface
  2a. invite codes, and invite code searching
  2b. new user creation
  2c. read/write user data
  2d. etc.
3. more error codes that help inform the user, or other api stake holders of problems

