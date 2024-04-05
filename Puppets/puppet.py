from abc import abstractmethod
from time import sleep
import pandas as pd
import numpy as np
from youtube import API

class Puppet:
    def __init__(self):
        ws_url = "ws://localhost:8080"
        self.yt = API(ws_url)

    def signin(self, username):
        # todo
        self.yt.signin()

    def watch(self, video_id):
        self.yt.addToWatchHistory(video_id)

    @abstractmethod
    def decisionFunction(self, recommendations):
        # returns score for each recommendation
        pass

    @abstractmethod
    def scoreFunction(self, videos):
        # given a dict of videos and scores returns the selected video
        pass

    def multiBinge(self, binge_depth, binge_count):
        graph = []
        for i in range(binge_count):
            print(f"Binge: {i}")
            home = self.yt.getHomePage()
            scores = self.decisionFunction(home)
            titles = [self.yt.getVideoInfo(x)['title'] for x in home]

            videos = dict()
            for i in range(len(home)):
                videos[home[i]] = scores[i]

            df = pd.DataFrame(list(videos.items()), columns=['video_id', 'score'])
            df['title'] = titles
            df.columns = ['HOME VIDEOS', 'score', 'title']
            print(df)

            seed = self.scoreFunction(videos)

            print('BINGE TIME')

            for i in range(binge_depth):
                print(f"{i} Watch: {seed}")
                self.yt.addToWatchHistory(seed)
                sleep(3)
                recommendations = self.yt.getRecommendations(seed)
                scores = self.decisionFunction(recommendations)
                titles = [self.yt.getVideoInfo(x)['title'] for x in recommendations]
                
                videos = dict()
                for i in range(len(recommendations)):
                    videos[recommendations[i]] = scores[i]

                print(f"Mean score: {np.mean(scores)}")
                
                df = pd.DataFrame(list(videos.items()), columns=['video_id', 'score'])
                df['title'] = titles
                df.columns = ['UPNEXT VIDEOS', 'score', 'title']
                print(df)

                seed = self.scoreFunction(videos)
                graph.append(videos[seed])

                print("-----------------")

        return graph

    def binge(self, seed, n):
        graph = []
        for i in range(n):
            print(f"{i} Watch: {seed}")
            self.yt.addToWatchHistory(seed)
            sleep(3)
            recommendations = self.yt.getRecommendations(seed)
            scores = self.decisionFunction(recommendations)
            titles = [self.yt.getVideoInfo(x)['title'] for x in recommendations]
            
            videos = dict()
            for i in range(len(recommendations)):
                videos[recommendations[i]] = scores[i]

            print(f"Mean score: {np.mean(scores)}")
            
            df = pd.DataFrame(list(videos.items()), columns=['video_id', 'score'])
            df['title'] = titles
            print(df)

            seed = self.scoreFunction(videos)
            graph.append(videos[seed])

            print("-----------------")
        return graph
