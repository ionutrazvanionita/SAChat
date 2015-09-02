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
        self.fname = 'lexicon/NRC-Hashtag-Emotion-Lexicon-v0.2.txt'
        self.word_dict = {}
        self.sentiments = ['joy','sadness', 'surprise','disgust', 'anger', 'fear']
        self.depeche_sents = ['afraid', 'amused', 'angry', 'annoyed','dcare', 'happy', 'inspired', 'sad']
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
            if pos[0] == 'V':
                #WordNetLemmatizer converts verbs to present tense
                new_lst.append((WordNetLemmatizer().lemmatize(word, 'v'), 'v'))
            if pos[0] == 'R':
                new_lst.append((word, 'r'))
            if pos[0] == 'J':
                new_lst.append((word, 'a'))
            if pos[0] == 'N':
                new_lst.append((word, 'n'))

        return new_lst



    """
    """
    def extract_expressions(self, sent):
        return None

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
        prints first n lines from nps_chat corpus
        from start index start
        @param1 number of lines to print
        @param2 start index
    """
    def print_first_n_lines(self, n, start=0):
        for i in xrange(n):
            print nps_chat.tagged_posts()[i+start]

    def get_sent_and_make_replace(self, n, start=0):
        n = len(nps_chat.tagged_posts())
        train_corpus = []

        #remove this; just for test
        n = 1000

        for i in xrange(n):
            train_sent = []
            sent = nps_chat.tagged_posts()[i+start]
            for word, pos in sent:
                word = self.make_subst(word)
                train_sent.append((word,pos))
            train_corpus.append(train_sent)

    def replace_words_in_corpus(self):
        n = len(nps_chat.tagged_posts())
        f = open('corpusv2', 'w')

        for i in xrange(n):
            words = nps_chat.posts()[i]
            #we jump over one word replies
            if (len(words) == 1):
                continue
            if words[0].startswith('.') and str.lower(words[1]).startswith('action'):
                continue
            if str.lower(words[0]) == 'nick':
                continue
            for j in xrange(len(words)):
                word = self.make_subst(words[j])
                words[j] = word
            f.write(' '.join(words)+'\n')

    def get_props_for_words(self):
        self.read_attr_file()
        with open('corpusv2') as f:
            lines = f.readlines()

        prob_list = []

        maxim = 0
        for sent in lines:
            tmp_dict = {}
            words = nltk.word_tokenize(sent)
            for word in words:
                # this denotes a username; we don't consider it
                if word == 'user':
                    continue
                word = str.lower(word)
                for sentiment in self.sentiments:
                    if word in self.word_dict[sentiment]:
                        if sentiment in tmp_dict:
                            tmp_dict[sentiment] = tmp_dict[sentiment] + self.word_dict[sentiment][word]
                        else:
                            tmp_dict[sentiment] = self.word_dict[sentiment][word]
            if tmp_dict != {}:
                pred_sent=max(tmp_dict, key=tmp_dict.get)
            else:
                pred_sent='neutral'

            with open('sentiments/'+pred_sent, 'a') as ff:
                if pred_sent == 'neutral':
                    ff.write(sent[:-1] + '|' + pred_sent + '|0\n')
                else:
                    ff.write(sent[:-1] + '|' + pred_sent + '|' + str(tmp_dict[pred_sent]) + '\n')
            prob_list.append(tmp_dict)

#        for i in xrange(len(prob_list)):
#            print prob_list[i]


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


    def read_attr_file(self):
        with open(self.fname) as f:
            lines = f.readlines()

        for line in lines:
            toks = line.split('\t')
            toks[2] = toks[2][:-1]
            if toks[1][0] == '#':
                toks[1] = toks[1][1:]

            if toks[0] not in self.word_dict:
                self.word_dict[toks[0]] = {}

            self.word_dict[toks[0]][toks[1]] = float(toks[2])

        print self.word_dict['anticipation']['davis']
        print 'ironic' in self.word_dict['disgust']

    """
        change of strategy
        calculate for each sentiment a score for a phrase
    """
    def write_chat_infile(self):
        f = open('corpus', 'w')
        n = len(nps_chat.tagged_posts())
        for i in xrange(n):
            sent = ' '.join(nps_chat.posts()[i])
            sent = str.lower(sent)
            f.write(sent + '\n')

    def hand_analyzer(self):
        f = open('tags', 'a')
        print 'unde ai ramas?'
        strnum = sys.stdin.readline()
        start = int(strnum)

        n = len(nps_chat.tagged_posts())
        for i in xrange(n-start):
            sent = ' '.join(nps_chat.posts()[i+start])
            sent = str.lower(sent)
            print sent
            print """Type:
\t'j' or 'J' for Joy
\t's' or 'S' for Sadness
\t'p' or 'P' for surPrise
\t'f' or 'F' for Fear
\t'd' or 'D' for Disgust
\t'a' or 'A' for Anger
\t'n' or 'N' for Neutral
\t'x' or 'X' for eXclude
\t'e' or 'E' for save and exit"""
            char = sys.stdin.readline()

            if char[0]=='x' or char=='X':
                print 'excluding'
                continue
            elif char[0]=='e' or char=='E':
                f.close()
                sys.exit(1)

            f.write(str(i+start)+'|')
            if char[0]=='j' or char == 'J':
                f.write(sent +  '|joy\n')
            elif char[0]=='s' or char=='S':
                f.write(sent +  '|sadness\n')
            elif char[0]=='p' or char=='P':
                f.write(sent +  '|surprise\n')
            elif char[0]=='f' or char=='F':
                f.write(sent +  '|fear\n')
            elif char[0]=='d' or char=='D':
                f.write(sent +  '|disgust\n')
            elif char[0]=='a' or char=='A':
                f.write(sent +  '|anger\n')
            elif char[0]=='n' or char=='N':
                f.write(sent +  '|neutral\n')
            else:
                print 'unknown'

    """
        maximum score for each sentiment
        used for normalization
    """
    def get_max_score(self):
        max_dict = {}
        for s in self.sentiments:
            with open('sentiments/'+s, 'r') as f:
                lines = f.readlines()

            for line in lines:
                toks = line.split('|')
                score = toks[2][:-1]
                if s not in max_dict:
                    max_dict[s] = float(score)
                elif float(score) > max_dict[s]:
                    max_dict[s] = float(score)

        print max_dict

        for s in self.sentiments:
            self.read_attr_file()
            with open('sentiments/'+s, 'r') as f:
                lines = f.readlines()

            for line in lines:
                toks = line.split('|')

                score = toks[2][:-1]
                words = nltk.word_tokenize(toks[0])

                #max rank 10; 0 not allowed in multiclass
                rank = int(float(score)/max_dict[s]*9)+1
                with open('sentiments/dataset_'+s, 'a') as ff:
                    ff.write(str(rank) + ' |')
                    for word in words:
                        if not word.isalpha():
                            continue
                        if word == 'user':
                            continue
                        if word in self.word_dict[s]:
                            ff.write(' ' + word + ':' + str(self.word_dict[s][word]))
                        else:
                            ff.write(' ' + word)
                    ff.write('\n')

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
            myparser.read_depeche_into_dict()

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
            if scores[s] < minn:
                minn = scores[s]
            if scores[s] > maxx:
                maxx = scores[s]

        for s in self.depeche_sents:
            scores[s] = (scores[s] - minn)/(maxx-minn)

        return scores


myparser=Parser()
#sent_list = myparser.parse_para(sent)
#mysent = "Amniotic fluid used to save baby's life."
#print myparser.get_score_for_phrase(mysent)

"""
myparser.pos_help('IN')
myparser.pos_help('P')
"""
