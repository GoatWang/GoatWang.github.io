---
title: Bi-Tempered Loss — 處理錯誤標記資料的損失函數
date: '2021-09-21T09:17:31+00:00'
draft: false
categories:
- Machine Learning
summary: '由於最近開始接觸工廠產線瑕疵檢測專案，工廠端對於錯誤判釋的可能幾乎是零容忍，因此一直致力於處理到99%準確率以上的模型瑕疵，但是工廠的訓練資料集大多都上萬張，要把所有錯誤標記抓出來實在太痛苦，剛好又被Medium廣告打到這篇文章:
  How To Train ML Models With Mislabeled Data，於是便開始研究Bi-Tempered Loss這個神奇的損失函數。 不過…先說結...'
cover:
  image: /images/posts/20210921_bi_tempered_loss/4c89fc48-2091-48dc-884e-85a2024a1a79.png
---

由於最近開始接觸工廠產線瑕疵檢測專案，工廠端對於錯誤判釋的可能幾乎是零容忍，因此一直致力於處理到99%準確率以上的模型瑕疵，但是工廠的訓練資料集大多都上萬張，要把所有錯誤標記抓出來實在太痛苦，剛好又被Medium廣告打到這篇文章: [How To Train ML Models With Mislabeled Data](https://aminey.medium.com/how-to-train-ml-models-with-mislabeled-data-cf4bb353b3d9)，於是便開始研究Bi-Tempered Loss這個神奇的損失函數。

不過…先說結論，雖然這個損失函數能夠有效對抗錯誤標記的資料，但也必須視**錯誤標記的比例**以及**超參數調整**才有機會得到比較好的效果，再加上目前google官方提供的程式碼僅有支援[tensorflow](https://github.com/google/bi-tempered-loss)且要修改過方可使用，此外這個損失函數的實作複雜到必須自己定義Gradient的計算方式，keras幾乎無法直接使用(PyTorch有Git Repo但我沒試過)，所以個人建議還是以調整資料的Label優先，真的沒辦法再來試試看這個損失函數。

### Bi-Tempered Loss的目的

Bi-Tempered Loss是Google在2019在[Arxiv](https://arxiv.org/abs/1906.03361)發表的文章，最主要的目的是用來對抗錯誤標記的資料。在[Google AI Blog](https://ai.googleblog.com/2019/08/bi-tempered-logistic-loss-for-training.html)中，錯誤標記的資料又分成兩種，一種是**距離正確答案很遙遠的離群值樣本**，如果用平均來計算所有樣本的損失，這種離群值將會很大程度的影響總體損失，以Mnist來說就是看起來根本不相似的數字照片被錯誤標記，像是1的照片被錯誤標記成3。另一種，則是**介在答案邊界周圍但錯誤標記的樣本**，這種錯誤會讓模型的判斷邊界變得模糊無法明確二值化，以Mnist來說就是看起來很相似的數字照片被錯誤標記，像是9的照片被錯誤標記成7。Bi-Tempered Loss中t1與t2的參數設置，便是用來處理這兩種類型的錯誤標記。以下是[Google AI Blog](https://ai.googleblog.com/2019/08/bi-tempered-logistic-loss-for-training.html)對這兩種錯誤標記的解釋。

> **Outliers far away can dominate the overall loss:** The logistic loss function is [sensitive to outliers](http://phillong.info/publications/LS08_potential.pdf). This is because the loss function value grows without bound as the mislabelled examples (outliers) are far away from the [decision boundary](https://en.wikipedia.org/wiki/Decision_boundary). Thus, a single bad example that is located far away from the decision boundary can penalize the training process to the extent that the final trained model learns to compensate for it by stretching the decision boundary and potentially sacrificing the remaining good examples. This “large-margin” noise issue is illustrated in the left panel of the figure below.

> **Mislabeled examples nearby can stretch the decision boundary:** The output of the neural network is a vector of [activation](https://en.wikipedia.org/wiki/Activation_function) values, which reflects the [margin](https://en.wikipedia.org/wiki/Margin_%28machine_learning%29) between the example and the decision boundary for each class. The [softmax transfer function](https://en.wikipedia.org/wiki/Softmax_function) is used to convert the activation values into probabilities that an example will belong to each class. As the tail of this transfer function for the logistic loss decays exponentially fast, the training process will tend to stretch the boundary closer to a mislabeled example in order to compensate for its small margin. Consequently, the generalization performance of the network will immediately deteriorate, even with a low level of label noise (right panel below).

### Bi-Tempered Loss的作用

在[Google AI Blog](https://ai.googleblog.com/2019/08/bi-tempered-logistic-loss-for-training.html)中，有針對不同類型的錯誤標記進行訓練測試。測試結果如下圖，每個點都是一個樣本，紅色與白色的底代表模型的決定邊界。clean dataset是沒有錯誤標記的資料，這類型的資料無論使用Logistic Loss或是Bi-Tempered Loss效果都不錯。small margin noise跟large margin noise則是包含部分**介在答案邊界周圍但錯誤標記的樣本**跟**距離正確答案很遙遠的離群值樣本**，這種類型的錯誤可以透過Bi-Tempered Loss中t2(small margin noise)與t1(large margin noise)的參數設置進行訓練，很明顯地使用Bi-Tempered Loss進行模型訓練可以得到較銳利的決定邊界。Logistic Loss則會很大程度的受到noise的影響。

![](/images/posts/20210921_bi_tempered_loss/7b1da4ca-1e1e-4fdf-b960-2c45747bf0bc.png)

### Bi-Tempered Loss的實際影響

以下實驗架設正確答案為1，並使用不同的預測機率(0到1之間)，測試在特定t1與t2的設置下loss的大小(Code部分詳見[Github Repo](https://github.com/GoatWang/bi-tempered-loss-tensorflow/))。如下圖所示，最左邊的圖是Logistic Loss 跟Bi-Tempered Loss的比較，中間與右邊兩張圖分別是不同的t1與t2設置的比較。可以發現:

1. 比起Logistic Loss，Bi-Tempered Loss更為平滑。
    
2. t1可以調整Loss的規模(scale)，對於large margin noise而言，Bi-Tempered Loss比起Logistic Loss，loss的最大值與最小值的差距可以被大幅度的縮小。
    
3. t2可以調整Loss的斜率(slope)，對於small margin noise而言，可以放大預測值與正確答案的微小差距在loss上的影響。
    

![](/images/posts/20210921_bi_tempered_loss/995bb9bf-4c9b-45cd-98c9-246d51858f88.png)

### Mnist實測

為了實際測試Bi-Tempered Loss的效果，這裡使用google提供tensorflow版本的Bi-Tempered Loss在Mnist資料及上面進行訓練測試。分別使用t1為1.0、0.6、0.2，t2為1.0、2.0、4.0對參雜Noise的訓練資料集進行訓練，並使用沒有參雜Noise的測試資料集進行模型評價(Code部分詳見[Github Repo](https://github.com/GoatWang/bi-tempered-loss-tensorflow/))。

下圖是在有10%的Noise的訓練資料集上訓練的成果，其中t1與t2同時等於1的情況就相當是使用CrossEntropy Loss進行訓練，很明顯可以發現CrossEntropy Loss雖然起初訓練可以有不錯的準確率(Accuracy)，但在越後面的Epoch其過度擬合的狀況就越明顯，反而是Bi-Tempered Loss可以在後面的Epoch持續具有對抗Noise的能力。

![](/images/posts/20210921_bi_tempered_loss/65d3dbbb-02c9-4201-acba-12a0f8b3ac97.png)

為了可以確保模型在後續訓練仍持續具有對抗Noise的能力，此處用最後一個(第15個)Epoch訓練結束時測試資料集上的準確率作為評價標準。下圖可以看到所有測試中不同的t1與t2在測試資料集上準確率的表現，可以發現當資料沒有Noise時CrossEntropy Loss與Bi-Tempered Loss(t2=2)表現都很不錯，但是當有Noise參雜其中時Bi-Tempered Loss(t1=0.2, t2=2)的表現大都可以得到比較好的成果。

![](/images/posts/20210921_bi_tempered_loss/7a612ebb-c616-4e50-aa25-103d4fd0bf31.gif)

### 結論

1. 參數t1與t2的設定會嚴重影響Bi-Tempered Loss的表現。
    
2. 參數t1與t2的設定良好，Bi-Tempered Loss可以比CrossEntropy Loss表現良好。
    
3. 如果Noise不大，Bi-Tempered Loss可能比CrossEntropy Loss表現更差。
    
4. (個人建議)還是把Label檢查到正確比較實際。  
    第一、如果無法確保測試資料集沒有Noise，無法正確評價模型的表現。  
    第二、如果無法正確評價模型的表現，參數t1與t2的調整只能憑感覺。  
    第三、如果t1與t2的調整不良，可能會得到比CrossEntropy Loss更差的結果。
