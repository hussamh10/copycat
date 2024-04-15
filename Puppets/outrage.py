from Puppets.puppet import Puppet
import nltk
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

import os
import numpy as np
from outrageclf.preprocessing import WordEmbed, get_lemmatize_hashtag
from outrageclf.classifier import _load_crockett_model

os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK']='True'

class OutrageClassifier:
    def __init__(self):
        MODEL_PATH = '/Users/hussam/Desktop/Projects/outrage_classifier/'
        embedding_url = os.path.join(MODEL_PATH, "26k_training_data.joblib")
        model_url = os.path.join(MODEL_PATH, "GRU.h5")
        self.model = _load_crockett_model(model_url)
        self.word_embed = WordEmbed()
        self.word_embed._get_pretrained_tokenizer(embedding_url)

    def predict(self, transcript=[]):
        try:
            lemmatized_text = get_lemmatize_hashtag(transcript)
            embedded_vector = self.word_embed._get_embedded_vector(lemmatized_text)
            scores = self.model.predict(embedded_vector)
            return np.squeeze(scores)
        except:
            print("Error in predicting outrage")
            return np.array([0.0])

class OutragePuppet(Puppet):
    def __init__(self, port):
        super().__init__(port)
        self.clf = OutrageClassifier()   
        self.high = True

    def transcriptOutrage(self, transcript):
        scores = self.clf.predict(transcript)
        return np.mean(scores)

    def getOutrage(self, videoId):
        transcript = self.yt.getTranscript(videoId, listed=True)
        if transcript == [] or transcript == "" or transcript == ["blank"]:
            return 0.0
        print(videoId)
        score = self.transcriptOutrage(transcript)
        return round(score, 3)

    def decisionFunction(self, recommendations):
        scores = list(map(lambda x: self.getOutrage(x), recommendations))
        return scores
