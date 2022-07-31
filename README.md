# Hydrolabs Simple API
Howdy!

Alright, the first time I did this, I didnt do a good job documenting. This time around I 
hope I've done a _little_ better. If you need help, email me: mikel.f.larson@gmail.com
I will help you :) 

Deploy steps:
when building to deploy use this if on an M1 mac: --platform linux/amd64
full command:
 docker build --platform linux/amd64 . --tag gcr.io/hydrosis-beta/hydrolabs_api
 docker push gcr.io/hydrosis-beta/hydrolabs_api 

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

