import requests
import os
import eventlet
import socketio
from bs4 import BeautifulSoup
from collections import deque
import subprocess
import json

# Get my wikipedia api credentials
cid = os.getenv('CLIENT_ID')
secret = os.getenv('CLIENT_SECRET')

# Use them to run a command which gives me an access token
result = subprocess.run([
    "curl", "-X", "POST",
    "-d", "grant_type=client_credentials",
    "-d", f"client_id={cid}",
    "-d", f"client_secret={secret}",
    "https://meta.wikimedia.org/w/rest.php/oauth2/access_token"
], capture_output=True, text=True)

result = json.loads(result.stdout)

token = result["access_token"]

# Initialize a socket.io server and a wsgi server to host it
sio = socketio.Server(cors_allowed_origins=["http://localhost:5173"])
app = socketio.WSGIApp(sio)

def get_links(article):
    """
    Take in the title of an article, fetch it from wikipedia, and use bs4 to find linked articles
    """

    # Fetch article
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Johnathan Application (cmmasonek@gmail.com)'
    }

    base_url = 'https://api.wikimedia.org/core/v1/wikipedia/'
    endpoint = f'/page/{article}/html'

    url = base_url + "en" + endpoint

    response = requests.get(url, headers=headers)

    content = response.content

    # Parse html to find links
    links = BeautifulSoup(content,"html.parser").find_all("a",{"rel":"mw:WikiLink"})

    links = [link.get('href')[2:] for link in links]

    return (set(links))

def BFS(node,target,sid,sleeptime):
    """
    Run breadth first search from a start node and stop when a path to target is found,
    or all possible nodes are found
    """

    queue = deque([[node]])
    E = {node}

    while queue:
        path = queue.popleft()

        node = path[-1]

        sio.emit("searching",{"path":path},sid) # Send current path over socket.io

        print(path)

        adjs = get_links(node) # Get links from the artcle

        if adjs == set():
            continue

        if target in adjs:
            return path + [target] # Generate path

        for adj in adjs:
            sio.emit("searching",{"path":path + [adj]},sid) # send path for each "adjacent" article
            eventlet.sleep(sleeptime) # 
            if adj in E:
                continue
            queue.append(path + [adj])
            E.add(adj)


@sio.event
def start(sid,data):
    """
    Handle the "start" message when sent from client
    """
    start = data["from"]
    end = data["to"]
    sleep = data["sleeptime"] # for fast/slow modes

    path = BFS(start,end,sid,sleep)

    sio.emit("searching",{"path":path}) # when a path is found, send it over

if __name__ == '__main__':
    # Run the server
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)