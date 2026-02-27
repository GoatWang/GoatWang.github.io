---
title: yolov4使用技術脈絡彙整 — Backbone
date: '2021-02-10T03:23:59+00:00'
draft: false
categories:
- Computer Vision
summary: 前言 最近為了使用yolov4，花了兩周把裡面引用到的論文與技術脈絡爬梳了一遍，發現yolov4幾乎整理了近年CNN技術的重要進展，並將能整合進yolov4的技術幾乎都用上了，真的只能由衷佩服。我搭配大量網路文章、影片的解釋，才比較弄懂每一篇論文的重要進展，作者竟然可以分門別類、按時間排序，把每本論文想解決的問題跟解決手段都整理出來，並整合使用在yolov4上，真的是嘔心瀝血之作。
  看完這些技術後...
cover:
  image: /images/posts/20210210_yolov4_backbone/81bbe92b-afb9-4d5d-b0c7-25060bd41076.png
---

### 前言

最近為了使用yolov4，花了兩周把裡面引用到的論文與技術脈絡爬梳了一遍，發現yolov4幾乎整理了近年CNN技術的重要進展，並將能整合進yolov4的技術幾乎都用上了，真的只能由衷佩服。我搭配大量網路文章、影片的解釋，才比較弄懂每一篇論文的重要進展，作者竟然可以分門別類、按時間排序，把每本論文想解決的問題跟解決手段都整理出來，並整合使用在yolov4上，真的是嘔心瀝血之作。

看完這些技術後，最大的感想是發現自己學習的CNN大約還是停留在2015年，學習到這些技術有種相見恨晚的感覺，許多自己過去做的專案都可以嘗試使用裡面提及的各種技術來解決問題。雖然，了解這些技術後也很難自己刻出yolov4(畢竟真的有太多技術細節)，但是這些技術在建構用在其他較簡單的任務的CNN模型上也是大有助益。整體來說，無論是在學術意義上，或是在實用程度上，這些技術都有非常卓越的表現，因此趁著記憶仍熟悉的情況，撰文紀錄看完這些技術的一些感想跟思考。

必須要說的是，由於很多技術在網路上都已經可以找到很好的解說，他們比較著重在論內容與實作步驟的逐一交代，所以這篇文章更偏向消化理解各項技術，然後討論模型改善的原因、被使用在yolov4的部分、以及在CNN或物件辨識發展脈絡下的重要貢獻。

### 架構

由於yolov4作者很明確地將物件辨識模型結構勾勒出來，在其文本中將其分為Backbone、Neck與Head，其中Backbone與Head在yolov1就已經有很明確的使用，Neck結構則是yolov3才開始使用。

Backbone主要透過大量的圖片分類資料訓練電腦理解一般圖片的知識，由於標記難度的因素，影像分類的資料集資資料量通常比物件辨識資料集較大，因此透過這樣預訓練的方式，提供電腦理解人類辨識圖便的基礎知識。Backbone的部分在yolov1(2016年)就已經很明確，除了yolov4有創造出CSPNet之外，yolov1~yolov3大都是簡單調整ResNet的結構以符合物件偵測的需求。

Head則負責將Backbone萃取出的特徵，重新畫成幾個固定大小的網格(grid)，如64x64、32x32或是16x16，再預測每個網個裡面出現物件中心的機率、anchor大小、位置以及類別。Head的部分，在yolov1~yolov4每個模型都有持續做修正，但都不是非常大的變動，無論是anchor的有無、anchor數的多少、anchor大小、norm的方式、初始值的設定、標記物件指派答案的方式或是網格大小的變化，都不斷地往更細節的部分進行修正。

最後，在yolov3開始出現使用的Neck的部分，起初主要是想改善影像不同解析度的預測偏差的問題。在yolov2的時候，透過每10 epoch塞入不同大小的影像，以解決影像解析度的問題，這個部分剛看到時覺得非常有趣，CNN竟然可以在模型架構不做更動的情況下，接受不同大小的圖像input size。到了v3的時候，透過結合SPP(Spatial Pyramid Poolinh)以及FPN(Feature Pyramid Network)的結構，在不同深度的卷積層(convolutional layer)做預測，由於CNN結構經常使用Max Pooling，而經過不同次數Max Pooling層的feature map基本上也就代表著不同解析度的同一張影像，因此可以在不調整影像大小的情況下，透過一個end-to-end的模型，訓練出可以接受不同解析度影像的網絡。到了v4的時候，則引入PANet的結構，透過多一輪的up-sampling的結構，加強特徵萃取與整合的能力。

當然，作者在裡面還提及到很多上述以外的技術與觀念。技術像是Loss Function(CIOU、GIOU、DIOU)、Attention(SE、SAM)、Activate Function(Swish、Mish)、Augumentation(cutmix、mosaic)，觀念的話像是Pooling與Receptive Field的關係、輸入圖像大小預測小物件偵測率的關係、網絡結構設計與運算時間的關係。另外，台灣作者王建堯在中研院舉辦的[演講](https://www.youtube.com/watch?v=HdQqAF-rMKc)中，也提供了很多在論文中沒有提及卻超級重要的技術，像是grid的邊緣偵測不佳的問題的改善方法、或是一些關於自動優化Backbone、Head與Neck網絡結構的模型。(順帶一提，我第一次聽這演講時是完全聽不懂的狀態，我在看完這些論文後再去聽一次，整個豁然開朗，對作者的專業知識含量又多敬重幾分，總之如果對於上述提及的技術不太陌生的話，這絕對是一場收穫讓人收穫滿滿的演講。)

ps. 由於寫到一半發現，要寫的東西真的太多，所以這一篇文章主要交代yolov4的Backbone技術，後面有毅力繼續寫的話文章才會提到Head與Neck。

### Backbone

yolov4主要使用的雖然是CSPNet，但要理解CSPNet，先備技術的爬梳實在太重要。如果沒有把整個技術脈絡整理出來，光是理解模型運作，幾乎很難理解作者設計這樣結構的原因，因此以下會從ResNet(2015年)開始後介紹，這些模型幾本上涵蓋大部分作者在related works裡面所提到的模型。

至於2015年以前的模型，包括LeNet、AlexNet、VGGNet以及GoogleNet，介紹的文章已經多到不勝枚舉，我就不多話了，不過個人是看下面這篇，個人覺得寫的滿好。

[**\[機器學習 ML NOTE\] *CNN演化史*(AlexNet、VGG、Inception、ResNet)+Keras Coding**  
CNN演化史medium.com](https://medium.com/%E9%9B%9E%E9%9B%9E%E8%88%87%E5%85%94%E5%85%94%E7%9A%84%E5%B7%A5%E7%A8%8B%E4%B8%96%E7%95%8C/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92-ml-note-cnn%E6%BC%94%E5%8C%96%E5%8F%B2-alexnet-vgg-inception-resnet-keras-coding-668f74879306 "https://medium.com/%E9%9B%9E%E9%9B%9E%E8%88%87%E5%85%94%E5%85%94%E7%9A%84%E5%B7%A5%E7%A8%8B%E4%B8%96%E7%95%8C/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92-ml-note-cnn%E6%BC%94%E5%8C%96%E5%8F%B2-alexnet-vgg-inception-resnet-keras-coding-668f74879306")[](https://medium.com/%E9%9B%9E%E9%9B%9E%E8%88%87%E5%85%94%E5%85%94%E7%9A%84%E5%B7%A5%E7%A8%8B%E4%B8%96%E7%95%8C/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92-ml-note-cnn%E6%BC%94%E5%8C%96%E5%8F%B2-alexnet-vgg-inception-resnet-keras-coding-668f74879306)

#### ResNet(2015，[2015論文](https://arxiv.org/abs/1512.03385)、[2016論文](https://arxiv.org/abs/1603.05027))

ResNet全稱為Deep Residual Network，是Microsoft Research在2015年提出的模型架構，主要解決了Gradient Vanishing(exploding)與Degradation的問題，同時也引入了BottleNeck 架構降學習參數數量。**ResNet之所以會被視為圖像辨識上極度重要的發展，是因為ResNet幾乎可以讓模型在不斷加深的過程中，持續增加模型的表現效果。**

ResNet Block

ResNet的結構(上圖)其實非常好懂，就是把經過2或3層卷積層的輸出與輸入相加，以作為下層的輸入，這個相加的步驟又稱為Identity Mapping，意思把上一層輸出的特徵映射到下一層。需要注意的是這邊的相加是element-wise的相加，所以實作上padding設定為same會比較方便，可以確保相加的兩個物件可以有相同的長與寬。這樣一來，由於梯度下降的學習目標變成加上「上一層的輸出」後等於「答案」，學習目標就不再是答案本身了，而是上一層的輸出與答案之間的差距，也就是殘差。ResNet解釋論文的文章已經太多，我就不做細緻介紹。

比較有趣的是，其實論文裡面並沒有解釋，為什麼ResNet可以解決Gradient Vanishing (exploding)與Degradation的問題，2015年那篇是完全沒有解釋，2016年那篇只證明了Identity Maping做Back Propagation的時候，可以無損的傳播梯度給淺層網絡，但並沒有進一步說明，這樣無損的傳播梯度對模型的貢獻。

網路文章對於這一塊的著墨也不多，很多人喜歡用最無腦的「接近目標說」去解釋，就是每次學習答案跟前一層的誤差(Residual)就會越來接近目標。但這其實有個大問題，就是減掉誤差後學習目標如果從正的變得負的，在不同的卷積層間學習目標就會在正負之間擺盪，因此越來接近目標這一說，其實並無法正確的解釋模型的表現。因此，以下整理兩個我比較可以接受的解釋。

1.  Weight Initialization說: 上面的接近目標說，如果再進一步修正一下解釋，其實就會合理很多了。就是每次學習跟前一層的誤差(Residual)，雖然不一定每次都會讓誤差變小，但是大多時候會比第一層的誤差小很多，再搭配「參數在初始化大都是非常接近零的值」這一特性，因此這樣的小誤差可以讓模型更新權重的時候一開始就比較貼近目標，進而提升學習效率。([來源](https://www.youtube.com/watch?v=Bu9A_-M5OZk&list=LLrM7AiR1E68n7cK2dQzhpAw))
2.  Ensemble說: 基於2016年論文對於ResNet可以無損的傳播梯度給淺層網絡的證明，Ensemble說進一步說明，這樣的特性讓模型在更新每一層CNN權重時，永遠可以選擇保有上一層的特徵，這麼一來模型便在每一層便可以做兩個選擇，改變或是不改變上一層特徵，擴張了整個架構的彈性。而將這樣的選擇放入模型的每一層並視覺化後，便產出了下面這一張決策流程圖。([來源](https://blog.csdn.net/malefactor/article/details/67637785))

![](/images/posts/20210210_yolov4_backbone/df61bad0-cb64-42d7-ae4c-b98d4e9563bb.png)

Ensemble說視覺化

另外值得一提的是ResNet裡面使用的Bottleneck架構，由於ResNet成功讓模型可以被大大加深，參數與運算效率的議題又重新被納入考量，因此ResNet同時建議在超過50層的神經網絡引入Bottleneck架構。Bottleneck架構基本上就是在3x3的卷積層前後塞入1x1的卷積層，並藉此減少參數量以提升訓練效能，詳細的餐數量計算可以參考下圖([來源](https://zhuanlan.zhihu.com/p/28413039))。

**比較重要的是，由於yolov4裡面最後選擇使用的是基於darknet53網絡的CSPNet，而darknet53是基於ResNet開發出來的網絡，所以裡面也大量使用到Bottleneck架構。另外，後面大多的深度網絡為了節省參數量也都有使用到這個技巧，因此若要弄懂yolov4 backbone的技術架構，Bottleneck中1x1的**卷積**層的重要性是不能被忽略的。**

![](/images/posts/20210210_yolov4_backbone/a383c978-1219-4a29-b865-66dbb91b6f9d.png)

**Bottleneck架構**

#### ResNext(2017，[論文](https://arxiv.org/abs/1512.03385))

ResNext是Facebook AI在2017年提出的模型架構，主要引入了GoogLeNet中Inception Module使用的split-transform-merge技巧(如下圖)。

![](/images/posts/20210210_yolov4_backbone/8af3d751-ece0-4271-8414-79439b084973.png)

Inception Module

將原本ResNet中的residual block(下圖左)改成透過多個卷積通道(Path，也稱branch、cardinality或group)疊合(concatenate)的block(下圖右)，增加模型的學習能力。而這樣的通道亦被作者從新定義為一般卷積層在設定時的一個參數Cardinality。**ResNext也是CNN領域中重要的發展，ResNext讓模型大小的比較從只有深度，轉移到深度與寬度。**

![](/images/posts/20210210_yolov4_backbone/38ebe7d9-16dd-4364-90e0-07cd644540ff.png)

ResNext網絡架構

上圖右示意了一個ResNext模塊(block)，其保留了ResNet中的Identity Mapping，並增加了Cardinality的設計。上圖中每個長方形層裡面的數字代表input channels, filter size, output channels，也就是說每一個通道會:

1.  透過4個1x1x256 filter的卷積層，把feature maps下降到4個channel
2.  透過4個3x3x4 filter的卷積層，進行特徵萃取
3.  最後經過256個1x1x4 filter的卷積層，把feature maps調整到輸出所需要的channel數

最後，再將每個path的輸出結果加在一起。比較需要注意的是，這邊(下圖a)是element-wise的相加，不是concatenation。

![](/images/posts/20210210_yolov4_backbone/9621d9af-4203-476d-afad-3f951074a8d5.png)

ResNext網絡架構實作

實作上，為了方便程式撰寫，在實作意義不改變的情況下，作者稍微轉化了上述架構，如上圖:

1.  (a) 就是上上圖右的原圖
2.  (b) 則參考Inception的實作方法，將每個通道中的第三層卷積層拿掉，並直接將每一通道中的4個channel的feature map疊合(concatenate)在一起，便成為一個128channel的feature map，最後通過256個1x1x128 filter的卷積層，把feature map調整到輸出所需要的channel數。由於原本在32個通道都有256個1x1x4的filter，調整後則直接對concatenate後的feature maps使用256個1x1x128的filter，因此實作意義並沒有發生變化。
3.  (c) 1. 將每個通道中的第一層一道通道外，透過128個1x1x256 filter的卷積層，把feature maps下降到128個channel，在通道中才將128個channel分成32個group，每個group有4個channel，讀者可以自行想像，此處的實作意義也沒有發生變化。2. 在圖片表達上，作者把concatenate層放入第二層，並以group表示通道數量。

比較需要注意的是，同一篇文章對這個「通道」的用詞已經因環境而不同，path、branch、cardinality或group都有出現過，不過總之都是同一個意思。

至於為什麼這樣的設計可以增加準確率，網路上的討論也不多。但我個人的猜測是，在沒有group的情況下(上上圖左)，3x3的卷積層使用的是64個3x3x64 filter，但是ResNext(上圖(c))有32個Path，每個Path使用4個3x3x4 filter。換而言之，原始的ResNet輸出的feature map中，每一個pixel是由3x3x64的filter與該pixel所在的上一層feature map位置相鄰的的3x3x64個pixel相乘相加的結果，這樣大的資訊量集成為一個pixel其實有點浪費，尤其在比較深度的網絡層當中，「特徵萃取」已經相對完整，應更強調在「特徵篩選」。因此，ResNext32個Path中使用的4個3x3x4 filter，僅將3x3x4(x2)個數字相乘相加後便產出一個新pixel，一方面在可以做特徵篩選的情況下節省了大量的參數(64x3x3x64:32x4x3x3x4=>36864:4608)，另一方面也因為參數量的下降，讓1x1的卷積層可以加深filter的深度，以提升特徵萃取的能力。

**比較重要的是，雖然ResNext並沒有被yolov4直接使用，但是在yolov4台灣作者王建堯的前一篇論文CSPNet(下面會提到)大量使用，ResNext也在結合CSPNet後也有被放入yolov4 backbone的待選清單當中，但因為yolov4不僅講求表現效果，同時也講求速度，所以最終並沒有被採用。**

#### DenseNet(2018，[論文](https://arxiv.org/abs/1608.06993))

DenseNet基本上就是把ResNet的Identity Mapping概念推到極致的架構。作者的出發點是，既然梯度在不同layer間傳播會有損失，那就把先前出現過的每一layer都當成下一層的輸入，這樣就能夠確保中間每一layer的梯度都能被傳播到當前的layer。

不過，在看下一篇要介紹的論文SparseNet時，其作者又進一步解釋了DenseNet表現優異的原因。由於越深的卷積層可以萃取越高階的特徵，因此把多層的卷積層輸出為下一層卷積層的輸入，有助於充分利用不同尺度(解析度)的特徵，以利下一個卷積層判讀。

前一陣子，聽了一位認知神經科學教授[謝伯讓](https://www.facebook.com/pojanghsieh)受訪的podcast，提到其實人類在判讀一些事情的時候，腦袋也會為了快速計算而建立捷徑，被稱為捷思，個人覺得與這接些架構中的shortcut設計有異曲同工之妙，以下節錄一小段這位教授的文章:

> 捷思是一種大腦為了求快而建立出來的計算捷徑。透過某些事先建立好的預設，大腦可以節省許多資源，例如，大腦預設人臉一定是凸出來的，而不可能是凹進去的。另外，大腦也預設了週遭物體本身的顏色通常不會任意改變（會改變的通常是光源的明暗和顏色）。這些捷思之所以會成為捷思，是因為上述這些事物的特質（例如人臉的凸出性）在「大部份」的狀態下都是恆定的，因此在演化的過程中，它們已經被寫入了大腦的預設值之中。

> from [https://pansci.asia/archives/author/hsieh-pj](https://pansci.asia/archives/author/hsieh-pj)

以下這個影片可以讓大家放鬆一下，看看人類腦袋中的捷思是如何運作的:

{{< youtube ORoTCBrCKIQ >}}

在實做上，DenseNet 架構中，作者總共使用4個Dense block，這四個Dense block被 transition layer連接在一起，如下圖所示。

![](/images/posts/20210210_yolov4_backbone/40a90ce0-8620-4969-b7d9-58563ae9fc69.png)

**每一個Dense block中，每一卷積層的輸入是前面所有卷積層的疊加(concatenation)，**換而言之，如果最原始的input是c的channel且每一個捲積層的輸出都是是k個channel，那麼block中第一個(紅色)捲積層輸入就是c個channel、block中第二個(綠色)捲積層輸入就是c+k x l個channel，而第三個(紫色)捲積層輸入就是c+k x 2個channel。因為每往後一層input的channel數就會增加k，因此作者又把k命名為growth rate，下圖就是一個完整的Dense Block。與ResNet不一樣的地方是，ResNet使用的是element-wise addition的方式做Identity Mapping，DenseNet則使用concatenation。

![](/images/posts/20210210_yolov4_backbone/e1e8bd69-2127-4774-9c07-7f5271de46bc.png)

Dense Block示意圖

在看這一篇論文時，有出現一個比較需要注意的詞彙 — **transition layer，主要就是由BatchNorm層、1x1的卷積層以及AvgPooling層所組成**，連接在Dense Block之間，由於這個技巧在CNN領域已經非常普及，因此直接使用 transition layer以加速討埨**，**如上圖所示。由於後面論文亦會提及這個詞彙，在此稍作解釋。

整體而言，DenseNet基本上證明了，ResNet的Path仍不足以完全解決梯度消失的問題，更多的Path還是能夠讓模型更直接的看到前面layer的輸出，並使整體表現變的更好。

#### SparseNet(2018，[論文](https://arxiv.org/abs/1804.05340))

SparseNet是DenseNet的修正版本，畢竟把前面所有卷積層的疊加起來做為下一層的輸入太過極端，一方面一層一層之間損失的資訊量沒那麼大，真的沒有必要讓每一層的從新計算過去每一層與正確答案之間的關聯性。另一面，這麼做對運算效能也會產生極大的壓力。因此，SparseNet的作者便開始想方設法，讓DenseNet可以在保留足夠Path的狀況下，減少模型的計算負擔。

![](/images/posts/20210210_yolov4_backbone/8874ad1d-dd99-4fe7-8479-496c66c575d6.png)

實作上，SparseNet採用僅疊加(concat)最靠近跟最遠的的n/2個layer的輸出，如上圖假設n=4的話，那麼當前這一層的捲積層僅使用最靠近及最遠的2層的疊加結果。另外，作者在attention上也有著墨，但並非這篇文章的重點，就不多提了。

#### CSPNet(2019, [論文](https://arxiv.org/pdf/1911.11929.pdf))

Cross Stage Partial Network (CSPNet)則是Yolov4主要作者之一中研院院士王建堯，在融會貫通上述的Backbone技術後，所發展出來的新技術。發展CSPNet的初衷是為了節省運算資源，手段則是取得較效率的梯度傳遞效果(achieve a richer gradient combination while reducing the amount of computation)。

由於作者重新思考過，ResNext中使用到GooLeNet Inception Module不同捲積通道(Path)傳遞梯度的意義，以及後續DenseNet與SparseNet經過過度修正過程，也就是將梯度傳遞精神推到極致後又修正回來的過程，於是重新組合了更效率的梯度傳遞通道組合，發展出了CSPNet。

以DenseNet搭配CSP的技術為例，由於DenseNet的運算量很大，每一層的input是前面所有捲積層output的疊合(concatenate)，若能將起初input的channel下降一半，便可大大下降GPU記憶體的捲積流量(CIO)與記憶體運輸量(memory traffic)。舉例來說，假設DenseNet的input是w × h × c，成長率(growth rate，也就是每一層輸出的channel數)是d，且總共有m個dense layers。那麼原始的DenseNet(下圖a)運算流量是(c × m) + ((m² + m) × d)/2，其中c × m是指原始input的c個channel要流過m層dense layer，(m² + m) × d)/2中，m(m+1)/2是指1加到m的總和，d則是每一層輸出的channel數。CSPDenseNet(下圖b)的運算流量則是(c × m)/2 + ((m² + m) × d)/2，其中c通常比m跟d大很多，因此至少可以減少一半的流量。

![](/images/posts/20210210_yolov4_backbone/28a597c9-9f3a-4dc8-9dbd-703c412f420a.png)

在結構上，Base layer會被切分成part1與part2，個別擁有Base layer中channel數的1/2，part2經過Dense Block與Transition layer後直接與Part1疊合(concatenate)在一起，論文中還有討論到截斷(truncating)重複傳遞梯度的好處，以及透過調整transition layer的位置來實踐的方式，不過在yolov4跟後面模型的實作上提及不多，這邊就不多做介紹了。

使用上，CSPNet可以跟不同的Backbone架構結合。在原始論文中有被比較的就有CSPResNet、CSPResNext、CSPDarknet…等等。而在yolov4的論文中，作者比較了CSPResNext50與為了物件偵測設計的CSPdarknet53後，發現雖然CSPResNext的Receptive Field較大(見下圖，Hypothetically speaking, we can assume that a model with a larger receptive field size and a larger number of parameters should be selected as the backbone.)，但是從AP來看，在總體表現上成長性卻不如CSPdarknet53(We observe that the CSPDarknet53 model demonstrates a greater ability to increase the detector accuracy owing to various improvements.)。

![](/images/posts/20210210_yolov4_backbone/7e07ea0b-b24a-4627-8ed9-cf583c2e1454.png)

![](/images/posts/20210210_yolov4_backbone/f4083861-bb9c-4537-9b4a-54a6b1dfd1ef.png)

在結論上，CSPNet並不若ResNet、ResNext在理論上開創CNN模型新的發展方向，但其實用價值卻是極高的，作者在消化理解過去各個重要模型上確實花了功夫，也成功找到突破點，在不降低模型表現的基礎上，提供了模型更效率的梯度學習進程。
