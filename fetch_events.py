import subprocess
import os
import socket
import re
import time
from dotenv import load_dotenv
import json

load_dotenv()
import microsoftgraph.client

# -------------------------------------------------------------------------
# Code modified from https://github.com/zmic/onedrive-python/blob/master/azure_onedrive.py
# -------------------------------------------------------------------------
client_id = os.environ["CLIENT_ID"]  
client_secret = os.environ["CLIENT_SECRET"]  

# -------------------------------------------------------------------------
#
#  this redirect uri should be registered in your application
#
redirect_uri = 'http://localhost:9001'

# -------------------------------------------------------------------------
#
#  Try to open the refresh_token saved to disk in a previous session.
#  If it's still valid, we don't need to login.
#  You only get refresh tokens if your app has permission "offline_access"
#
def try_refresh_token():
    try:
        refresh_token = open('data/refresh_token.txt', 'r').read()
    except FileNotFoundError:
        return None        
    try:
        return client.refresh_token(redirect_uri, refresh_token).data
    except microsoftgraph.exceptions.BaseError as e:
        print(e)
        
# -------------------------------------------------------------------------
#
#  Run a "webserver" to catch the redirect from the login page
#
def mini_webserver():
    HOST = 'localhost'
    PORT = int(redirect_uri.split(':')[-1].replace('/', ''))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024)
            return str(data)
            
# -------------------------------------------------------------------------
#
#  Authenticate
#
client = microsoftgraph.client.Client(client_id, client_secret=client_secret, account_type=os.environ['TENANT_ID'])
token = try_refresh_token()     
    
if token is None:    
    # 
    #  refreshing the token did not work so we need to log in.
    #
    scopes=['Calendars.Read','Calendars.Read.Shared', 'User.Read', 'offline_access']    
    url = client.authorization_url(redirect_uri, scopes, state=None)
    # launch url in a browser (linux only)
    subprocess.call(['xdg-open',url])
    # and catch the redirect
    response = mini_webserver()
    # GET request contains the code
    code = re.search("code=([\S]+)", response).group(1).split("&")[0]
    print("Got code")
    # code has to be exchanged for the actual token
    token = client.exchange_code(redirect_uri, code).data
    print("Got token")

    # save the refresh token to disk so we don't need to login next time 
    if 'refresh_token' in token:
        open('data/refresh_token.txt', 'w').write(token['refresh_token'])
    
client.set_token(token)

# -------------------------------------------------------------------------
#
#  Fetch calendar events
#
start_time = time.time()
events = []
calendars = client.calendar.list_calendars()
for calendar in calendars.data["value"]:
    calendar_events = client.calendar.list_events(calendar["id"])
    events.extend(calendar_events.data['value'])
print(f"{len(events)} events saved in {time.time()-start_time:.0f}s!")

# -------------------------------------------------------------------------
#
#  Save calendar events to json file
#
with open("data/events.json",'w') as f:
    f.write(json.dumps(events))
