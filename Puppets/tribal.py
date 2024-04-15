from Puppets.puppet import Puppet
import nltk
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


class TribalPuppet(Puppet):
    def __init__(self):
        super().__init__()   
        they = open(f"res/they.txt", "r")
        us = open(f"res/us.txt", "r")
        self.they = they.read().split(", ")
        self.us = us.read().split(", ")
        they.close()
        us.close()
        self.high = True

    def countKeywords(self, transcript):
        us_count = 0
        they_count = 0
        for word in self.they:
            they_count += transcript.count(word)

        for word in self.us:
            us_count += transcript.count(word)
        totalWords = len(transcript.split()) + 1
        they_ratio = they_count / totalWords
        return round(they_ratio, 3)

    def transcriptIdentity(self, transcript):
        transcript = transcript.lower()
        identity = self.countKeywords(transcript)
        return identity

    def getIdentity(self, videoId):
        try:
            transcript = self.yt.getTranscript(videoId)
            identity = self.transcriptIdentity(transcript)
        except Exception as e:
            identity = 0
        return round(identity, 3)

    def decisionFunction(self, recommendations):
        identity = list(map(lambda x: self.getIdentity(x), recommendations))
        return identity