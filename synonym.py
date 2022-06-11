import torch
from nltk.corpus import wordnet
from transformers import BertTokenizer, BertModel, BertForMaskedLM
from transformers import AutoTokenizer
from scipy.spatial.distance import cosine
import nltk
nltk.download('wordnet')

class Synonym():

    def __init__(self, source):
        self.source = source
        self.bert_model = BertModel.from_pretrained("bert-base-uncased", output_hidden_states = True)
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        #self.bert_model = BertForMaskedLM.from_pretrained("bert-base-uncased", output_hidden_states = True)
        self.bert_auto_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")


    def bert_text_preparation(self, text):
        marked_text = "[CLS] " + text + " [SEP]"
        tokenized_text = self.bert_auto_tokenizer.tokenize(marked_text)
        indexed_tokens = self.bert_auto_tokenizer.convert_tokens_to_ids(tokenized_text)
        segment_ids = [1] * len(indexed_tokens)

        tokens_tensor = torch.tensor([indexed_tokens])
        segments_tensors = torch.tensor([segment_ids])

        return tokenized_text, tokens_tensor, segments_tensors

    def get_hidden_states(self, tokens_tensors, segments_tensors):
        with torch.no_grad():
            outputs = self.bert_model(tokens_tensors, segments_tensors)
            hidden_states = outputs[2]
        token_embeddings = torch.stack(hidden_states, dim=0)
        token_embeddings = torch.squeeze(token_embeddings, dim= 1)
        token_embeddings = token_embeddings.permute(1, 0, 2)

        return token_embeddings


    def embed_with_sum(self, token_embeddings):
        token_vecs_sum = []
        for token in token_embeddings:
            sum_vec = torch.sum(token[-4:], dim=0)
            token_vecs_sum.append(sum_vec)

        return token_vecs_sum


    def get_subword_info(self, encoded):
        desired_output = [0]
        #print("encoded:", encoded)
        for word_id in encoded.word_ids():
            if word_id is not None:
                start, end = encoded.word_to_tokens(word_id)
                if start == end - 1:
                    tokens = [start]
                else:
                    tokens = [start, end - 1]
                if len(desired_output) == 0 or desired_output[-1] != tokens:
                    desired_output.append(tokens)
        desired_output.append(end)

        return desired_output

    def get_embedding(self, text, target):
        tokenized_text, tokens_sensor, segments_sensor = self.bert_text_preparation(text)
        subwords = self.get_subword_info(self.bert_auto_tokenizer(text))
        index = text.split(" ").index(target) + 1

        embed_list = self.get_hidden_states(tokens_sensor, segments_sensor)
        token_vecs_sum = self.embed_with_sum(embed_list)

        if len(subwords[index]) > 1:
            data = torch.stack(token_vecs_sum[subwords[index][0]:subwords[index][1]+1])
            return torch.mean(data, dim=0)
        else:
            return token_vecs_sum[index]


    def get_cosine(self, v1, v2):
        return 1 - cosine(v1, v2)

    def synonym_antonym_extractor(self, query):
        synonyms = []
        max_sim = 0
        best_synonym = ""
        for phrase in query.split():
            for candidates in wordnet.synsets(phrase):
                for lemma in candidates.lemmas():
                    print(lemma.name())
                    v1 = self.get_embedding(query, phrase) #buraya sadece query gelecek
                    v2 = self.get_embedding(lemma.name(), phrase) # buraya sadece synonym gelecek
                    sim = self.get_cosine(v1, v2)
                    print(sim)
                    if sim > 0.95 and lemma.name().lower() != phrase:
                        #best_synonym = lemma.name()
                        #max_sim = sim
                        synonyms.append(lemma.name())
                    #synonyms.append(lemma.name())
        return synonyms