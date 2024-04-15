import websockets
import json
import sys
sys.path.append('../')
from youtube import API

class Voyager:
    def __init__(self, port, client_id):
        ws_url = f"ws://localhost:{port}"
        self.yt = API(ws_url)
        self.client_id = client_id
        self.groundcontrol_port = 6789

    def signin(self):
        username = self.client_id
        print("username: ", username)
        if username == 'blank':
            print("Signing in...: blank")
            self.yt.signinBlank()
        else:
            self.yt.signin(username)

    def getHomePage(self):
        return self.yt.getHomePage()

    def getRecommendations(self, video_id):
        return self.yt.getRecommendations(video_id)
    
    def getVideo(self):
        uri = f"ws://localhost:{self.groundcontrol_port}"
        with websockets.connect(uri) as websocket:
            websocket.send(json.dumps({'client_id': self.client_id, 'action': 'request_id'}))
            response = websocket.recv()
            if response == -1:
                return -1
            print(f"Received: {response}")
            return 1
    
    def uploadSeeds(self, videos):
        for video in videos:
            uri = f"ws://localhost:{self.groundcontrol_port}"
            with websockets.connect(uri) as websocket:
                websocket.send(json.dumps({'client_id': self.client_id, 'action': 'add_id', 'video_id': video}))
                response = websocket.recv()
                print(f"Received: {response}")
    

    def binge(self):
        self.signin()
        home = self.getHomePage()
        self.uploadSeeds(home)
        while True:
            response = self.getVideo()
            if response == -1:
                break
            recommendations = self.getRecommendations(response)
            self.uploadSeeds(recommendations)
            print(recommendations)
            print("Bingeing...")
