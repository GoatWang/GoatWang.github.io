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
  image: /images/posts/20260307_chardet_ai_clean_room/04_chardet_700_release.png
---

上週，一場圍繞著 Python 函式庫 `chardet` 的授權爭議，在開源社區引爆——這不只是一場技術爭論，更可能是 AI 時代重新定義「程式碼所有權」的第一聲槍響。

為什麼影響這麼大？因為 `chardet` 的使用範圍極廣，這場爭議在開源界幾乎是核彈等級的衝擊。

> `chardet` 是 Python 的**字元編碼偵測工具**——當你拿到一個文字檔案但不知道它是 UTF-8、Big5、Shift-JIS 還是 GBK 時，`chardet` 會自動猜出來。它是 `requests`（Python 最熱門的 HTTP 套件）的依賴項，每月下載量約 **1.3 億次**，幾乎所有寫 Python 的人都間接用過它。

本文基於 [Simon Willison 的分析](https://simonwillison.net/2026/Mar/5/chardet/)、[GitHub Issue #327](https://github.com/chardet/chardet/issues/327) 的 211 則討論、以及 [The Register 的報導](https://www.theregister.com/2026/03/06/ai_kills_software_licensing/)，深入拆解這場爭議的每一個環節。

---

## 故事的起點：一次「輕描淡寫」的版本發布

2026 年 3 月 4 日，`chardet` 的維護者 Dan Blanchard 發布了 7.0.0 版本，發布說明裡寫著：

> Ground-up, MIT-licensed rewrite of chardet. Same package name, same public API — drop-in replacement for chardet 5.x/6.x. Just way faster and more accurate!

![chardet 7.0.0 release](/images/posts/20260307_chardet_ai_clean_room/04_chardet_700_release.png)

翻譯過來就是：**我們從零重寫了整個專案，把授權從 LGPL 改成了 MIT，而且更快更準**。

這個改動有多大？**LGPL 到 MIT 的轉變，意味著無數使用它的閉源軟體不再需要擔心授權合規問題。**

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

![Compaq Portable and IBM PC](/images/posts/20260307_chardet_ai_clean_room/06_wiki_compaq_portable.jpg)

1982 年，Compaq 想要製造一台 100% 相容 IBM PC 的電腦。但 IBM PC 的 BIOS 受版權保護。Compaq 的解決方案後來成為了行業黃金標準——**潔淨室（Clean Room）逆向工程**。

做法極其嚴格：

1. **Team A**（汙染團隊）：逆向工程 IBM BIOS，寫出功能規格說明書。他們**不寫一行代碼**。
2. 規格書經過律師審核，確保不包含受版權保護的內容。
3. **Team B**（潔淨團隊）：**從未見過 IBM 原始碼**，只根據規格書從零寫代碼。

這套流程耗費了 **100 萬美元**，但讓 Compaq 在法庭上成功證明他們的 BIOS 不是 IBM 的衍生品。Compaq Portable 第一年就賣了 53,000 台，營收 1.11 億美元。

後來的案例進一步鞏固了這個法律標準，1990年在intel的案子中**法院首次接受潔淨室抗辯**。

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

![Dan Blanchard's Similarity Table](/images/posts/20260307_chardet_ai_clean_room/03b_dan_reply_jplag_table.png)


正常的版本迭代相似度在 80%-94%。即使是大改版的 6.0.0，最大相似度仍有 80%（因為部分檔案直接沿用）。

但 7.0.0？**最大相似度只有 1.29%**。匹配到的 token 全是 Python 通用模式：`argparse` 樣板、`dict` 字面量、`import` 區塊。

---

## 重寫過程的工程紀律

Dan 公開了整個重寫流程的工件，這不是隨便的 prompt，而是一次嚴謹的工程實踐：

![Rewrite plan](/images/posts/20260307_chardet_ai_clean_room/09_rewrite_plan.png)

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

未來， LLM 會不會是 **IP Laundering（知識產權洗白）** 的工具。

### 2. metadata/charsets.py 的泄漏

在重寫計劃中，有一個關鍵時刻：Claude 實際上**參考了舊代碼庫中的 `metadata/charsets.py` 文件**——這是一個定義字符集屬性的資料類字典。計劃中明確寫著「Do not invent era assignments」（不要自己編造 era 分配），並指向了舊代碼作為權威來源。

在法律訴訟中，這種細節的泄漏往往是致命的證據。

### 3. 同名同 API 的法律陷阱

Dan 選擇保留了 `chardet` 這個套件名和完全一致的公共 API。從工程角度看，這是向後兼容的必要條件。但在法律角度：

- 當你使用相同的套件名和介面時，你在向使用者承諾：**我就是那個東西**
- 這種功能和命名上的延續性，極大地削弱了「獨立作品」的法律防禦力
- Google v. Oracle 案中，聯邦巡迴法院在 2014 年裁定 **API 是可以受版權保護的**（雖然最高法院後來以 fair use 翻盤）

如果 Dan 改個名字——比如叫 `chardet2` 或 `pychardet`——他的合規風險會大幅降低。但他沒有。

---

## 12 年的伏筆：這不是一時興起

![2014 license issue](/images/posts/20260307_chardet_ai_clean_room/08_issue36_2014_license.png)

很多人不知道的是，Dan 想改授權已經 **12 年了**。但要理解他為什麼這麼執著，得先搞懂 LGPL 這個授權到底卡在哪。

> 我們可以合法地更改 chardet 的授權嗎？...我不喜歡 LGPL，用在自己維護的專案上感覺很怪。

LGPL 有兩個核心限制：

1. **允許商用，但修改版必須繼續保持 LGPL 授權**

2. **允許抽換原則**： 無論是否商用，打包binary時（如用PyInstaller 打包成 `.exe`），LGPL 要求「使用者必須有辦法把你 App 裡的 chardet 抽掉，換成他自己修改過的版本」。但這讓 ｀PyInstaller 打包出來的 binary 是把所有 `.pyc` 塞在一起的，使用者根本沒辦法單獨替換。

到了 2021 年，開發者 johnthagen 在同一個 Issue 裡痛陳這個問題對整個生態的傷害：

![LGPL binary challenge](/images/posts/20260307_chardet_ai_clean_room/15_issue36_lgpl_binary_quote.png)

> LGPL makes it challenging for including chardet inside of a binary due to the restriction that users need to be able to swap out the LGPL library for another of their choosing, something infeasible/very tricky for a binary distribution.

> This affects users of Pyinstaller, Nuitka, PyOxdizer, etc. that want to package their Python code and dependencies into a standalone binary.

改成 MIT 意味著什麼？LGPL 要求使用者必須能夠將 LGPL 函式庫替換成自己選擇的版本，這使得將 chardet 包含在二進位檔案中變得非常困難。這影響了所有使用 **PyInstaller**、**Nuitka**、**PyOxidizer** 等工具將 Python 程式碼和依賴項打包成獨立二進位檔的使用者。改成 MIT 後，這些限制全部消失。

所以這段歷史告訴我們：Dan 不是在 vibe coding，他是在用 AI 完成一個規劃了十多年、被法律堵了十多年的目標。

---

## 更大的圖景：當複製成本趨近於零

The Register 的報導將這場爭議推向了更大的舞台。

![The Register coverage](/images/posts/20260307_chardet_ai_clean_room/10_the_register_article.png)

**Bruce Perens**（Open Source Definition 的作者）直接拉響了警報：

![SW Economic Death](/images/posts/20260307_chardet_ai_clean_room/11_sw_eco_death.png)

> 「軟體開發的整個經濟學已經死了、消失了、結束了、完蛋了！」

他描述了自己如何用 AI 在十天內複製了一個現有的 SRE 平台——用不同的語言、不同的授權。

**FSF 執行董事 Zoë Kooyman** 表達了擔憂：

> 「破壞 copyleft 是一個嚴重的行為。」

但 **Flask 的創造者 Armin Ronacher**（mitsuhiko）則表達了不同看法：

![Hacker News discussion](/images/posts/20260307_chardet_ai_clean_room/14_0_agreestatement.png)

> chardet 早就在我認為應該進行潔淨室重寫的函式庫清單上了，無論是出於效能還是授權的原因。

[Hacker News](https://news.ycombinator.com/item?id=47259177) 和各大技術論壇上的討論也同樣激烈。這已經不只是一個 Python 函式庫的問題了。

---

## 我的觀察

我對整件事的想法其實滿矛盾的，一方面，過去的學習大多奠基於這些開源前輩的的貢獻，他們是燈塔般的存在。另一方面，一個消失17年的作者，完全忽視Dan的詢問、對PyInstaller與整個Python社群造成的困擾，竟在此時才願意現身。我大概沒辦法對這件事本身有所評價，但更讓我在意的是，這場爭議背後浮現的一個更大問題：**AI 正在從根本上瓦解開源生態賴以運作的結構。** 我認為這個瓦解會沿著三個階段發生：

### 第一步：複製成本歸零——你的文檔就是你的藍圖

當一個開源專案把文件寫得越詳細、測試覆蓋得越全面，它就越容易被人用極低成本複製。Cloudflare 的工程師用一週時間、1,100 美元的 API 費用，就[重建了 Vercel 花數年打造的 Next.js](https://worksonmymachine.ai/p/open-source-saas-and-the-silence)——而且直接拿 Next.js 自己的測試套件當路線圖。開源在分享代碼的同時，也在分享摧毀自身的藍圖。

chardet 的情況如出一轍：完整的公共 API、詳盡的測試案例、清晰的功能規格，恰恰構成了 AI 重寫所需的全部輸入。諷刺的是，一個專案做得越好、越開放，就越容易被取代。

### 第二步：貢獻者沉默離場——溝通成本大於自給自足

當複製如此容易，開源的經濟邏輯就翻轉了。以前，寫代碼是昂貴的，提交是便宜的。現在完全反過來——寫代碼便宜，但要讓代碼被合併？要fork專案、匹配代碼風格、提交PR、來回修改、通過review，成本遠高於自己動手。**自給自足的成本，已經低於溝通協作的成本。**

更糟的是，每一次貢獻——每一則 Issue、每一個 PR、每一段文檔——都在為下一次 AI 複製提供更完整的養分。貢獻者開始意識到：我在幫別人更容易取代這個專案。

結果是，真正的貢獻者不再敲門了。他們clone、改完、走人。

Dan 的故事正是這個趨勢的極端案例：身為維護者，他等了 12 年無法改授權，最終自己用 AI 重寫了整個專案——這本質上就是「fork and move on」的維護者版本。

### 第三步：製作比參與更便宜——沒有使用的誘因

當複製成本歸零、貢獻者離場，最終的結果是：**人們根本不再使用現有的函式庫，而是直接讓 AI 從零生成。**

一個開發者需要錯誤追蹤工具？他不再評估三四個服務、註冊免費套餐——他直接告訴 AI「幫我做一個」，二十分鐘後就跑起來了。沒有註冊帳號，沒有信用卡，沒有留下任何痕跡。那家 SaaS 公司永遠不知道他的存在。潛在客戶根本不進入市場，整個市場規模無聲收縮。

這個邏輯同樣適用於函式庫生態：未來的開發者可能根本不會去選擇 chardet 或任何現有的 encoding detection 庫，而是直接告訴 AI「幫我寫一個字元編碼偵測模組」。

開源的核心邏輯是一個循環：用戶遇到痛點 → 變成貢獻者 → 貢獻積累成專案 → 專案吸引新用戶。這個循環只在「參與比不參與更容易」的時候才運轉。但當製作比參與更便宜，這個迴路就從根部斷裂了。個體的花園從沒這麼美過，但園丁們互相不認識了——因為沒有理由再走進同一扇門。

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
