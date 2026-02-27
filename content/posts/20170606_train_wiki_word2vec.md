---
title: Train Wiki Corpus by gensim Word2vec
date: '2017-06-06T11:44:06+00:00'
draft: false
categories:
- Information Retrieval
summary: 'What is Word2vec? There are some keywords about the model for you to consider:
  unsupervised learning, LSTM, encode(translate) a word to a vector. Actually, I don''t
  know exactly about the theory of wor...'
---

# What is Word2vec?

There are some keywords about the model for you to consider: unsupervised learning, LSTM, encode(translate) a word to a vector. Actually, I don't know exactly about the theory of word2vec. What I can tell you is that, using models training from a corpus by this method, you can find related words a specific word or a words list. In addition, the most famous point of this theory is that the vectors of retlated words translated by this model can be caculated. For example, the (vector of) king - man = queen - woman. That is, you can caculate Taiwan's vector by France - Paris + Taipei.more

# To be installed

* [pandas](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pandas)
    
* [gensim](http://www.lfd.uci.edu/~gohlke/pythonlibs/#gensim)
    
* nltk (using , I am using python3.5 32bit, and I am not sure if it works for other edition of python)
    

```sh
$ python -m pip install nltk
```

* [nltk data](http://www.nltk.org/data.html)
    

# Test gensim word2cev function

## Preprocess nltk predownload corpus(5 mins)

```python
import pandas as pd
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords

st = LancasterStemmer()    ##You can also select Porter stemmer, through which you can remove 's', 'ed', 'es' in the end of a word.

from gensim.models import Word2Vec
from nltk.corpus import brown, movie_reviews, treebank   ##I use these three coupuses to test

stops = stopwords.words("english")    ## remove stop words such as: the, and , is, are...... you can print stops to see what words will be drop
def removestops(item):
    WithoutStops = pd.Series([word for word in item if word not in stops])
    Stemmed = list(WithoutStops.apply(st.stem))
    return Stemmed
brownLi = pd.Series(brown.sents()).apply(removestops)    
## from brown.sents(), you can see preprocessed documents in form of list collected in a list 
## apply function can apply defined function to each item in pandas' Series(DataFrame also work)
movie_reviewsLi = pd.Series(movie_reviews.sents()).apply(removestops)
treebankLi = pd.Series(treebank.sents()).apply(removestops)

print(len(brownLi))
print(len(movie_reviewsLi))
print(len(treebankLi))
```

## train them and see the result:

```python
    b = Word2Vec(brownLi)
    mr = Word2Vec(movie_reviewsLi)
    t = Word2Vec(treebankLi)

    mon_b = pd.Series(b.most_similar('money', topn=5))
    mon_mr = pd.Series(mr.most_similar('money', topn=5))
    mon_t = pd.Series(t.most_similar('money', topn=5))
    
    com_b = pd.Series(b.most_similar('company', topn=5))
    com_mr = pd.Series(mr.most_similar('company', topn=5))
    com_t = pd.Series(t.most_similar('company', topn=5)) 

    dataList = [mon_b,mon_mr,mon_t,com_b,com_mr,com_t]
    Indecies = ['mon_b','mon_mr','mon_t','com_b','com_mr','com_t']

    pd.DataFrame(data=dataList, index=Indecies)
```

## Result

|  | 0 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- | --- |
| mon\_b | ('imagin', '0.9841') | ('job', '0.9712') | ('learn', '0.9674') | ('chant', '0.9655') | ('child', '0.9646') |
| mon\_mr | ('away', '0.8631') | ('someon', '0.8479') | ('rewind', '0.8439') | ('wait', '0.8361') | ('try', '0.8236') |
| mon\_t | ('reg', '0.9999') | ('ag', '0.9999') | ('may', '0.9999') | ('institut', '0.9999') | ('stat', '0.9999') |
| com\_b | ('county', '0.9796') | ('highway', '0.9754') | ('railroad', '0.9752') | ('district', '0.9744') | ('redevelop', '0.969') |
| com\_mr | ('england', '0.9799') | ('london', '0.9774') | ('californ', '0.9738') | ('mexico', '0.9723') | ('chicago', '0.9712') |
| com\_t | ('ad', '0.9999') | ('could', '0.9999') | ('may', '0.9999') | ('ag', '0.9999') | ('also', '0.9999') |

# Start train Wiki corpus

## Download wiki Corpus

* Download the same corpus with me from this [link](https://dumps.wikimedia.org/enwiki/20170520/enwiki-20170520-pages-articles.xml.bz2)(about 13 GB )
    
* ps. I download this corpus at 2017/06/02. Also, you can download the [latested one](https://dumps.wikimedia.org/enwiki/latest/), find the link named: enwiki-latest-pages-articles.xml.bz2
    

## Notice

Before doing the following works, I have to notice you. The following tasks will take you about more than 15 hours, during which the cpu of your computer will run up to 90% to 100%. Take my computer for example, my CPU is Intel(R) Core(TM) i7-6500 CPU, and Ram is 8.00GB. And all following tasks took me up to 15 hours, during which I put two fans around my computer to help cold down. As a result, you have to check your working environment first, then do the following tasks.

## Preprocess Wiki Corpus(3.5 hours)

process the xml format wikipedia to text format using {% asset\_link process\_wiki.py process\_wiki.py %}, download it and put it into the directory where you save 'enwiki-xxxx-pages-articles.xml.bz2'. Then, Open your command line: go to the directory, and type:

```sh
python process_wiki.py enwiki-XXXX-pages-articles.xml.bz2 wiki.en.text   
##Remembeer to replace the filename
```

Output will be:

2017-06-03 07:06:22,577: INFO: Saved 10000 articles 2017-06-03 07:07:54,501: INFO: Saved 20000 articles 2017-06-03 07:09:07,157: INFO: Saved 30000 articles 2017-06-03 07:10:08,793: INFO: Saved 40000 articles 2017-06-03 07:10:58,331: INFO: Saved 50000 articles 2017-06-03 07:11:30,901: INFO: Saved 60000 articles 2017-06-03 07:12:02,807: INFO: Saved 70000 articles ... 2017-06-03 10:38:51,985: INFO: Saved 4270000 articles 2017-06-03 10:39:08,530: INFO: finished iterating over Wikipedia corpus of 4275675 documents with 2346581879 positions (total 17544907 articles, 2410007372 positions before pruning articles shorter than 50 words) 2017-06-03 10:39:08,538: INFO: Finished Saved 4275675 articles

## Train the word2vec model(13.5 hours)

download {% asset\_link train\_word2vec\_model.py train\_word2vec\_model.py %} and put it into the directory where you save 'wiki.en.text'. Then, open your command line: go to the directory, and type:

```sh
python train_word2vec_model.py wiki.en.text wiki.en.word2vec.model
```

I forget to record the output message, but it takes about 13 hours.

## Use the word2vec model

```python
import gensim
model = gensim.models.Word2Vec.load("D:\WikiCorpus\WikiModel\wiki.en.word2vec.model")
model.most_similar(positive=['teacher'],topn=20)
```

result:

```json
[
    ('schoolteacher', 0.683679461479187), 
    ('instructor', 0.6685980558395386), 
    ('tutor', 0.667843759059906), 
    ('educator', 0.6145995855331421), 
    ('teachers', 0.6062737107276917), 
    ('teaching', 0.5911847352981567), 
    ('lecturer', 0.5808757543563843), 
    ('librarian', 0.5734823346138), 
    ('pupil', 0.571779727935791), 
    ('professor', 0.5539975166320801), 
    ('schoolmaster', 0.547014057636261), 
    ('student', 0.545426607131958), 
    ('pedagogue', 0.5427858233451843), 
    ('headmaster', 0.5372023582458496), 
    ('mentor', 0.5237945318222046), 
    ('taught', 0.5192644596099854), 
    ('headmistress', 0.5052664279937744), 
    ('school', 0.500705361366272), 
    ('scholar', 0.4987880289554596), 
    ('classmate', 0.49570029973983765)
]
```

## Note

I modify the code from [this page](http://textminingonline.com/training-word2vec-model-on-english-wikipedia-by-gensim) because there are some encoding problems in windows system when using chinese as first language.
