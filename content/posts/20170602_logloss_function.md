---
title: LogLoss Function
date: '2017-06-02T12:17:34+00:00'
draft: false
categories:
- Machine Learning
summary: 'Function From scikit-learn: This is the loss function used in (multinomial)
  logistic regression and extensions of it such as neural networks, defined as the
  negative log-likelihood of the true labels ...'
math: true
---

# Function

From [scikit-learn](http://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html): This is the loss function used in (multinomial) logistic regression and extensions of it such as neural networks, defined as the negative log-likelihood of the true labels given a probabilistic classifier’s predictions. The log loss is only defined for two or more labels. For a single sample with true label yt in {0,1} and estimated probability yp that yt = 1, the log loss is $$-log P(yt|yp) = -(yt\\ log(yp) + (1 - yt) log(1 - yp))$$more

However, the actual scroe of 'is\_duplicate' equals 1 or 0, we can derive from this function into $$-log P(yt|yp) = -(log(yp) + log(1 - yp))$$

# Source data

Because of the copy right issue, I give you part of the data. Originally, the dataset contains 6 columns: id, qid1, qid2, question1, question2, is\_duplicate, which is used to train a model to distinguish whether two questions are duplicate.

| id | qid1 | qid2 | question1 | question2 | is\_duplicate |
| --- | --- | --- | --- | --- | --- |
| $0$ | 1 | 2 | What is the step by step... | What is the step by step guide to invest in sh... | 0 |
| $1$ | 3 | 4 | What is the story of... | What would happen if the Indian government sto... | 0 |
| $2$ | 5 | 6 | How can I increase the speed... | How can Internet speed be increased by hacking... | 0 |

However, we don't need actul text in questions in order to learn LogLoss function. Aa a result, I delete 'question1', 'question2', and release this edition: {% asset\_link train.csv trainingData %}

| id | qid1 | qid2 | is\_duplicate |
| --- | --- | --- | --- |
| 0 | 1 | 2 | 0 |
| 1 | 3 | 4 | 0 |
| 2 | 5 | 6 | 0 |

# Code

1. Self-Defined LogLoss
    

```python
import pandas as pd
import numpy as np
path = 'path/to/train.csv'
df_train = pd.read_csv(path)
df_train.head()

def logloss(actual, predict):
    predict = min(max(predict, 1e-15), (1 - (1e-15)))  
    ##if the number smaller than 10^-15, then define it to be 10^-15
    ##if the number bigger than 1-(10^-15), then define it to be 1-(10^-15)
    
    if actual == 1:    ##actual==1, else(actual==0)
        return np.log(predict)    ##numpy default log == ln (with e as base)
    else:
        return np.log(1-predict)
    
predict = np.average(df_train['is_duplicate'])    
##Assume our model predict every query pair has a score of average score of all pairs
print(predict)
LoglossList = [-logloss(actual, predict) for actual in df_train['is_duplicate']]
LoglossScore = np.average(LoglossList)
print(LoglossScore)
```

2. Use sklearn
    

```python
from sklearn.metrics import log_loss

p = np.average(df_train['is_duplicate'])    ##directly use average score
print(p)
LoglossScore = log_loss(df_train['is_duplicate'], np.zeros_like(df_train['is_duplicate']) + p)
print(LoglossScore)
```
