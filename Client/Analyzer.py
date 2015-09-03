import re
import itertools
import nltk
import nltk.data
from nltk.corpus import nps_chat
import sys
from nltk.stem.wordnet import WordNetLemmatizer


sent = """We are not happy about what happened last night. You are very smart. The beautiful sun is up."""


class Parser:
    def __init__(self):
        #train the sentence detctor
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.word_dict = {}
        self.depeche_sents = ['afraid', 'amused', 'angry', 'annoyed','don\'t care', 'happy', 'inspired', 'sad']
        self.depeche_dict = {}
        self.sent_averages = {}
        self.sent_maxes = {}
        self.sent_mins = {}

    """
        split a paragraph into sentences using nltk punkt
        @param1 paragraph to be parsed
        @return list of sentences
    """
    def parse_para(self, para):
        return self.sent_detector.tokenize(para.strip())

    """
        part of speech tagging for a sentnce
        @param1 sentence to be parsed
        @return list of (word, POS_TAG)
    """
    def pos_tag(self, sent):
        toks = nltk.word_tokenize(sent)
        return nltk.pos_tag(toks)

    """
        @param1 list of touples (word, pos)
        @return list of touples (word, pos)
        the pos shall be one of a - adjective,
        n - noun, r - adverb, v - verb
        the rest shall be discarded
    """
    def transform_to_depeche_tags(self, lst):
        new_lst = []
        for (word, pos) in lst:
            #WordNetLemmatizer converts verbs to present tense, nouns
            #to singular form etc.
            if pos[0] == 'V':
                new_lst.append((WordNetLemmatizer().lemmatize(word, 'v'), 'v'))
            if pos[0] == 'R':
                new_lst.append((WordNetLemmatizer().lemmatize(word, 'r'), 'r'))
            if pos[0] == 'J':
                new_lst.append((WordNetLemmatizer().lemmatize(word, 'a'), 'a'))
            if pos[0] == 'N':
                new_lst.append((WordNetLemmatizer().lemmatize(word, 'n'), 'n'))

        return new_lst

    """
        for a given pos prints info about
        that pos
    """
    def pos_help(self, pos):
        nltk.help.upenn_tagset(pos)

    """
        given a list of words constructs ngrams
        @param1 the list of words
        @param2 the number of grams
        @return list of ngrams
    """
    def extract_ngrams(self, list, n):
        ngrams=[]
        i = 0
        while i < len(list) - n:
            j = 0
            tup = list[j+i]
            j = j+1
            while j < n:
                tup = tup, list[j+i]
                j = j+1
            ngrams.append(tup)
            i=i+1
        return ngrams

    def parse_ngrams(self, ngram_list):
        for el in ngram_list:
            print el

    """
        substitues word
        if elongated bring it to normal
        if 'n't' transform to 'not'
        TBD
    """
    def make_subst(self, word):
        word = str.lower(word)
        if word[0] == 'n' and word == 'n\'t':
            return 'not'
        if word[0] == 'i' and (word == 'i\'m' or word == 'im'):
            return 'i am'
        if word == 'wanna':
            return 'want to'
        if word[0] == 'u' and word[1:].isdigit():
            return 'user'
        if word == 'ya':
            return 'you'
        if word == 'whats':
            return 'what is'
        if word == '\'ll':
            return 'will'
        if word == 'dont':
            return 'do not'
        if word == 'outta':
            return 'out of'
        if word == 'gettin':
            return 'getting'
        if word == 'that\'s' or word =='thats':
            return 'that is'
        if word == 'kinda':
            return 'kind of'
        if word == 'gosh':
            return 'god'
        if word == 'n':
            return 'and'
        if self.is_elong(word):
            return self.rem_elong(word)
        if word.startswith(':)') or word.startswith(':-)'):
            return 'happy'
        if word.startswith(':(') or word.startswith(':-('):
            return 'sad'
        if word.startswith(':d') or word.startswith(':-d'):
            return 'excited'
        if word.startswith(':p') or word.startswith(':-p'):
            return 'ironic'
        if word.startswith('xd'):
            return 'laugh'
        if word.startswith('<3'):
            return 'love'
        if word.startswith(':o') or word.startswith(':-o'):
            return 'surprised'
        if word.startswith(';)') or word.startswith(';-)'):
            return 'winking'
        if word.startswith(':*(') or word.startswith(':\'('):
            return 'crying'
        if word.startswith(':s') or word.startswith(':-s'):
            return 'worried'
        if word.startswith(':\\'):
            return 'displeased'
        if word.startswith('>:('):
            return 'angry'
        if word.startswith('b)'):
            return 'cool'
        if word.startswith('>:)'):
            return 'evil'
        if word.startswith(':^*'):
            return 'cheer'
        if word == 'u':
            return 'you'
        if word == 'r':
            return 'are'
        if word == '\'m':
            return 'am'
        if word == '\'re':
            return 'are'
        if word == 'wonna':
            return 'wanna'
        if word == 'wb':
            return 'welcome back'
        if word == 'ty':
            return 'thanks'
        if word == 'allright':
            return 'all right'
        if word == 'ppl':
            return 'people'
        if word == 'ima':
            return 'i am going to'
        if word == 'ur':
            return 'you are'
        if word == 'ca':
            return 'see you'


        return word

    """
        checks if a word is elongated
        @param1 the word to check
        @return true or false if word is elongated
    """
    def is_elong(self, word):
        elong = re.compile('([a-zA-Z])\\1{2,}')
        return bool(elong.search(word))

    """
        @param1 elongated word
        @return normal word
        (one must be sure that word is elongated))
        if word like upppppeeeeerrr will be converted to uper
    """
    def rem_elong(self, word):
        return re.sub(r'(.)\1+', r'\1', word)


    def read_depeche_into_dict(self):
        with open("depeche/lexicon", "r") as f:
            lines = f.readlines()

        for line in lines[1:]:
            toks = line.split('\t')
            first = toks[0].split('#')
            if not first[0] in self.depeche_dict:
                self.depeche_dict[first[0]] = {}

            self.depeche_dict[first[0]][first[1]] = {}
            i = 1
            for s in self.depeche_sents:
                self.depeche_dict[first[0]][first[1]][s] = float(toks[i])
                i = i + 1

        #get average for each sentiment
        for line in lines[1:]:
            toks = line.split('\t')
            i = 1
            for s in self.depeche_sents:
                if not s in self.sent_averages:
                    self.sent_averages[s] = (float(toks[i]), 1)
                    self.sent_maxes[s] = (float(toks[i]))
                    self.sent_mins[s] = (float(toks[i]))
                else:
                    (summ, count) = self.sent_averages[s]
                    self.sent_averages[s] = (summ + float(toks[i]), count+1)
                    if float(toks[i]) > self.sent_maxes[s]:
                        self.sent_maxes[s] = float(toks[i])
                    if float(toks[i]) < self.sent_mins[s]:
                        self.sent_mins[s] = float(toks[i])
                i = i + 1

        for s in self.depeche_sents:
            (summ, count) = self.sent_averages[s]
            self.sent_averages[s] = summ/count


    def get_depeche_score(self, lst):
        score_dict = {}
        for (word, pos) in lst:
            if word in self.depeche_dict and pos in self.depeche_dict[word]:
                for key in self.depeche_dict[word][pos]:
                    if not key in score_dict:
                        score_dict[key] = (self.depeche_dict[word][pos][key], 1)
                        self.sent_mins[key] = self.depeche_dict[word][pos][key]
                        self.sent_maxes[key] = self.depeche_dict[word][pos][key]
                    else:
                        (value, no) = score_dict[key]
                        score_dict[key] = (value + self.depeche_dict[word][pos][key], no+1)

                        #find the mins and maxes for each value
                        if self.depeche_dict[word][pos][key] > self.sent_maxes[key]:
                            self.sent_maxes[key] = self.depeche_dict[word][pos][key]
                        if self.depeche_dict[word][pos][key] < self.sent_mins[key]:
                            self.sent_mins[key] = self.depeche_dict[word][pos][key]

        for key in score_dict:
            (score, number) = score_dict[key]
            score_dict[key] = score/number
        return score_dict

    def get_score_for_phrase(self, sent):
        if not self.depeche_dict:
            self.read_depeche_into_dict()

        words = sent.split(' ')
        nwords = []
        for word in words:
            word=self.make_subst(word)
            nwords.append(word)

        sent= ' '.join(nwords)

        poses = self.pos_tag(sent)
        dposes =self.transform_to_depeche_tags(poses)

        scores = self.get_depeche_score(dposes)

        #normalize based on the average score of all words
        maxx = 0
        minn = 1
        for s in self.depeche_sents:
            if s in scores and scores[s] < minn:
                minn = scores[s]
            if s in scores and scores[s] > maxx:
                maxx = scores[s]

        for s in self.depeche_sents:
            if s in scores:
                scores[s] = (scores[s] - minn)/(maxx-minn)

        return scores
