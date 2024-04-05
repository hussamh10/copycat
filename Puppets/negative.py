from Puppets.puppet import Puppet
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as SIA
import nltk
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


class NegativePuppet(Puppet):
    def analyzeSentiment(self, sentence):
        sid_obj = SIA()
        sentiment_dict = sid_obj.polarity_scores(sentence)
        return sentiment_dict['compound']

    def transcriptSentiment(self, transcript):
        sentences = nltk.sent_tokenize(transcript)
        sentiments = list(map(self.analyzeSentiment, sentences))
        mean = np.mean(sentiments)
        return mean

    def getSentiment(self, videoId):
        transcript = self.yt.getTranscript(videoId)
        sentiment = self.transcriptSentiment(transcript)
        return round(sentiment, 3)

    def decisionFunction(self, recommendations):
        sentiments = list(map(lambda x: self.getSentiment(x), recommendations))
        return sentiments

    def scoreFunction(self, videos):
        minScore = 1
        selected = None
        for videoId, score in videos.items():
            if score < minScore:
                minScore = score
                selected = videoId

        return selected