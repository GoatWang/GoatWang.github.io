---
title: 'TronGisPy: GIS網格資料處理工具'
date: '2021-07-24T09:28:18+00:00'
draft: false
categories:
- Tools & DevOps
summary: TronGisPy 簡介TronGisPy TronGisPy是基於Python語言，並以GDAL為底層進行開發的GIS影像自動化處理開源套件，同時也提供機器學習前處裡與後處理的重要功能。為了加速資料處理的開發速度與建置GIS自動化流程，TronGisPy簡化了GDAL的介面，並提供各式方便的Python介面，以利工程師快速開發出有價值且可自動化的應用。由於TronGisPy的所有函式幾乎是基於解...
cover:
  image: /images/posts/20210724_trongispy_gis_tool/90997739-4972-4d8b-b05b-4cbd5a853803.png
---

![](/images/posts/20210724_trongispy_gis_tool/f9fc6480-62c0-464b-bca3-1a5f7fc9e87e.png)

TronGisPy

### 簡介TronGisPy

TronGisPy是基於Python語言，並以GDAL為底層進行開發的GIS影像自動化處理開源套件，同時也提供機器學習前處裡與後處理的重要功能。為了加速資料處理的開發速度與建置GIS自動化流程，TronGisPy簡化了GDAL的介面，並提供各式方便的Python介面，以利工程師快速開發出有價值且可自動化的應用。由於TronGisPy的所有函式幾乎是基於解決實際問題而進行開發的，且已經至少十個大小不同的專案，因此應該已經可以滿足大部分GIS專案的需求。本篇文章主要在介紹TronGisPy起源、模組、安裝方法以及基礎的GIS影像觀念，應用方式及程式碼會在後面文章陸續介紹。

### 模組簡介

主要含有以下模組:

*   **Raster**: 儲存TIF裡所有資訊的物件模組，其中資訊包含影像本身(`Raster.data`)、投影座標(`Raster.projection`)、影像位置解析度與旋轉角(`Raster.geo_transform`)，同時亦有繪圖(`Raster.plot()`)、轉投影(`Raster.reproject()`)與從新定位網格位置(`Raster.remap()`)或解析度(`Raster.refine_resolution()`)等功能。
*   **ShapeGrid**: 網格資料與向量資料的轉換功能模組。本模組可以方便地將網格資料向量化(`vectorize_layer`)、將向量資料網格化(`rasterize_layer`)，或透過已知的Raster網格將向量資料網格化(`rasterize_layer_by_ref_raster`)，或使用Polygon對網格進行切割(`clip_raster_with_polygon`)。
*   **DEMProcessor**: DEM各項因子運算的功能模組。各項因子包含坡度(`dem_to_slope`)、坡向(`dem_to_aspect`)、陰影(`dem_to_hillshade`)、粗糙度(`dem_to_roughness`)、TPI(`dem_to_TPI`)、TRI(`dem_to_TRI`)。
*   **Interpolation**: 影像補遺的功能模組。此模組可以透過反距離加權法(IDW)或像素鄰近的數值將遺漏值填上。可以選擇使用像鄰近網格的平均值(`mean_interpolation`)或是眾數(`majority_interpolation`)進行內差，亦可使用GDAL實作的反距離加權法(`gdal_fillnodata`)進行內差。其中為了加速像素鄰近網格Filter的卷機運算，相關函式皆有使用numba進行平行化運算。
*   **CRS**: 協助座標系統轉換的功能模組。經緯度座標與`numpy.array`的網格索引的轉換(`coords_to_npidxs`, `npidxs_to_coords`)、投影座標格式WKT與EPSG的轉換(`epsg_to_wkt`, `wkt_to_epsg`)。
*   **Normalizer**: 像素數值規一化的物件模組。由於GIS影像感測器繁多像素數值型態有float、8bit或16bit，此模組可以協助將不同的像素數值型態進行規一化(`Normalizer.fit_transform()`)。另外，由於許GIS影像感光元件較敏感或無法確保足夠的光源，在程現時常會有亮度太暗的狀況，此時可以將像素數值中的離群值切掉(`Normalizer.clip_by_percentage()`)，以利影像呈現與觀察。
*   **SplittedImage**: 協助裁切與組合GIS影像的物件模組。由於GIS影像常常非常大張(e.g. 10000x10000像素)，如果直接放入機器學習模型，一方面資料量可能不足，另一方面也會造成記憶體與運算量的龐大負擔。因此透過`SplittedImage`物件可以把影像按照移動窗格的模式進行切割，待機器學習模型判釋完成，再將判釋結果組合(`get_combined_image`)為與原影像具有相同空間資訊的影像。
*   **TypeCast**: 協助Numpy與GDAL資料格式轉換的功能模組。主要提供GDAL資料格式轉換為Numpy資料格式的函式(`tgp.gdaldtype_to_npdtype`)，與Numpy資料格式的函式轉換為GDAL資料格式的函式(`tgp.npdtype_to_gdaldtype`)。
*   **io**: 檔案讀寫相關的功能模組。可以讀取GIS影像(`tgp.read_raster`)、取得(`tgp.get_raster_info`)及更新(`tgp.update_raster_info`)GIS影像的描述性資訊，亦有提供測試資料與使用者測試上述模組(`tgp.get_testing_fp`)。

### 安裝

由於Gis的底層套件的依賴性比較強，建議根據相應的版本進行安裝。

*   透過Docker直接安裝: `docker pull jeremy4555/trongispy:latest`，並透過`docker run -it --rm jeremy4555/trongispy:latest /bin/bash`啟動docker，或請見TronGisPy的[Dockerfile](https://github.com/thinktron/TronGisPy/blob/master/Dockerfile)。
*   Windows建議直接安裝[別人build好的套件](https://www.lfd.uci.edu/~gohlke/pythonlibs/)。
*   Linux的部分請注意GDAL必須先安裝到可以透過`gdal_info --version`取得`GDAL 3.0.4, release 2020/01/28`後，再透過pip安裝`pip install GDAL=3.0.4`(安裝GDAL的[Dockerfile](https://github.com/GoatWang/GdalDockerfile))，務必確認`gdal_info`的版本與python中的gdal版本必須一致，其餘套件則透過pip安裝即可。

GDAL==3.0.4  
Fiona==1.8.13  
Shapely==1.6.4.post2  
geopandas==0.7.0  
Rtree==0.9.4  
opencv\_python==4.1.2

接著只要透過pip便可安裝TronGisPy了。

```
pip install TronGisPy
```

### GIS影像的屬性與基本操作

一張GIS影像需要具備以下資訊: 影像數值、投影座標、起始位置、網格解析度以及旋轉角。最常見的GIS影像格式就是TIFF，裡面儲存的data就是影像數值，Projection就是投影座標，GeoTransform裡面則包含有起始位置、網格解析度以及旋轉角等資訊。而在TronGisPy中僅須透過`tgp.read_raster('<fp>')`，便可將GIS影像讀進記憶體並開始運算。以下詳細介紹Data(影像數值)、Projection(投影座標)、GeoTransofrm(起始位置、網格解析度以及旋轉角)

import TronGisPy as tgp  
img\_fp = tgp.get\_testing\_fp('aereo\_tif') # 取得測試資料的路徑  
ras = tgp.read\_raster(img\_fp) # 讀取GIS影像  
ras.plot(clip\_percentage=(0.1, 0.9)) # 把影像數值前後10%切掉增顯並畫出影像

#### Data(影像數值)

影像數值上與一般影像不同的是波段(Band)的數量以及資料型態。波段(Band)的數量，在電腦視覺領域又稱為通道(Channel)。由於遙測資料中比RGB更細緻的波段頻率切割，以及RGB以外的不可見光波段頻率，往往能針對特定的地表物件具有奇特的相關性，像是近紅外光(Near Infrared)對於觀測植披或是水體的都有許多已經非常成熟的應用方法。下圖就是透過紅光(RED)與近紅外光(NIR)計算出的植生指標(NDVI, `NDVI=(NIR-RED)/(NIR+RED))` ，對於葉綠素的感測就非常敏感，甚至能用來判是農田的健康狀況。

import TronGisPy as tgp  
fp = tgp.get\_testing\_fp('aereo\_tif') # 取得測試資料的路徑  
ras = tgp.read\_raster(fp) # 讀取GIS影像  
RED, NIR = ras.data\[:, :, 0\], ras.data\[:, :, 3\] # 取得紅光跟近紅外光  
NDVI = (NIR - RED) / (NIR + RED + 10\*\*-6) # 計算NDVI  
ras\_NDVI = ras.copy() # 複製原本GIS影像的地理資訊  
ras\_NDVI.data = NDVI # 複製將數值資料改為NDVI  
ras\_NDVI.plot(clip\_percentage=(0.1, 0.9), cmap='gray') # 把影像數值前後10%切掉增顯並畫出影像

![](/images/posts/20210724_trongispy_gis_tool/0bfbab9e-4715-4840-a1e1-6b4c660d48f2.png)

因此，許多在遙測儀器上使用不同光波段的感測器也就非常普遍，舉例來說歐洲太空總署(ESA)公開給大眾自由取用的Sentinel-2影像便有12個波段，如下圖所示。

![](/images/posts/20210724_trongispy_gis_tool/b08a91e1-89ff-4684-800c-cf8bf8304fcd.png)

Bands List in Sentinel-2

另外，GIS影像的資料型態也與一般相片不同。GIS影像的數值不一定是8bit(0~255)，有些比較精密的感測器也可能拍出16bit(0~65535)的影像，如果是經過處理的影像(非原始影像)，則有可能出現其他型別的資料，GDAL是GIS影像處理上非常重要的底層套件，裡面常見的型別就有Byte、Float32、Float64、Int16、Int32、TypeCount、UInt16、UInt32。可以透過下面程式碼取得所有GDAL內建的資料型別。

\>>> import gdal  
\>>> print(\[func for func in dir(gdal) if "GDT" in func\])  
\['GDT\_Byte', 'GDT\_CFloat32', 'GDT\_CFloat64', 'GDT\_CInt16', 'GDT\_CInt32', 'GDT\_Float32', 'GDT\_Float64', 'GDT\_Int16', 'GDT\_Int32', 'GDT\_TypeCount', 'GDT\_UInt16', 'GDT\_UInt32', 'GDT\_Unknown'\]

#### Projection(投影座標)

由於地球是一個球體，若要用平面來呈現整個世界，必然會有些區域的面積比例與實際比例不符，因此也就衍生了不同的投影方式，大致上可分為未經過投影的經緯度座標(WGS84)，也有六度分帶(UTM)以及二度分帶(TM2)投影，但這些投影方式應用在不同區域仍需選擇不同的起始位置與投影中心。因此，各國或地區亦會針對其所在位置，重新找尋投影中心，降低投影面積扭曲的狀況。不同的投影方式配上不同的起始位置與投影中心，便可重新定義新的座標系統。

而最常見的通用投影代碼是EPSG代碼，EPSG代碼是歐洲石油調查組為了讓座標系統的跨域溝通更為便利而訂立的，最常見的EPSG代碼是4326，也就是未經投影的WGS84的經緯度座標，台灣全島現行最通用的EPSG代碼是3826(也稱為TWD97)，不同地區設適用的投影亦會有自己的EPSG代碼。不過TIF檔為了增加投影座標定義的彈性，因此使用Well Known Text(WKT)，詳細的定義非常複雜，這邊就不多提了，大多時候在談論座標系統時仍是以EPSG代碼進行溝通。以下程式碼示範如何取得TIF的Projection，並使用TronGisPy轉換EPSG與WKT。

\>>> import TronGisPy as tgp  
\>>> fp = tgp.get\_testing\_fp('aereo\_tif')  # 取得測試資料的路徑  
\>>> ras = tgp.read\_raster(fp) # 讀取GIS影像  
\>>> print("Projection(WKT):", ras.projection)  # 取得投影座標WKT  
Projection(WKT): PROJCS\["TWD97 / TM2 zone 121",GEOGCS\["TWD97",DATUM\["Taiwan\_Datum\_1997",SPHEROID\["GRS 1980",6378137,298.257222101,AUTHORITY\["EPSG","7019"\]\],AUTHORITY\["EPSG","1026"\]\],PRIMEM\["Greenwich",0,AUTHORITY\["EPSG","8901"\]\],UNIT\["degree",0.0174532925199433,AUTHORITY\["EPSG","9122"\]\],AUTHORITY\["EPSG","3824"\]\],PROJECTION\["Transverse\_Mercator"\],PARAMETER\["latitude\_of\_origin",0\],PARAMETER\["central\_meridian",121\],PARAMETER\["scale\_factor",0.9999\],PARAMETER\["false\_easting",250000\],PARAMETER\["false\_northing",0\],UNIT\["metre",1,AUTHORITY\["EPSG","9001"\]\],AXIS\["Easting",EAST\],AXIS\["Northing",NORTH\],AUTHORITY\["EPSG","3826"\]\]  
\>>> print("Projection(EPSG):", tgp.wkt\_to\_epsg(ras.projection))  # 取得投影座標WKT  
Projection(EPSG): 3826  
\>>> print("EPSG(4326) to WKT:", tgp.epsg\_to\_wkt(4326))  # 取得投影座標WKT  
EPSG(4326) to WKT: GEOGCRS\["WGS 84",DATUM\["World Geodetic System 1984",ELLIPSOID\["WGS 84",6378137,298.257223563,LENGTHUNIT\["metre",1\]\]\],PRIMEM\["Greenwich",0,ANGLEUNIT\["degree",0.0174532925199433\]\],CS\[ellipsoidal,2\],AXIS\["geodetic latitude (Lat)",north,ORDER\[1\],ANGLEUNIT\["degree",0.0174532925199433\]\],AXIS\["geodetic longitude (Lon)",east,ORDER\[2\],ANGLEUNIT\["degree",0.0174532925199433\]\],USAGE\[SCOPE\["unknown"\],AREA\["World"\],BBOX\[-90,-180,90,180\]\],ID\["EPSG",4326\]\]

然而須注意的是，因為WKT比EPSG的彈性更高，在轉換的時候，EPSG一定可以成功找到WKT，但是WKT未必可以找到相對應的EPSG。另外，如果希望照片可以與向量資料如Shapefile互動，或是要比較精密的測量或面積計算，務必要避免使用WGS84(EPSG:4326)，因為影像的像素網格每一個的長度或寬度都必須固定，但是球面上的每一個網格並無法固定長度或寬度，因為會有一定的形變，疊圖時自然無法準確對應，面積計算也會失準。以下程式碼示範如何將影像轉投影。

import TronGisPy as tgp  
from matplotlib import pyplot as plt  
ras = tgp.read\_raster(tgp.get\_testing\_fp('aereo\_tif')) # 讀取GIS影像  
ras\_reproj = ras.reproject(dst\_crs='EPSG:4326') # 轉投影到EPSG:4326  
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5)) # 開啟一張1x2網格的畫布  
ras.plot(ax=ax1, clip\_percentage=(0.1, 0.9)) # 畫上EPSG:3826的圖像  
ax1.set\_title('EPSG:3826')  
ras\_reproj.plot(ax=ax2, clip\_percentage=(0.1, 0.9)) # 畫上EPSG:4326的圖像  
ax2.set\_title('EPSG:4326')  
plt.show()

![](/images/posts/20210724_trongispy_gis_tool/040f26f5-294b-44ec-89cb-8d80c2e872cd.png)

#### GeoTransofrm(起始位置、網格解析度以及旋轉角)

GeoTransform是由六個數字所構成，如下面程式碼示範如何透過TronGisPy取得GeoTransform。

\>>> import TronGisPy as tgp  
\>>>ras = tgp.read\_raster(tgp.get\_testing\_fp('aereo\_tif')) # 讀取GIS影像  
\>>> ras.geo\_transform  
(219541.78148359052, 0.0201129761884431, 2.3639991549296866, 2654444.8101615803, 2.3639991549296155, -0.020112976188556786)

其中第1個數字(219541.78)以及第四個數字(2654444.81)分別代表圖像最左上角x軸y軸的座標，第二個數字(0.020)與第三個數字(2.36)則代表在圖像上網格每往右移動一格x與y的變化量，第五個數字(2.36)與第六個數字(-0.02)則代表在圖像上網格每往下移動一格x與y的的變化量，以下便列出了圖像網格索引值(Numpy Index)與座標值轉換的公式。

\# 將直從geo\_transform取出  
c, a, b, f, d, e = geo\_transform

\# 矩陣形式的運算  
| coord\_lng |   | a  b  c | | npidx\_col |  
| coord\_lat | = | d  e  f | | npidx\_row |  
|     1     |   | 0  0  1 | |     1     |

\# 寫成一般式  
a \* npidx\_col + b \* npidx\_row + c = coord\_lng  
d \* npidx\_col + e \* npidx\_row + f = coord\_lat

這裡有三點事項必須注意，第一，Numpy Index在索引網個時第一個維度是Row Index、第二格維度才是Column Index，但是座標系統上，第一個維度是x軸方向、第二格維度才是y方向。第二、影像索引值是由上而下，但是座標系統上是數字越大緯度越高，所以大多時候第六個數字都是負值，也就是影像索引值往下移動時，緯度會越來越小。第三，絕大多數的GIS影像都不會有旋轉，所以第三個數字跟第五個數字大多時候都是0，也就是索引值往右移動時，僅會導致座標系統x軸方向的變動，而索引值往下移動時，僅會導致座標系統y軸方向的變動。如果覺得轉換過於複雜，TronGisPy也已經將轉換的函式都寫好了，以下將示範，如何將影像的每一個像素都轉換為xy座標值。

import TronGisPy as tgp  
ras = tgp.read\_raster(tgp.get\_testing\_fp('aereo\_tif')) # 讀取GIS影像  
npidxs\_col, npidxs\_row = np.meshgrid(range(ras.cols), range(ras.rows)) # 給每個像素都取得row\_idx跟col\_idx  
npidxs = np.stack(\[npidxs\_row, npidxs\_col\], axis=-1).reshape(-1, 2) # 將每個像素的row\_idx跟col\_idx整理在同一筆資料  
coords = tgp.npidxs\_to\_coords(npidxs, ras.geo\_transform) # 將影像像素索引值轉換為座標位置  
for npidx, coord in zip(npidxs\[:5\], coords\[:5\]): # 印出頭五個結果  
    print(npidx, "=>", coord)

\# \[0 0\] => \[ 219541.78148359 2654444.81016158\]  
\# \[0 1\] => \[ 219541.80159657 2654447.17416074\]  
\# \[0 2\] => \[ 219541.82170954 2654449.53815989\]  
\# \[0 3\] => \[ 219541.84182252 2654451.90215904\]  
\# \[0 4\] => \[ 219541.8619355 2654454.2661582\]

另外，TronGisPy在繪圖的座標位置以及與向量圖資的疊塗上也有支援。以下程式碼將示範如何將影像與向量疊合呈現，此處的向量是森林分布的圖資。

import TronGisPy as tgp  
import geopandas as gpd  
from matplotlib import pyplot as plt  
ras = tgp.read\_raster(tgp.get\_testing\_fp('aereo\_tif')) # 讀取GIS影像  
df = gpd.read\_file(tgp.get\_testing\_fp('aereo\_tif\_clipper')) # 取得疊圖向量  
fig, ax = plt.subplots(1, 1)# 創建一個畫布，並把圖片跟像量化在同一畫布上  
ras.plot(ax=ax, clip\_percentage=(0.1, 0.9)) # TronGisPy的`plot()`，已經將座標資訊考量進去，僅需與向量畫在同一畫布即可。  
df.loc\[df\['value'\] == 3\].boundary.plot(ax=ax, color='red')  
plt.show()

![](/images/posts/20210724_trongispy_gis_tool/6f38cbab-38bc-4f61-a9fc-3ba68d0a0d1a.png)

### 後記

本篇文章主要在簡介TronGisPy與講解GIS影像的屬性與基本操作。下一篇文章將會聚焦在網格資料(Raster)與向量資料(Vector)的互動、填補露值的方法、以及地形因子的計算等。
