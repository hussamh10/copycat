import asyncio
import websockets
import json

class GroundControl:
    def __init__(self):
        self.limit = 100
        self.cycle_limit = 10
        self.video_ids = []
        self.index = 0
        self.cycles = 0
        self.clients = {}

    def get_client_data(self, client_id):
        if client_id not in self.clients:
            self.clients[client_id] = {'index': 0, 'cycles': 0}
        return self.clients[client_id]

    def addVideo(self, data):
        if len(self.video_ids) >= self.limit:
            return 'Limit reached'

        video_id = data['video_id']
        if video_id not in self.video_ids:
            self.video_ids.append(video_id)
            print(self.video_ids)
            return 'Added'

    def getVideo(self, client_data):
        print(client_data)
        if client_data['cycles'] >= self.cycle_limit:
            return -1

        if client_data['index'] >= len(self.video_ids):
            client_data['index'] = 0
            client_data['cycles'] += 1
        
        if client_data['index'] >= len(self.video_ids):
            client_data['index'] = 0
            return 0

        response = self.video_ids[client_data['index']]
        client_data['index'] += 1
        return response

    async def handler(self, websocket, path):
        client_id = None
        try:
            async for message in websocket:
                data = json.loads(message)
                if 'client_id' in data:
                    client_id = data['client_id']
                else:
                    await websocket.send(json.dumps({'error': 'Client ID is required'}))
                    continue
                
                client_data = self.get_client_data(client_id)
                if data['action'] == 'request_id':
                    await websocket.send(json.dumps({'video_id': self.getVideo(client_data)}))
                if data['action'] == 'add_id':
                    await websocket.send(json.dumps({'status': self.addVideo(data)}))
        finally:
            if client_id and client_id in self.clients:
                del self.clients[client_id] 


async def main():
    gc = GroundControl()
    start_server = websockets.serve(gc.handler, "localhost", 6789)
    await start_server
    await asyncio.Future()  # run forever

asyncio.run(main())