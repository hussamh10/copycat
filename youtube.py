import websocket
import json

class API:
    def __init__(self, ws_url):
        self.ws_url = ws_url

    def signinBlank(self):
        print("Signing in...")
        signin_response = self._call_function_and_wait("signinBlank")
        if signin_response.get('status') == 'success':
            print("Signed in successfully. Proceeding with next operations.")

    def signin(self, username):
        print("Signing in...")
        signin_response = self._call_function_and_wait("signin", [username])
        if signin_response.get('status') == 'success':
            print("Signed in successfully. Proceeding with next operations.")

    def getHomePage(self):
        homepage = self._call_function("getHomePage")
        page = homepage['result']

        videos = []
        for post in page:
            if post['type'] == 'Video':
                videos.append(post['id'])
        return videos

    def getTranscript(self, video_id): 
        try:
            transcript = self._call_function("getTranscript", [video_id])
            transcript = transcript['result']
            transcript = ' '.join(transcript)
        except:
            transcript = "good good"
        return transcript
    
    def addToWatchHistory(self, video_id):
        self._call_function("addToWatchHistory", [video_id])

    def getRecommendations(self, video_id):
        recommendations = self._call_function("getUpNextRecommendations", [video_id])
        return recommendations['result']

    def getVideoInfo(self, video_id):
        info = self._call_function("getInfo", [video_id])
        info = info['result']

        safe_info = {
        'title': info.get('basic_info', {}).get('title', 'Unknown Title'),
        'duration': info.get('basic_info', {}).get('duration', 'Unknown Duration'),
        'like_count': info.get('basic_info', {}).get('like_count', 'Unknown Likes'),
        'view_count': info.get('basic_info', {}).get('view_count', 'Unknown Views'),
        'channel': info.get('basic_info', {}).get('author', 'Unknown Author'),
        'channel_id': info.get('basic_info', {}).get('channel', {}).get('id', 'Unknown Channel ID'),
        'channel_url': info.get('basic_info', {}).get('channel', {}).get('url', 'Unknown Channel URL'),
        'short_description': info.get('basic_info', {}).get('short_description', 'No Description Available'),
        'thumbnail_url': info.get('basic_info', {}).get('thumbnail', [{}])[0].get('url', 'No Thumbnail URL'),
        'id': info.get('basic_info', {}).get('id', 'Unknown ID'),
        'category': info.get('basic_info', {}).get('category', 'Unknown Category'),
        'comment_count': info.get('comments_entry_point_header', {}).get('comment_count', {}).get('text', 'Unknown Comment Count'),
        }
        return safe_info

    def _call_function(self, function_name, args=[]):
        # Establish a WebSocket connection
        ws = websocket.create_connection(self.ws_url)
        
        # Construct the message with the function name and arguments
        message = json.dumps({"functionName": function_name, "args": args})
        ws.send(message)

        # Wait for the response
        response = ws.recv()
        ws.close()
        # Return the parsed JSON response
        return json.loads(response)


    def _call_function_and_wait(self, function_name, args=[]):
        ws = websocket.create_connection(self.ws_url)
        
        message = json.dumps({"functionName": function_name, "args": args})
        ws.send(message)
        print(f"Sent request to call '{function_name}' with arguments {args}")

        # Wait for the response
        while True:
            response = ws.recv()
            response_data = json.loads(response)
            print(f"Response from server: {response_data}")
            if response_data.get('status') == 'success':
                break  # Sign-in was successful, break the loop
            elif response_data.get('status') == 'error':
                print("Error during the operation. Exiting...")
                break

        ws.close()
        return response_data