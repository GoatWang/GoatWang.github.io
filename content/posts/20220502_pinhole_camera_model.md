---
title: Pinhole Camera Model理論與實務
date: '2022-05-02T03:49:55+00:00'
draft: false
categories:
- Computer Vision
summary: 前言 去年開始接觸攝影測量，發現攝影機可以進行精準的三維量測與建模覺得驚為天人，雖然網路上對於理論講解的文章非常多，但把理論應用於實務問題的文章卻屈指可數，偏偏這個領域理論與實務可以說是天讓之別，主要是因為攝影測量精準程度極高，每一像素可以測量的精準程度可以到μm等級，因此需要透過非常多複雜的校正算法來彌補理論與實務的落差，同時理論在實踐時亦牽涉到硬體規格的選擇、參數之對照甚至是校正取像的技巧。
  ...
cover:
  image: /images/posts/20220502_pinhole_camera_model/b9f4bd2e-649c-4bde-8f08-7272012c6ebe.gif
---

### 前言

去年開始接觸攝影測量，發現攝影機可以進行精準的三維量測與建模覺得驚為天人，雖然網路上對於理論講解的文章非常多，但把理論應用於實務問題的文章卻屈指可數，偏偏這個領域理論與實務可以說是天讓之別，主要是因為攝影測量精準程度極高，每一像素可以測量的精準程度可以到μm等級，因此需要透過非常多複雜的校正算法來彌補理論與實務的落差，同時理論在實踐時亦牽涉到硬體規格的選擇、參數之對照甚至是校正取像的技巧。

整體而言，在專家指導下自己也花了至少一年的時間才能比較全面地理解攝影測量的基礎概念，若各位自行嘗試不但須耗費時間，更需資金測試不同的相機、鏡頭甚至是支架。因此非常希望把這個過程有系統的記錄下與各位分享，幫助降低攝影測量之進入門檻。

### 本文架構

本篇文章會先說明Pinhole Camera Model的目的與意義，接著會定義Model中所需要的參數(畸變參數、內方位參數與外方位參數)，並說明時物應用中所需的硬體設置(感光元件與鏡頭)，然後說明Model本身的計算流程(**世界**座標系統、**相機**座標系統與**相片**座標系統)，最後提供Model的Python+OpenCV範例程式。本篇文章雖會提及畸變參數、內方位參數與外方位參數的取得，但僅會說明其邏輯與實作，並不會涉及細部的校正演算法，同時亦不會提及雙目或多目相機的三維量測與建模，但必須說明的是，Pinhole Camera Model絕對是進入攝影測量領域最重要的先備知識。

### Pinhole Camera Model的目的與意義

目的上來說，Pinhole Camera Model主要提供了相片中每一像素與像素中物件真實位置的轉換關係，這樣的轉換可以被廣泛應用在各個相關聯的領域，例如「測量」與「建模」、甚至更應用面的詞彙像是「元宇宙」、「虛擬實境」與「自駕車」，從產品面來說，最廣泛應用的大約是intel出的realsense以及stereo lab推出的zed，兩個產品在硬體層面、匹配算法與適用情境上略有差異，但是在算法層面都需要基於這個理論進行研發，所以Pinhole Camera Model也算是一個電腦視覺3D應用中，最基礎也最重要的演算法了。

![](/images/posts/20220502_pinhole_camera_model/d14a08de-886b-4be3-9cb9-8689647fee5d.png)

Pinhole Camera Model (from: [https://docs.opencv.org/3.4.15/d9/d0c/group\_\_calib3d.html](https://docs.opencv.org/3.4.15/d9/d0c/group__calib3d.html))

如上圖所示，Pinhole Camera Model主要解釋了2D相片座標系統與3D世界座標系統的轉換關係，2D與3D的轉換上可以分為兩個方向的轉換(2D=&gt;3D及3D=&gt;2D)。由於3D空間的點(XYZ)富含的資訊量比較2D(XY)相片大，若要把2D相片上的點投影至3D空間中，需要兩張以上不一樣角度拍攝的相片，才能把2D相片中的點投影至3D空間中，並定位其在3D空間中的位置。若要從3D空間中的點投影至2D相片上，由於是一個降低維度的運作，一張相片即可完成。因此，為了方便理解，Pinhole Camera Model一般是將已知的3D空間座標點投影到相片上，並計算其在相片上的像素位置。

當然，隨著時代的進步，感光元件與鏡頭的種類也越來越多元，並不是所有相機都可以直接透過Pinhole Camera Model進行解構，例如魚眼鏡頭，其觀測的角度很多時候已經超過180度，可以想像成人的眼睛可以看到後腦杓的物件，Pinhole Camera Model卻只能處理180度以內的投影，因此並無法直接適用於這類相機，這時可能就必須尋找其他Camera Model來解決問題，如Fisheye Camera Model。也有一些類型的相機是需要經過**特殊校正方法**處理後才能套用Pinhole Camera Model，例如rolling shuttle的相機，因為這種相機是一行(row)一行進行取像地，若是在行進中取像，可能會導致同一張影像中的每行(row)會有平移的現象，這種就需要透過特殊的校正方式處理後，方能使用Pinhole Camera Model。

不過總體而言，除非有特殊需求，Pinhole Camera Model仍是2D相片與3D空間轉換上最基礎也最常用的模型。

### 參數設定與解釋

![](/images/posts/20220502_pinhole_camera_model/38a5a8e1-2150-48c8-b33c-502a0a1489d8.png)

Pinhole Camera Model (from: [https://docs.opencv.org/3.4.15/d9/d0c/group\_\_calib3d.html](https://docs.opencv.org/3.4.15/d9/d0c/group__calib3d.html))

以下簡要說明Pinhole Camera Model所需的已知參數，如上圖所示，距離相機(O點)較遠的紅色P點(下面成為Pw)代表的是世界座標系統的物點，位於相片上的紅色P點(下面成為Pi)則代表Pw點被投影到相片上時，在相片座標系統上的像素座標點。其中，O代表相機中心(實質上是透鏡中心)，F代表相片中心，F與O的距離稱為焦距(Focal Length)。

![](/images/posts/20220502_pinhole_camera_model/939d287d-9650-4ada-b5d9-3a035b0bbff0.png)

Pinhole Camera Model

上式即是Pinhole Camera Model，可以用來計算3D物點投影到相片上的像素點，要完成這樣的投影轉換主要需取得畸變參數(Distortion Coefficients，沒有出現上面的圖片或式子中)、內方位參數(Intrinsic Parameters)、外方位參數(Extrinsic Parameters)與物點的世界空間座標(World Coordinate)，以下逐一介紹:

#### 一、畸變參數

主要用來表示弧面相機鏡頭所導致相片邊緣的像素扭曲的情況，主要有下圖中兩種類型的畸變。上面的圖片或式子中沒有顯示相關的參數，主要是因為他們假設畸變已經被校正，但是這仍然是不能被忽略的步驟，不過簡單的畸變校正可以用[OpenCV](https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html)來完成，本文最後一位提供Python與OpenCV的程式碼，校正算法跟參數結構這裡就不說明了。

![](/images/posts/20220502_pinhole_camera_model/b4162370-040f-457e-9ba5-ca3abaf0a4e9.png)

Distortion Types

#### 二、內方位參數

內方位參數就是相機本身的既定參數，一旦選好相機(感光元件與鏡頭)後，這些參數也就決定好了，並有以下參數:

1. f: 焦距(Focal Length)，亦即相機中心到感光元件(CCD)之間的距離，**在硬體頁面顯示上一般是以mm為單位，但在openCV的設定中是以像素為單位，在後面應用中需注意單位轉換，此外因為感光元件XY軸的像素大小(Pixel Size)，也就是每一像素暫實際空間的大小未必相同，因此若f換算為像素單位，XY軸的值也可能不同。**
    
2. px, py: Pixel Size，width of CCD size / columns, height of CCD size / rows，也就是感光元件上每一像素在實際空間中的大小。
    
3. n\_rows, n\_col: 相片的像素解析度 e.g. 1920 x 1080的相片n\_rows是1080且n\_cols是1920。
    

需別提醒的是，**要拿來做測量的相機務必是定焦相機**，焦距的變動亦會影響到其他參數如**畸變參數**與**內方位參數**，如此便無法進行量測。因此，在開始相關專案時必須確保使用的相機是定焦的鏡頭，並可以查得相機所使用的感光元件大小與像素大小。以Lucid工業相機為例，這邊隨機挑選了一台[五百萬畫素的相機](https://thinklucid.com/product/triton-5-mp-imx264/)與[4mm焦距的鏡頭](https://thinklucid.com/product/edmund-optics-c-mount-1-2-4-mm-f-1-8/)。相機的規格如下圖，Sensor Size代表的是整個感光元件的大小，有些地方會用CCD Size表示，11.1mm代表的是感光元件對角線的長度。Pixel Size代表每一個像素的實際大小。一般來說，Sensor Size的長與寬除以像素的數量約會等於Pixel Size。

![](/images/posts/20220502_pinhole_camera_model/2c20346d-a855-4c9f-8f89-7a676d693474.png)

鏡頭的規格如下，Focal Length代表感光元件到透鏡中心的垂直距離。

![](/images/posts/20220502_pinhole_camera_model/3456af50-1a18-4240-9f9e-53466e204c13.png)

從下圖可以得知，透鏡、感光元件與焦距的相對關係。

![](/images/posts/20220502_pinhole_camera_model/2058bfff-6cac-4a83-8b00-a6513fa9e599.gif)

Relation of focal\_length, ccd\_size and lens (from: [http://www.wescomponents.com/datasheets/dvr/CCD\_Focal\_Length\_Calculator.htm](http://www.wescomponents.com/datasheets/dvr/CCD_Focal_Length_Calculator.htm))

需特別提醒的是，因為物件經過透鏡在感光元件上成像時會有上下左右顛倒的現象，為了方便計算，以下會假定感光元件介於透鏡與物件之間，如下圖Image plane位置所示。如此一來，便可以如同本文第一張圖片所示(順序: 透鏡中心=&gt;感光元件=&gt;物件)進行計算了。

![](/images/posts/20220502_pinhole_camera_model/ea7dfb72-881a-4d9e-972d-fccbc8356a4a.png)

#### 三、外方位參數

![](/images/posts/20220502_pinhole_camera_model/6ec7bfa6-263a-411e-acdc-7649f653b4b2.png)

Pinhole Camera Model

世界空間座標系統與相機座標系統的起始座標位移量(offset)與XYZ軸角度差，一般來說習慣用公式換算出一個3x4的矩陣來表達，也就是上式中的外部參數矩陣，如果是使用OpenCV進行校正，OpenCV會直接提供這個個3x4的矩陣，也就可以直接應用在上式中，但是如果要整合其他硬體資料則需要了解一下，這個矩陣的組成與意義，主要需要了解「位移量」與「角度差」兩個概念，通常做以下表示:

1. ω, φ, κ or roll, yaw, pitch: 旋轉座標系統，相機xyz軸相對於世界空間座標的旋轉角。可以透過公式轉換為3x3的旋轉矩陣，此參數可以透過。
    
2. t1, t2, t3: Translation。在相機座標系統中，相機中心所在位置與世界座標系統的原點的位移(Offset)。
    

在旋轉角度差的表達上，主流有兩種不同的座標轉換系統，omega, phi, kappa系統以及roll, yaw, pitch系統，兩種系統只是表示方式的不同並可以互相轉換，已經有很多文章介紹兩者的定義與差異，這邊就不贅述了。

比較重要的是需要知道如何透過XYZ軸角度差，計算出轉換兩座標系統(世界and相機)的**旋轉矩陣**以方便Pinhole Camera Model的應用。以omega, phi, kappa系統為例，下面是將其轉換為旋轉矩陣的公式，其中omega, phi, kappa分別是XYZ軸的角度差，經過下面公式轉換後可以得到相應的旋轉矩陣，有線性代數座標系統轉換的基礎便很好理解其中意義，不過在這邊沒有相關基礎亦可以直接操作。

![](/images/posts/20220502_pinhole_camera_model/66d556db-f22b-4730-8166-4590bd1b57c5.png)

另外一個疑惑會是，如何取得omega, phi, kappa參數。實務上來說，若要真正得知跟**相機**跟**世界**座標系統的轉換非常困難，就算使用校正方法計算出來，相機一旦移動便要重新校正，若要在移動仍要維持轉換矩陣可以運作，就必續配備非常高規格的GPS與IMU(慣性導航儀)，或是透過其他軟體方法計算不同時間點相片的位移量(e.g. SLAM)，但這些設備或算法的取得、設定與使用都很仰賴知識與經驗，建議小心入坑。

實際應用中，如果並不在意物件在世界座標系統中的位置，只需要取得同一物件的3D資訊，那麼透過兩台相機相對位置的校正便可達成目的，因此，**旋轉矩陣**在Pinhole Camera Model中雖然是世界空間座標系統與相機座標系統的轉換矩陣，但在實務應用上，常常應用在兩感測器(e.g. 兩台相機)座標系統的轉換。以兩台相機為例，**旋轉矩陣**便可以透過OpenCV與[校正板](https://markhedleyjones.com/projects/calibration-checkerboard-collection)事先校正得知，後面會提供程式碼。

#### 四、物點在世界空間座標的位置

在使用情境下，物點一般是需要透過測量而得知的座標點，僅有在校正畸變參數、內方位參數或外方位參數時，可以事先取得[校正板](https://markhedleyjones.com/projects/calibration-checkerboard-collection)上面已經定義好的座標點位置。不過如果前面目的段落的敘述，為了讓我們快速了解Pinhole Camera Model，先從3D物點投影至2D相片所需要的資訊量較少，硬體設置也較簡單，就先假設3D物點在世界空間座標的位置是已知的。

### Pinhole Camera Model計算流程

接下來要介紹本篇文章的主題Pinhole Camera Model本身。上面已經說明，Pinhole Camera Model一般是將已知的3D空間座標點投影到相片上，並計算其在相片上的像素位置。明確來說，就是在已知上面參數的情況下，計算物點P(Xw, Yw, Zw)投影在相片上的像素點索引值(u, v)。在這段轉換的過程中需經過，三個不同的座標系統:

1. *世界空間座標*: 就是下圖中的World Coordinate System，世界空間座標可以是相對的亦可以是絕對的，相對的世界空間座標可以計算物點在某一特定坐標系(另一相機的坐標系、Lidar的坐標系或是IMU的坐標系)的位置與旋轉角；絕對的世界空間座標即是指經緯度座標或是其他二度分帶投影座標(如台灣使用的TWD97座標)。
    
2. *相機空間座標:* 就是下圖中的Camera Coordinate System，是以mm為單位、以相機的中心點(O點)為原點，以感光元件(藍色畫布)的x軸(綠色x軸)為X軸，以感光元件的y軸(綠色y軸)為Y軸，並以相機中心到感光元件垂直線(OF線段)為Z軸。
    
3. *相片平面座標:* 就是下圖Imaeg Coordinate System，也就是感光元件所在的位置，因為相片是一個2D平面，僅有X軸與Y軸，其以像素為單位，相片由左到右為X軸、由上到下為Y軸。這裡須注意，這裡的XY軸比較像是OpenCV的設定，OpenCV的第一的維度是橫向的Column、第二個維度是直向的Row，Numpy的第一的維度是直向的Row、第二個維度是橫向的Column。  
    整體來說，*相片平面座標*與*相機空間座標*有三個最重要的差異。一、維度: *相機空間座標*是三個維度的空間座標；*相片平面座標*是二個維度的平面座標。二、起始點: *相機空間座標*的XY軸原點在相片的正中心；*相片平面座標*的XY軸原點在相片的左上角。三、單位: *相機空間座標*的單位是mm；*相片平面座標*的單位是像素。
    

![](/images/posts/20220502_pinhole_camera_model/f9b3a02c-2cd7-400a-8825-2173bb3cec06.png)

Pinhole Camera Model (from: [https://docs.opencv.org/3.4.15/d9/d0c/group\_\_calib3d.html](https://docs.opencv.org/3.4.15/d9/d0c/group__calib3d.html))

整個Pinhole Camera Mode需經過以下三個流程:

1. 把P點*世界空間座標*(Xw, Yw, Zw)轉換成*相機空間座標*(Xc, Yc, Zc)。
    
2. 把物點P(最左上的紅色箭頭P點)投影至透過相似三角形計算的轉換投影至相片上(相片上的紅色箭頭P點)，並將單位從mm轉換為像素。
    
3. 把*相機空間座標*中P點的座標(uc, vc, f)轉換為*相片座標*(u, v)
    

#### 一、把P點世界空間座標(Xw, Yw, Zw)轉換成相片空間座標(Xc, Yc, Zc)

![](/images/posts/20220502_pinhole_camera_model/551d3e6b-6868-4e04-9978-d3fc26858c2f.png)

從上式來看，紅色框框內的計算就是將世界空間座標(Xw, Yw, Zw)轉換成相機空間座標(Xc, Yc, Zc)，詳細的來說，又分為旋轉角的轉換(R)與位移(T)，R是一個3x3的矩陣，實際意義則記錄了XYZ軸旋轉的角度，T的部分則是在相機空見座標系統中，相機空間座標中心與世界空間座標中心的位移量，所以將物點透過R轉換到相機空間後，再加上T位移，便可得到誤點在相機座標系統的位置，也就是下式中的(Xc, Yc, Zc)。

還是在強調一次，這部份如果無法理解，可以去研究線性代數的Change of Basis，不過如果沒有相關基礎，這部分會需要一段時間去理解，此處可以先以應用為主。

![](/images/posts/20220502_pinhole_camera_model/96db9735-c0ea-4e32-8868-eda160f1df0a.png)

#### 二、把物點P(最左上的紅色箭頭P點)投影至透過相似三角形計算的轉換投影至相片上(相片上的紅色箭頭P點)，並將單位從mm轉換為像素

![](/images/posts/20220502_pinhole_camera_model/46ac52a3-11d5-4472-be2b-34a76ef4aaa9.png)

Pinhole Camera Model (from: [https://docs.opencv.org/3.4.15/d9/d0c/group\_\_calib3d.html](https://docs.opencv.org/3.4.15/d9/d0c/group__calib3d.html))

上圖中紫色的線段可以組成兩個三角形，並互為相似三角形。由於上一步驟的計算，已知P點在*相機空間座標*為(Xc, Yc, Zc)，透過相似三角形的計算可以得知其在*相機空間座標*中P點投影至相片上的位置(uc, vc, f)，此處的Z軸必定是焦距(focal length，上圖中的F)，因為是在*相機空間座標*中，所以uc與vc中的c是Camera的縮寫。

我們把相似三角形投影在XZ平面上的相似三角形解剖來看可以得到下圖，P點在*相機空間座標*中X軸座標為Xc、Y軸座標為Yc，其投影在相片上的Z軸座標為f，那麼X軸座標就會等於(fx/Zc)\*Xc。如果套用在YZ平面上面即可以得到，Y軸座標等於(fy/Zc)\*Yc。下面最右下式將其改寫為矩陣相乘的形式，不過得到的結果會是一致的。

**這邊須注意，在openCV的設定中，fx, fy的單位是像素，所以uc跟vc的單位已經被轉換為像素(而不是mm)。**

![](/images/posts/20220502_pinhole_camera_model/9d0ed1bd-830b-4891-8d7e-777847770bd4.png)

#### 三、把*相機空間座標*中P點的座標(uc, vc, f)轉換為*相片座標*(u, v)

![](/images/posts/20220502_pinhole_camera_model/a0ae1ada-6526-45aa-9d3c-1c465e95af01.png)

前面有提到，*相片平面座標*與*相機空間座標*有三個最重要的差異: **維度**、**起始點**與\*\*單位。\*\*維度部份把Z軸的值拿掉即可，單位部分在上一步驟已經轉換完成，因此在這個階段，只需要把起始點從相片的正中心移動到相片的左上角，也就是加上相片正中心的像素值(cx, cy)即可完成。舉例而言，假設相片長寬是128\*128，uc, vc = (0, 0)，那麼u, v = (64, 64)。

![](/images/posts/20220502_pinhole_camera_model/95f3222f-4acb-48b3-8111-58abc437c2c2.png)

最後我們再回過頭來看原式，等號的左手邊u, v旁邊還乘一個s，等號右手邊乘開來X軸會等於fx\*Xc+0+cx\*Zc、Y軸會等於0+fy\*Yc+cy\*Zc、Z軸會等於Zc，但左手邊我們需取得的Z軸是1，所以將XYZ軸全部除以Zc，便可成功建立等號。

### 相機的內外方位校正程式

可以參考我的[Github Repo CamCalibration](https://github.com/GoatWang/CamCalibration)，裡面有提供測試用的圖片，clone下來就可以直接跑，主要是透過校正板與OpenCV，計算出相機的畸變參數、內方位參數與外方位參數，並將每一張相片所在的位置與旋轉角畫出來。

```bash
# git clone https://github.com/GoatWang/CamCalibration
# change directory to CamCalibration
# pip install -r requirements.txt

# 取得畸變參數、內方位參數與外方位參數
> python intrinsic.py
...
...
fx, fy 5.971613716038594 5.947925373788673
w_mv, h_mv -0.18810492107689925 1.2861034491316445
calibrated
fx, fy 5.780574817681404 5.757644293170961
w_mv, h_mv -0.5 -0.5

# 劃出每一張相片所在的位置
> python intrinsic_eval.py
```

![](/images/posts/20220502_pinhole_camera_model/6fa2449a-4efe-4278-99e7-95fe6da2c142.webp)

之後我們便可以得到上面這一張圖，圖中最上面那個很整齊的便是校正板的棋盤格點(見下圖)，下面每一個紅點就是一張相片拍攝時相機所在的位置，位在相機前面一點點的平面是為了表示相機的旋轉角，並不是感光元件實際所在的位置，因為感光元件實際所在的位置會太靠近相機中心，幾乎就是黏再一起，這樣會無法辨識相機拍攝的旋轉角。

![](/images/posts/20220502_pinhole_camera_model/87ab2c99-6c5a-44da-b4ec-397ad6bdcef5.png)
