from abc import abstractmethod
from random import randint
import pandas as pd
import numpy as np
from youtube import API
from IPython.display import clear_output
from tqdm import tqdm
from matplotlib import pyplot as plt
from matplotlib import style
style.use('seaborn-v0_8-whitegrid')

class Puppet:
    def __init__(self, port):
        ws_url = f"ws://localhost:{port}"
        self.yt = API(ws_url)

    def signin(self, username):
        if username == 'blank':
            self.yt.signinBlank()
        else:
            self.yt.signin(username)

    def watch(self, video_id):
        self.yt.addToWatchHistory(video_id)

    @abstractmethod
    def decisionFunction(self, recommendations):
        # returns score for each recommendation
        pass

    def scoreFunction(self, videos):
        sorted_keys = sorted(videos, key=videos.get, reverse=self.high)
        return sorted_keys

    def multiBinge(self, binge_depth, binge_restarts, repeat=True, plot='none'):
        watched = []
        watched_titles = []
        mean_graph = []
        graph = []
        for i in range(binge_restarts):
            home = self.yt.getHomePage()
            scores = self.decisionFunction(home)
            titles = [self.yt.getVideoInfo(x)['title'] for x in home]

            videos = dict()
            for i in range(len(home)):
                videos[home[i]] = scores[i]

            seeds = self.scoreFunction(videos)
            seed = seeds[0]    

            for i in range(binge_depth):
                clear_output(wait=True)
                print(f"Binge: {i}")
                print(f"{i} Watch: {seed}")
                if plot == 'mean':
                    self.drawPlot([mean_graph], binge_depth, binge_restarts)
                if plot == 'selection':
                    self.drawPlot([graph], binge_depth, binge_restarts)
                if plot == 'both':
                    self.drawPlot([mean_graph, graph], binge_depth, binge_restarts)


                for title in watched_titles:
                    print(f"Watched: {title}")

                for i in range(len(seeds)):
                    try:
                        recommendations = self.yt.getRecommendations(seed)
                        break
                    except:
                        print(f"Failed to get recommendations for {seed}")
                        seed = seeds[i]
                        continue    

                self.yt.addToWatchHistory(seed)
                watched.append(seed)
                watched_titles.append(self.yt.getVideoInfo(seed)['title'])

                if not repeat:
                    recommendations = [x for x in recommendations if x not in watched]

                scores = self.decisionFunction(recommendations)
                titles = [self.yt.getVideoInfo(x)['title'] for x in recommendations]
                
                videos = dict()

                for i in range(len(recommendations)):
                    videos[recommendations[i]] = scores[i]

                print(f"Mean score: {np.mean(scores)}")
                
                seeds = self.scoreFunction(videos)
                seed = seeds[0]

                graph.append(videos[seed])
                mean_graph.append(scores)

        results = {'selected': graph, 'mean': mean_graph, 'watched': watched_titles}
        return results

    def drawPlot(self, graphs, depth, restarts):
        x = depth * restarts
        plt.figure(figsize=(20, 10))
        for graph in graphs:
            if len(graph) == 0:
                graph = [0]
            if x is None:
                x = len(graph)

            plt.plot(graph, linewidth=4, color='black')
        plt.xticks(range(0, x, 1), range(0, x, 1), fontsize=8, rotation=90)
        # add vertical lines for restarts
        for i in range(restarts):
            plt.axvline(x=i*depth, color='red', linestyle='--', linewidth=2)
        plt.yticks(fontsize=20)
        plt.xlabel('Videos Watched', fontsize=20)
        plt.ylabel('Utility', fontsize=20)
        plt.title('Utility over time', fontsize=20)
        plt.grid(False)
        plt.show()

    def drawPlotOld(self, graph, x=None):
        if len(graph) == 0:
            graph = [0]
        if x is None:
            x = len(graph)

        plt.figure(figsize=(20, 10))
        plt.plot(graph, linewidth=4, color='black')
        plt.xticks(range(0, x, 1), range(0, x, 1), fontsize=0)
        plt.yticks(fontsize=20)
        plt.xlabel('Videos Watched', fontsize=20)
        plt.ylabel('Utility', fontsize=20)
        plt.title('Utility over time', fontsize=20)
        plt.grid(False)
        plt.show()

    def binge(self, seed, n, plot=False):
        mean_scores = []
        graph = []
        for i in range(n):
            clear_output(wait=True)
            print(f"{i} Watch: {seed}")
            if plot:
                self.drawPlot(graph, n)

            recommendations = self.yt.getRecommendations(seed)
            self.yt.addToWatchHistory(seed)
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
            mean_scores.append(np.mean(scores))

            print("-----------------")
        print(f"Mean scores: {np.mean(mean_scores)}")
        return graph
