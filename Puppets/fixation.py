from Puppets.puppet import Puppet
import nltk
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

class FixationPuppet(Puppet):
    def __init__(self, file):
        super().__init__()   
        self.high = True
        file = open(f"res/{file}.txt", "r")
        self.keywords = file.read().split(", ")
        file.close()

    def countKeywords(self, transcript):
        count = 0
        for word in self.keywords:
            count += transcript.count(word)

        totalWords = len(transcript.split()) + 1
        return count / totalWords

    def transcriptFixation(self, transcript):
        transcript = transcript.lower()
        fixation = self.countKeywords(transcript)
        return fixation

    def getFixation(self, videoId):
        transcript = self.yt.getTranscript(videoId)
        fixation = self.transcriptFixation(transcript)
        return round(fixation, 3)

    def decisionFunction(self, recommendations):
        fixations = list(map(lambda x: self.getFixation(x), recommendations))
        return fixations
