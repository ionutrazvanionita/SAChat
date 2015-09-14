import sys
import nltk

def parser_func():
    f = 'lexicon'
    help_line = """Afraid/aNgry/annoYed/Sad
Dontcare
aMused/Happy/Inspired
iRrelevant
If you follow sent letter by M you can enter more variants of this word\n"""

    with open('lexicon', 'r') as f:
        lines = f.readlines()

    w = open('tagged', 'w')
    for line in lines:
        word = line[:-1]
        word = str.lower(word)

        if not word.isalpha():
            continue

        sent = ''

        res = raw_input(help_line+word+'\n'+'\n')
        res = str.lower(res)
        if res[0] == 'a':
            sent = 'A'
        if res[0] == 'm':
            sent = 'M'
        if res[0] == 'n':
            sent = 'N'
        if res[0] == 'y':
            sent = 'Y'
        if res[0] == 'd':
            sent = 'D'
        if res[0] == 'h':
            sent = 'H'
        if res[0] == 'i':
            sent = 'I'
        if res[0] == 's':
            sent = 'S'
        if res[0] == 'r':
            continue
        if res[0] == 'q':
            break
        w.write(word+'#'+sent+'\n')

        if len(res) > 1 and res[1] == 'm':
            new_words = raw_input('Insert list of words here\n')
            new_lst = new_words.split(',')
            for nword in new_lst:
                w.write(nword+'#'+sent+'\n')

    w.close()



parser_func()
