---
title: 從「chardet AI 抄襲案」看AI 如何「洗白」開源專案的授權違約
date: '2026-03-07T00:00:00+08:00'
draft: false
categories:
- AI & Open Source
tags:
- ai
- open-source
- licensing
- clean-room
- claude-code
- chardet
cover:
  image: /images/posts/20260307_chardet_ai_clean_room/04_chardet_700_release.png
---

上週，一場圍繞著Python library: `chardet`的授權爭議，在開源社群大爆炸——這極有可能是開源世界大核彈。

為什麼影響這麼大？因為 `chardet` 的使用範圍極廣，每月約**1.3 億次**的下載量。

> 題外話，`chardet`是 Python的**字元編碼偵測工具**——

> 想像一下，我不知道這個套件時，我如果拿到亂碼的文字檔案，我就會開啟vscode change file encoding亂猜。

> 這個套件就是讓你不用猜，`chardet` 會自動偵測出來UTF-8、Big5、Shift-JIS 還是 GBK 

> 如果你不知道`chardet`，那以一定聽過`requests`，`requests`正是`chardet`的使用者。

本文基於 [Simon Willison 的分析](https://simonwillison.net/2026/Mar/5/chardet/)、[GitHub Issue #327](https://github.com/chardet/chardet/issues/327) 的 211 則討論、以及 [The Register 的報導](https://www.theregister.com/2026/03/06/ai_kills_software_licensing/)，深入拆解這場爭議的每一個爭點。

---

## 故事的起點：一次「輕描淡寫」的版本發布

2026年3月4日，`chardet`的維護者Dan Blanchard發布了7.0.0版本，發布說明裡寫著：

> Ground-up, MIT-licensed rewrite of chardet. Same package name, same public API — drop-in replacement for chardet 5.x/6.x. Just way faster and more accurate!

![chardet 7.0.0 release](/images/posts/20260307_chardet_ai_clean_room/04_chardet_700_release.png)

翻譯過來就是：**我們從零重寫了整個專案，把授權從 LGPL 改成了 MIT，而且更快更準**。

這個改動有多大？LGPL 到 MIT 的轉變，也就代表**所有下游使用者可以不必開源了。**

但問題是——他有權這樣做嗎？

---

## 原作者的怒火：「你們沒有這個權利」

隔天，一個消失了15年的名字重新出現在GitHub上。

Mark Pilgrim——`chardet`的原作者，同時也是《Dive Into Python》的作者——開了一個Issue，標題直截了當：**No right to relicense this project**。

![Mark Pilgrim's Issue #327](/images/posts/20260307_chardet_ai_clean_room/02_issue327_mark_pilgrim.png)

> 我是 Mark Pilgrim。在 7.0.0 版本中，維護者聲稱擁有「重新授權」本專案的權利。他們並無此權利；這樣做明確違反了 LGPL。...

這則 Issue 獲得了 **1,328 個 👍** 和 **301 個 ❤️**，211 則留言。開源社群明顯偏向 Mark 的立場。

Mark清楚的表明：根據 LGPL，修改後的程式碼必須保持原授權。Dan 維護了這個專案十幾年，腦子裡全是舊程式碼的邏輯，不可能做到真正的「潔淨室」隔離。用 AI 幫忙寫，不等於洗白。

比較有趣的是，他提到這並非「潔淨室」實作...

---

## 什麼是潔淨室（Clean Room）？

歷史太重，講得輕巧一點。

![Compaq Portable and IBM PC](/images/posts/20260307_chardet_ai_clean_room/06_wiki_compaq_portable.jpg)

1982 年，Compaq 想要製造一台 100% 相容 IBM PC 的電腦。但！ IBM PC 受版權保護。

怎麼辦？

Compaq組成了兩個團隊

1. **團隊A**（汙染團隊）：逆向工程 IBM PC，寫出功能規格文件。他們**不寫一行程式碼**。
2. 規格書經過律師審核，確保不包含受版權保護的內容。
3. **團隊B**（潔淨團隊）：**從未見過 IBM 原始碼**，只根據「規格書」從零開始敲叩。

這套流程後法院認證有效，在過去四十年是法律的黃金標準。**但 AI 打破了這個平衡。**

---

## AI 時代：五天完成過去需要數月的工程

以前需要兩支團隊耗時數月才能完成的物理隔離，現在 AI 編碼代理在**幾小時到幾天**內就能跑完。

Dan在The Register的採訪中說：

> 過去阻止我實現這些目標的主要因素是時間。Claude 讓我在大約**五天內**完成了我想要做的事情。

7.0.0 的成果也確實驚人：

- **96.8% 準確率**（比 6.0.0 高 2.3 個百分點）
- **41 倍加速**（mypyc 編譯後，純 Python 也快 28 倍）
- 支援 **99 種編碼**，**49 種語言**偵測
- **零執行時依賴**

但工程上的成功不等於法律上的合規。

---

## Dan 的反擊：用數據重新定義「潔淨室」

面對 Mark 的指控，Dan 的回應非常有策略。他沒有否認自己熟悉舊程式碼，而是試圖**重新定義潔淨室的標準**：

![Dan Blanchard's reply](/images/posts/20260307_chardet_ai_clean_room/03_dan_reply_top.png)

> 你說得對，我確實對原始程式庫有著深入的了解：我維護它已超過十年。......
>
> **然而，潔淨室方法的目的是確保最終程式碼不構成原始作品的衍生作品。這是達成目的的手段，而非目的本身。**

我知道這很嗷口，基本上就是，潔淨室證明了新作品不是抄襲來的，我也證明了他不是抄襲來的，你不要吵。

Dan 的核心論點是：**別看流程，看結果。** 他拿出了 [JPlag](https://github.com/jplag/JPlag)——一個學術級的代碼抄襲檢測工具——跑出了一組驚人的數據：

![Dan Blanchard's Similarity Table](/images/posts/20260307_chardet_ai_clean_room/03b_dan_reply_jplag_table.png)


正常的版本迭代相似度在 80%-94%。即使是大改版的 6.0.0，最大相似度仍有 80%（因為部分檔案直接沿用）。

但 7.0.0？**最大相似度只有 1.29%**。匹配到的 token 全是 Python 通用模式：`argparse` 樣板、`dict` 字面量、`import` 區塊。

---

## 重寫過程的工程紀律

Dan 公開了整個重寫流程的工件：

![Rewrite plan](/images/posts/20260307_chardet_ai_clean_room/09_rewrite_plan.png)

1. **在空白倉庫中開始**，無法存取舊原始碼
2. **明確指示 Claude 不得基於任何 LGPL/GPL 程式碼**
3. .....

他列出了 13 項需求，其中第 3 條明確寫著：**Not based on any GPL or LGPL code**。

[完整的重寫計劃](https://github.com/chardet/chardet/blob/925bccbc85d1b13292e7dc782254fd44cc1e7856/docs/plans/2026-02-25-chardet-rewrite-plan.md)包含 21 個任務，採用分層偵測 pipeline 架構——這一切都有跡可查。

Dan 的回應獲得了 57 個 👍，但也有 **151 個 👎**。顯然開源社群不買賬。

---

## 裂痕：三個致命的灰色地帶

聽起來似乎無懈可擊，但問題恰恰出在以下幾個地方：

### 1. 受汙染的 LLM 悖論

它在訓練階段很可能已經吞噬過 GitHub 上成千上萬份 `chardet` 的副本。

> 如果一個人類工程師看過原始碼，我們說他被「汙染」了。那麼一個模型看過算不算被「汙染」了？

未來， LLM 會不會是 **IP Laundering（知識產權洗白）** 的工具。

### 2. 同名同 API 的法律陷阱

Dan 選擇保留了 `chardet` 這個套件名和完全一致的公共 API 介面。

當然，他希望使用者可以無痛轉換到新版本，所以有這個設計。

但是**API 是可以受版權保護的**！

---

## 12 年的伏筆：這不是一時興起

最有趣的是，Dan 想改授權已經 **12 年了**。是什麼原因讓他這樣執著？

![2014 license issue](/images/posts/20260307_chardet_ai_clean_room/08_issue36_2014_license.png)

他在2014年的一個issue問到

> 我們可以合法地更改 chardet 的授權嗎？...我不喜歡 LGPL，用在自己維護的專案上感覺很怪。

最主要原因就是，LGPL下面這兩個讓人難受的條件：

1. **修改版必須繼續保持 LGPL 授權**

2. **允許抽換原則**： 無論是否商用，打包binary時（如用PyInstaller 打包成 `.exe`），LGPL 要求「使用者必須有辦法把你 App 裡的 chardet 抽掉，換成他自己修改過的版本」。但這讓 ｀PyInstaller 打包出來的 binary 是把所有 `.pyc` 塞在一起的，使用者根本沒辦法單獨替換。

到了 2021 年，另一位開發者 johnthagen 在同一個 Issue 裡寫出了的多套件開發者心裡的痛：

![LGPL binary challenge](/images/posts/20260307_chardet_ai_clean_room/15_issue36_lgpl_binary_quote.png)

> LGPL makes it challenging for including chardet inside of a binary due to the restriction that users need to be able to swap out the LGPL library for another of their choosing, something infeasible/very tricky for a binary distribution.

> This affects users of **Pyinstaller**, **Nuitka**, **PyOxdizer**, etc. that want to package their Python code and dependencies into a standalone binary.

這說明了**PyInstaller**、**Nuitka**、**PyOxidizer** 等使用到`chardet`的工具，要設計一套合理的機制讓使用者在binary裡面抽換不同版本的`chardet`，這對binary檔案來說，造成很大的困擾。

Dan就在這個AI出現的轉折，開始了他蓄謀已久的復仇。

---

## 社群的反饋

也有媒體 The Register 報導這則趣聞。

![The Register coverage](/images/posts/20260307_chardet_ai_clean_room/10_the_register_article.png)

**Bruce Perens**（Open Source Definition 的作者）直接宣告了軟體經濟學已死：

![SW Economic Death](/images/posts/20260307_chardet_ai_clean_room/11_sw_eco_death.png)

> 「軟體開發的整個經濟學已經死了、消失了、結束了、完蛋了！」

他也分享了他如何用AI在十天內複製了一個現有的 SRE 平台，並使用「不同的語言」跟「不同的授權」。

**FSF 執行董事 Zoë Kooyman** 作為開源世界的最後一道防線，自然也是站在反對的立場。

但 **Flask 的創造者 Armin Ronacher**（mitsuhiko）則表達了不同看法：

![Hacker News discussion](/images/posts/20260307_chardet_ai_clean_room/14_0_agreestatement.png)

> chardet 早就應該被重寫了，無論是出於效能還是授權的原因。

[Hacker News](https://news.ycombinator.com/item?id=47259177) 和各大技術論壇上的討論也同樣激烈。畢竟這是一個開源世界的存亡之戰。

---

## 我的觀察

先撇開對錯問題不談，我為什麼說這個一個開源世界的存亡戰爭。我預計這一槍響後，**AI 正在將從根本上瓦解開源生態。**並從下面兩個方向發展：

### 方向一：複製成本歸零——清晰的文檔就是AI的藍圖

當一個開源專案把文件寫得越詳細、測試覆蓋得越全面，它就越容易被人用極低成本複製。開源在分享程式碼的同時，也在分享摧毀自身的藍圖。

從本案例就可以窺知一二，全部的API接口都照抄、加上詳盡的測試案例，AI還不把你寫爆，搞不好寫的還比原作好。

可以想像未來大家對於開源專案的授權不滿意，也懶得跟你吵架，直接重寫更快。

這就是一個諷刺的悖論，一個專案做得越好、越開放，就越容易被取代。

### 方向二：溝通成本大於自給自足->貢獻者沉默離場

想像一下過去要貢獻，要經過fork專案、匹配程式碼風格、提交PR、來回修改、通過review，這過程不只要專業還要耐心。

在AI時代，複製成本遠大於溝通成本時，大家改出了自己要的功能就跑了，根本不會去送PR。

clone、改完、走人。

貢獻者消失了，集體的智慧累積也消失了。

---

> 個體的花園從沒這麼美過，但園丁們互相不認識了——因為沒有理由再走進同一扇門。

開源世界的土崩瓦借似乎已經是一個不可避免的未來。

---

## 參考資料

- [Simon Willison - Can coding agents relicense open source through a "clean room" implementation of code?](https://simonwillison.net/2026/Mar/5/chardet/)
- [GitHub Issue #327 - No right to relicense this project](https://github.com/chardet/chardet/issues/327)
- [Dan Blanchard's detailed response](https://github.com/chardet/chardet/issues/327#issuecomment-4005195078)
- [The Register - Chardet dispute shows how AI will kill software licensing](https://www.theregister.com/2026/03/06/ai_kills_software_licensing/)
- [chardet 7.0.0 Release Notes](https://github.com/chardet/chardet/releases/tag/7.0.0)
- [2014 License Discussion (Issue #36)](https://github.com/chardet/chardet/issues/36)
- [Wikipedia - Clean-room design](https://en.wikipedia.org/wiki/Clean-room_design)
- [chardet Rewrite Plan](https://github.com/chardet/chardet/blob/925bccbc85d1b13292e7dc782254fd44cc1e7856/docs/plans/2026-02-25-chardet-rewrite-plan.md)
- [JPlag - Source Code Plagiarism Detection](https://github.com/jplag/JPlag)
- [Hacker News Discussion](https://news.ycombinator.com/item?id=47259177)
