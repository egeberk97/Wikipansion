import torch
from nltk.corpus import wordnet
from transformers import BertTokenizer, BertModel, BertForMaskedLM
from transformers import AutoTokenizer
from scipy.spatial.distance import cosine
import nltk


import requests
from bs4 import BeautifulSoup


class Synonym():

    def __init__(self, source):
        self.source = source
        self.bert_model = BertModel.from_pretrained("bert-base-uncased", output_hidden_states = True)
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        #self.bert_model = BertForMaskedLM.from_pretrained("bert-base-uncased", output_hidden_states = True)
        self.bert_auto_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    def get_source(self):
        return self.source

    def set_source(self, source):
        self.source = source

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

    def embed_last_layer(self, token_embeddings):
        token_vecs_sum = []
        for token in token_embeddings:
            sum_vec = token[-1]
            token_vecs_sum.append(sum_vec)

        return token_vecs_sum

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
        #print("context: ", text, "target: ", target)
        #target = target.strip()
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

    def get_pos_tag(self, query):
        tokenized = nltk.word_tokenize(query)
        list_pos = nltk.pos_tag(tokenized)
        return zip(*list_pos)

    def get_synonym_from_thesaurus(self, term):
        response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
        soup = BeautifulSoup(response.text, "html.parser")
        soup.find('section', {'class': 'css-191l5o0-ClassicContentCard e1qo4u830'})
        return [span.text for span in soup.findAll('a', {'class': 'css-1kg1yv8 eh475bn0'})]

    def sort_and_get_3(self, lst, syn):
        if lst[-1][1]< syn[1]:
            lst[-1] = syn
            lst = sorted(lst, key = lambda x : x[1], reverse = True)
        return lst

    def flatten(self, lst):
        return [x for xs in lst for x in xs]

    def get_synonym_from_thesaurus(self, term):
        response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
        soup = BeautifulSoup(response.text, 'html.parser')
        soup.find('section', {'class': 'css-191l5o0-ClassicContentCard e1qo4u830'})
        return [span.text for span in soup.findAll('a', {'class': 'css-1kg1yv8 eh475bn0'})]
    

    def synonym_antonym_extractor(self, query):
        synonyms = []
        max_sim = 0
        best_synonym = ""
        pos_filter = "NN"
        word, pos_tag = self.get_pos_tag(query)
        for phrase in query.split():
            lst = []
            if pos_tag[word.index(phrase)] not in pos_filter:
                #print(phrase, " is filtered - pos tag ", pos_tag[word.index(phrase)])
                continue
            if self.source.lower() == "wordnet":
                candidates_list = set(self.flatten([[lemma.name().lower() for lemma in candidates.lemmas()] for candidates in (wordnet.synsets(phrase))]))
            elif self.source.lower() == "thesaurus":
                candidates_list = set(self.get_synonym_from_thesaurus(phrase))
                #print(candidates_list)
                candidates_list = [x.strip() for x in candidates_list if len(x.strip().split(" ")) == 1]
                #print(candidates_list)
            else:
                #print("synonym source is invalid")
                return []

            for lemma in candidates_list:

                #print(lemma.name())
                v1 = self.get_embedding(query, phrase)
                v2 = self.get_embedding(query.replace(phrase, lemma), lemma)
                sim = self.get_cosine(v1, v2)
                #print((lemma,sim))
                #print(sim)
                if sim > 0.75 and lemma != phrase:
                    #best_synonym = lemma.name()
                    #max_sim = sim
                    if len(lst)<3:
                        lst.append((query.replace(phrase, lemma), sim))
                        lst = sorted(lst, key = lambda x : x[1], reverse = True)
                    else:
                        lst = self.sort_and_get_3(lst, (query.replace(phrase, lemma), sim))

            synonyms.extend([i[0] for i in lst])
                #synonyms.append(lemma.name())
        return synonyms