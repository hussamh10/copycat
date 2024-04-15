from Puppets.puppet import Puppet
import nltk
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

class RandomPuppet(Puppet):
    def __init__(self):
        super().__init__()   
        self.letters = ['g', 'k']
        self.high = True

    def countKeywords(self, transcript):
        count = 0
        for word in self.letters:
            count += transcript.count(word)

        total_letters = len(transcript) + 1
        return count / total_letters

    def transcriptScore(self, transcript):
        transcript = transcript.lower()
        score = self.countKeywords(transcript)
        return score

    def getScore(self, videoId):
        transcript = self.yt.getTranscript(videoId)
        score = self.transcriptScore(transcript)
        return round(score, 3)

    def decisionFunction(self, recommendations):
        scores = list(map(lambda x: self.getScore(x), recommendations))
        return scores