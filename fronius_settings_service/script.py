import os
import requests
from requests.auth import HTTPDigestAuth
import re
import hashlib
import time

# Configuration
base_url = "http://192.168.1.66"
username = "technician"
password = None
login_endpoint = "/commands/Login"
timeofuse_endpoint = "/config/timeofuse"
referer_url = "http://192.168.1.66/"

def set_password(pw):
    global password
    password = pw

def get_nonce(session, login_url):
    initial_response = session.get(login_url, headers={'Referer': referer_url})
    if initial_response.status_code == 401 and 'X-WWW-Authenticate' in initial_response.headers:
        www_authenticate = initial_response.headers['X-WWW-Authenticate']
        nonce = re.search('nonce="([^"]+)"', www_authenticate).group(1)
        realm = re.search('realm="([^"]+)"', www_authenticate).group(1)
        qop = re.search('qop="([^"]+)"', www_authenticate).group(1)
        return nonce, realm, qop
    else:
        raise Exception("Failed to get nonce")

def create_digest_header(nonce, realm, qop, uri, method, username, password, nc, cnonce):
    ha1 = hashlib.md5(f"{username}:{realm}:{password}".encode()).hexdigest()
    ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
    response = hashlib.md5(f"{ha1}:{nonce}:{nc:08x}:{cnonce}:{qop}:{ha2}".encode()).hexdigest()
    auth_header = (
        f'Digest username="{username}", realm="{realm}", nonce="{nonce}", uri="{uri}", '
        f'response="{response}", qop={qop}, nc={nc:08x}, cnonce="{cnonce}"'
    )
    return auth_header

def set_time_of_use(power=None, remove=False):
    if remove:
        timeofuse_payload = {"timeofuse": []}
    else:
        timeofuse_payload = {
            "timeofuse": [
                {
                    "Active": True,
                    "Power": power,
                    "ScheduleType": "CHARGE_MIN",
                    "TimeTable": {"Start": "09:00", "End": "14:00"},
                    "Weekdays": {"Mon": True, "Tue": True, "Wed": True, "Thu": True, "Fri": True, "Sat": True, "Sun": True}
                }
            ]
        }

    # Step 1: Perform an initial request to get the nonce
    session = requests.Session()
    login_url = f"{base_url}{login_endpoint}?user={username}"
    relative_login_url = f"{login_endpoint}?user={username}"
    try:
        nonce, realm, qop = get_nonce(session, login_url)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    # Step 2: Create the Digest authentication header
    nc = 1
    cnonce = hashlib.md5(str(time.time()).encode()).hexdigest()
    auth_header = create_digest_header(nonce, realm, qop, relative_login_url, 'GET', username, password, nc, cnonce)

    # Step 3: Perform the login request with Digest Authentication
    headers = {
        'Referer': referer_url,
        'Authorization': auth_header
    }
    login_response = session.get(login_url, headers=headers)

    # Check if login was successful
    if login_response.status_code == 200:
        # Step 4: Use the session to set the time of use settings
        timeofuse_url = f"{base_url}{timeofuse_endpoint}"
        relative_timeofuse_url = timeofuse_endpoint
        nc += 1
        auth_header = create_digest_header(nonce, realm, qop, relative_timeofuse_url, 'POST', username, password, nc, cnonce)
        headers = {
            'Referer': referer_url,
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        timeofuse_response = session.post(timeofuse_url, json=timeofuse_payload, headers=headers)

        # Check if setting the time of use was successful
        if timeofuse_response.status_code == 200:
            if remove:
                print("Time of Use settings removed successfully.")
            else:
                print("Time of Use settings updated successfully.")
        else:
            print(f"Failed to update Time of Use settings. Status code: {timeofuse_response.status_code}")
            print(timeofuse_response.text)
    else:
        print(f"Login failed. Status code: {login_response.status_code}")
        print(login_response.text)
