import enchant
from enchant.checker import SpellChecker
import nltk

def spellcheck(s, lang="en_US"):
    # import textblob
    # c = textblob.TextBlob(s).correct()
    # print("{}\n{}\n".format(s, c))
    # return c
    chk = SpellChecker(lang)
    chk.set_text(s)
    for e in chk:
        e.replace(e.suggest()[0])
    print("{}\n{}\n".format(s, chk.get_text()))
    return chk.get_text()
def error_rate(s, lang="en_US"):
    tok = nltk.word_tokenize(s)
    tok = [w for w in tok]
    errors = [len(nltk.corpus.wordnet.synsets(w)) == 0 for w in tok]
    return sum(errors) / len(tok)
    # tkn = enchant.tokenize.get_tokenizer(lang)
    # tkn = list(tkn(s))
    # if len(tkn) == 0:
    #     return 1
    # return len(chk) / len(tkn)
