---
title: 當 AI 可以在幾小時內「潔淨室重寫」整個開源專案，授權協議還守得住嗎？
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
  image: /images/posts/20260307_chardet_ai_clean_room/01_simon_willison_blog_full.png
---

上週，一場圍繞著 Python 函式庫 `chardet` 的授權爭議，在開源社區引爆。這不只是一場技術爭論，更可能是 AI 時代重新定義「程式碼所有權」的第一聲槍響。

`chardet` 是 Python 的**字元編碼偵測工具**——當你拿到一個文字檔案但不知道它是 UTF-8、Big5、Shift-JIS 還是 GBK 時，`chardet` 會自動猜出來。它是 `requests`（Python 最熱門的 HTTP 套件）的依賴項，每月下載量約 **1.3 億次**，幾乎所有寫 Python 的人都間接用過它。

本文基於 [Simon Willison 的分析](https://simonwillison.net/2026/Mar/5/chardet/)、[GitHub Issue #327](https://github.com/chardet/chardet/issues/327) 的 211 則討論、以及 [The Register 的報導](https://www.theregister.com/2026/03/06/ai_kills_software_licensing/)，深入拆解這場爭議的每一個環節。

---

## 故事的起點：一次「輕描淡寫」的版本發布

2026 年 3 月 4 日，`chardet` 的維護者 Dan Blanchard 發布了 7.0.0 版本，發布說明裡寫著：

> Ground-up, MIT-licensed rewrite of chardet. Same package name, same public API — drop-in replacement for chardet 5.x/6.x. Just way faster and more accurate!

![chardet 7.0.0 release](/images/posts/20260307_chardet_ai_clean_room/04_chardet_700_release.png)

翻譯過來就是：**我們從零重寫了整個專案，把授權從 LGPL 改成了 MIT，而且更快更準**。

這個改動有多大？`chardet` 在 PyPI 上每月有約 **1.3 億次下載**，是 `requests` 等主流套件的依賴項。LGPL 到 MIT 的轉變，意味著無數使用它的閉源軟體不再需要擔心授權合規問題。

但問題是——他有權這樣做嗎？

---

## 原作者的怒火：「你們沒有這個權利」

隔天，一個消失了 15 年的名字重新出現在 GitHub 上。

Mark Pilgrim——`chardet` 的原作者，同時也是《Dive Into Python》的作者——開了一個 Issue，標題直截了當：**No right to relicense this project**。

![Mark Pilgrim's Issue #327](/images/posts/20260307_chardet_ai_clean_room/02_issue327_mark_pilgrim.png)

> 我是 Mark Pilgrim。在 7.0.0 版本中，維護者聲稱擁有「重新授權」本專案的權利。他們並無此權利；這樣做明確違反了 LGPL。他們聲稱這是「完全重寫」是無關緊要的，因為他們充分接觸過原始授權程式碼（也就是說，這並非「潔淨室」實作）。在過程中加入花俏的程式碼生成器，並不能賦予他們任何額外的權利。

這則 Issue 獲得了 **1,328 個 👍** 和 **301 個 ❤️**，211 則留言。社區的站隊明顯偏向 Mark。

Mark 的邏輯很清楚：根據 LGPL，修改後的程式碼必須保持原授權。Dan 維護了這個專案十幾年，腦子裡裝滿了舊代碼的邏輯，不可能做到真正的「潔淨室」隔離。用 AI 幫忙寫，不等於洗白。

---

## 什麼是潔淨室（Clean Room）？先回到 1982 年

要理解這場爭論的核心，需要回溯到個人電腦時代的一個經典案例。

![Compaq Portable and IBM PC](/images/posts/20260307_chardet_ai_clean_room/06_wiki_compaq_portable.png)

1982 年，Compaq 想要製造一台 100% 相容 IBM PC 的電腦。但 IBM PC 的 BIOS 受版權保護。Compaq 的解決方案後來成為了行業黃金標準——**潔淨室（Clean Room）逆向工程**。

做法極其嚴格：

1. **Team A**（汙染團隊）：逆向工程 IBM BIOS，寫出功能規格說明書。他們**不寫一行代碼**。
2. 規格書經過律師審核，確保不包含受版權保護的內容。
3. **Team B**（潔淨團隊）：**從未見過 IBM 原始碼**，只根據規格書從零寫代碼。

這套流程耗費了 **100 萬美元**，但讓 Compaq 在法庭上成功證明他們的 BIOS 不是 IBM 的衍生品。Compaq Portable 第一年就賣了 53,000 台，營收 1.11 億美元。

後來的案例進一步鞏固了這個法律標準：

| 案例 | 年份 | 結果 |
|------|------|------|
| Apple v. Franklin | 1983 | 確立韌體受版權保護 |
| NEC v. Intel | 1990 | **首次法院接受潔淨室抗辯** |
| Sony v. Connectix | 1999 | 確立逆向工程的合理使用 |

這套流程在過去四十年是法律的黃金標準。**但 AI 打破了這個平衡。**

---

## AI 時代：五天完成過去需要數月的工程

以前需要兩支團隊耗時數月才能完成的物理隔離，現在 AI 編碼代理在**幾小時到幾天**內就能跑完。

Dan 在 The Register 的採訪中說：

> 過去阻止我實現這些目標的主要因素是時間。Claude 讓我在大約**五天內**完成了我想要做的事情。

7.0.0 的成果也確實驚人：

- **96.8% 準確率**（比 6.0.0 高 2.3 個百分點）
- **41 倍加速**（mypyc 編譯後，純 Python 也快 28 倍）
- 支援 **99 種編碼**，**49 種語言**偵測
- **零執行時依賴**

但工程上的成功不等於法律上的合規。

---

## Dan 的反擊：用數據重新定義「潔淨室」

面對 Mark 的指控，Dan 的回應非常有策略。他沒有否認自己熟悉舊代碼，而是試圖**重新定義潔淨室的標準**：

![Dan Blanchard's reply](/images/posts/20260307_chardet_ai_clean_room/03_dan_reply_top.png)

> 你說得對，我確實對原始程式庫有著深入的了解：我維護它已超過十年。傳統的潔淨室方法涉及嚴格區隔知悉原始內容的人員與撰寫新實作的人員，而這種區隔在本案中並不存在。
>
> **然而，潔淨室方法的目的是確保最終程式碼不構成原始作品的衍生作品。這是達成目的的手段，而非目的本身。**

Dan 的核心論點是：**別看流程，看結果。** 他拿出了 [JPlag](https://github.com/jplag/JPlag)——一個學術級的代碼抄襲檢測工具——跑出了一組驚人的數據：

![JPlag similarity table](/images/posts/20260307_chardet_ai_clean_room/03b_dan_reply_jplag_table.png)

| 版本對比 | 平均相似度 | 最大相似度 |
|----------|-----------|-----------|
| 5.2.0 vs 5.0.0 | 90.93% | 93.83% |
| 5.0.0 vs 4.0.0 | 87.41% | 91.99% |
| 4.0.0 vs 3.0.0 | 82.99% | 94.09% |
| 6.0.0 vs 5.2.0 | 3.30% | 80.05% |
| **7.0.0 vs 6.0.0** | **0.04%** | **1.29%** |
| 1.1 vs 7.0.0 | 0.50% | 0.64% |

正常的版本迭代相似度在 80%-94%。即使是大改版的 6.0.0，最大相似度仍有 80%（因為部分檔案直接沿用）。

但 7.0.0？**最大相似度只有 1.29%**。匹配到的 token 全是 Python 通用模式：`argparse` 樣板、`dict` 字面量、`import` 區塊。

---

## 重寫過程的工程紀律

Dan 公開了整個重寫流程的工件，這不是隨便的 prompt，而是一次嚴謹的工程實踐：

![Rewrite process](/images/posts/20260307_chardet_ai_clean_room/03c_dan_reply_process.png)

1. 用 [superpowers](https://github.com/obra/superpowers) 工具建立[設計文件](https://github.com/chardet/chardet/commit/f51f523506a73f89f0f9538fd31be458d007ab93)
2. **在空白倉庫中開始**，無法存取舊原始碼
3. **明確指示 Claude 不得基於任何 LGPL/GPL 程式碼**
4. 測試先行：先寫測試用例，再讓 AI 填充實現
5. 逐步審查、測試、迭代每一部分

他列出了 13 項需求，其中第 3 條明確寫著：**Not based on any GPL or LGPL code**。

[完整的重寫計劃](https://github.com/chardet/chardet/blob/925bccbc85d1b13292e7dc782254fd44cc1e7856/docs/plans/2026-02-25-chardet-rewrite-plan.md)包含 21 個任務，採用分層偵測 pipeline 架構——這一切都有跡可查。

Dan 的回應獲得了 57 個 👍，但也有 **151 個 👎**。社區顯然對這個論點有保留。

---

## 裂痕：三個致命的灰色地帶

聽起來似乎無懈可擊，但問題恰恰出在以下幾個地方：

### 1. 受汙染的 LLM 悖論

Claude 是一個大語言模型。它在訓練階段很可能已經吞噬過 GitHub 上成千上萬份 `chardet` 的副本。

> 如果一個人類工程師看過原始碼，我們說他被「汙染」了。那麼一個訓練資料裡包含原始碼的 AI，算不算被汙染了？

如果算，那 Claude 生成的每一行代碼，本質上都可能是某種形式的記憶提取——所謂的 **IP Laundering（知識產權洗白）**。

GitHub 上的 justinclift 精準指出：

> 應該假設（或確認）chardet 的原始碼是 LLM 訓練資料的一部分嗎？如果是，那就可能非常相關。(63 👍)

而就在這場爭論爆發的同時，美國最高法院剛拒絕重審 *Thaler v. Perlmutter* 案——這意味著 **AI 生成的內容不能獲得版權**。這帶來一個弔詭的問題：如果 7.0.0 主要由 AI 生成，它可能根本無法被授權。

### 2. metadata/charsets.py 的泄漏

![Rewrite plan](/images/posts/20260307_chardet_ai_clean_room/09_rewrite_plan.png)

在重寫計劃中，有一個關鍵時刻：Claude 實際上**參考了舊代碼庫中的 `metadata/charsets.py` 文件**——這是一個定義字符集屬性的資料類字典。計劃中明確寫著「Do not invent era assignments」（不要自己編造 era 分配），並指向了舊代碼作為權威來源。

在法律訴訟中，這種細節的泄漏往往是致命的證據。

### 3. 同名同 API 的法律陷阱

Dan 選擇保留了 `chardet` 這個套件名和完全一致的公共 API。從工程角度看，這是 drop-in replacement 的必要條件。但在法律角度：

- 當你使用相同的套件名和介面時，你在向使用者承諾：**我就是那個東西**
- 這種功能和命名上的延續性，極大地削弱了「獨立作品」的法律防禦力
- Google v. Oracle 案中，聯邦巡迴法院在 2014 年裁定 **API 是可以受版權保護的**（雖然最高法院後來以 fair use 翻盤）

如果 Dan 改個名字——比如叫 `chardet2` 或 `pychardet`——他的合規風險會大幅降低。但他沒有。

---

## 12 年的伏筆：這不是一時興起

![2014 license issue](/images/posts/20260307_chardet_ai_clean_room/08_issue36_2014_license.png)

很多人不知道的是，Dan 想改授權已經 **12 年了**。但要理解他為什麼這麼執著，得先搞懂 LGPL 這個授權到底卡在哪。

LGPL 有兩個核心限制：

1. **允許商用，但修改版必須繼續保持 LGPL 授權**

2. **允許抽換原則**： 無論是否商用，打包binary時（如用PyInstaller 打包成 `.exe`），LGPL 要求「使用者必須有辦法把你 App 裡的 chardet 抽掉，換成他自己修改過的版本」。但這讓 ｀PyInstaller 打包出來的 binary 是把所有 `.pyc` 塞在一起的，使用者根本沒辦法單獨替換。

**技術上這就違反了 LGPL**。

2014 年，Dan 在 [Issue #36](https://github.com/chardet/chardet/issues/36) 中首次提出想改授權：

> 我們可以合法地更改 chardet 的授權嗎？...我不喜歡 LGPL，用在自己維護的專案上感覺很怪。

另一位維護者 sigmavirus24 的回答很直接：

> 我 98% 確定只有原作者才能改授權。除非完全重寫，否則我們做不到。

到了 2021 年，開發者 johnthagen 在同一個 Issue 裡痛陳這個問題對整個生態的傷害：

![LGPL binary challenge](/images/posts/20260307_chardet_ai_clean_room/15_issue36_lgpl_binary_quote.png)

> LGPL makes it challenging for including chardet inside of a binary due to the restriction that users need to be able to swap out the LGPL library for another of their choosing, something infeasible/very tricky for a binary distribution.

Dan 的回應充滿無奈：

> 很遺憾，因為 chardet 的原始程式碼是基於 LGPL 的，我們真的沒辦法重新授權。**相信我，如果可以的話，我一定會做。** 甚至有人提議把 chardet 加入 Python 標準庫，但因為無法改授權而作罷。

改成 MIT 意味著什麼？意味著整條依賴鏈被解放——所有閉源產品、打包工具、企業用戶都不再有合規風險。`requests` 的使用者不用再擔心 LGPL 的傳染性。這不是小事。

所以這段歷史告訴我們：Dan 不是在 vibe coding，他是在用 AI 完成一個規劃了十多年、被法律堵了十多年的目標。

---

## 更大的圖景：當複製成本趨近於零

The Register 的報導將這場爭議推向了更大的舞台。

![The Register coverage](/images/posts/20260307_chardet_ai_clean_room/10_the_register_article.png)

**Bruce Perens**（Open Source Definition 的作者）直接拉響了警報：

> 「軟體開發的整個經濟學已經死了、消失了、結束了、完蛋了！」

他描述了自己如何用 AI 在十天內複製了一個現有的 SRE 平台——用不同的語言、不同的授權。

**FSF 執行董事 Zoë Kooyman** 表達了擔憂：

> 「破壞 copyleft 是一個嚴重的行為。」

但 **Flask 的創造者 Armin Ronacher**（mitsuhiko）則表達了不同看法：

> chardet 早就在我認為應該進行潔淨室重寫的函式庫清單上了，無論是出於效能還是授權的原因。

![Hacker News discussion](/images/posts/20260307_chardet_ai_clean_room/14_hackernews_discussion.png)

Hacker News 和各大技術論壇上的討論也同樣激烈。這已經不只是一個 Python 函式庫的問題了。

---

## 範式轉移：從流程隔離到可測相異性

這場爭論揭示了一個正在發生的範式轉移：

**舊範式（1982-2025）：流程導向**
- 兩支隔離團隊
- 律師審核規格書
- 物理隔離 = 法律安全

**新範式（2026-）：結果導向？**
- 一個人 + AI 代理
- 代碼相似度審計（JPlag 等工具）
- 可測量的結構差異 = 法律安全？

過去我們問「**誰**寫了代碼」，現在 Dan 試圖讓我們改問「代碼**長得像不像**」。

但法律體系是否準備好接受這個轉變？答案還是未知數。

---

## 我的觀察

Simon Willison 說他個人傾向於認為重寫是合法的，但雙方的論點都完全可信。我同意這個判斷。

幾個值得思考的點：

1. **Dan 的工程紀律值得尊敬**——他不是隨便丟個 prompt，而是做了嚴謹的設計、測試、審計流程。
2. **但 LLM 的訓練資料問題是一顆定時炸彈**——如果法院認定訓練過原始碼的 AI 等同於「被汙染」，那所有 AI 輔助的潔淨室重寫都將站不住腳。
3. **真正的考驗不在開源社區，而在商業世界**——當企業發現可以用 AI 在幾天內複製競爭對手的核心算法，資金充裕的訴訟將不可避免。

在 LLM 時代，複製成熟代碼的工程成本正在無限趨近於零。當代碼變得如此廉價，**以此為基礎建立的信任、品牌和法律邊界，才是未來真正昂貴的資產。**

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
