---
title: 我的全 Agent 開發實錄 —— 看不懂swift，但我每天有 20 個 commits
date: '2026-04-12T00:00:00+08:00'
draft: false
categories:
- AI & LLM
tags:
- ai-agent
- codex
- claude
- worktree
- testing
- ios
summary: 過去一個月，我真的像是進入另一種開發模式。從 Web 到 iPhone Simulator、從 feature worktree 到獨立驗證環境，我把整套全 Agent 開發流程慢慢補齊。這篇文章整理七個我目前最有感的實戰建議。
cover:
  image: /images/posts/20260412_full_agent_dev_ecosystem/cover.png
---

過去一個月，我的 terminal 沒有少於三個 agent session 同時在跑；每次開 screen share，畫面裡都有一台 iPhone Simulator 在自己點來點去；我打開 FB 的次數從一天 N 次掉到一天一次，而且每次打開通知都至少有五則。

這篇是這一個月踩坑下來，八個我目前最有感的建議。

## 1. 必須閉環

如果 Agent 沒有自我驗證的能力，那人類的驗證工作絕對跟不上開發速度。「沒有閉環」就是那個 bottleneck。

現在網頁的自我驗證已經做得很好，因為可以看到介面，Agent 也可以拿到 DOM 跟 id 去操作控制。但是有兩週時間，我卡在沒有辦法操控 iPhone Simulator，如果沒有給 AI 對的工具使用，它會截圖去看怎麼操作，就會很不精準，所以最後把所有的驗證工作都壓到自己身上。

我後來發現，有套件可以像 Android 的 adb cmd 一樣去做 UI Automation，可以拿到 UI component 的 id，然後操作它們，一直到這週才把 app 的開發閉環環境建立起來。

現在每開發一個 feature，它都會自己寫驗證提案跟報告，然後會把驗證過程中的截圖附在報告裡。每次開啟 screen share，就看到 Simulator 在認真跑驗證，且每次都是有效率有意義的 case，看 Simulator 就知道它在驗證什麼功能，有種讓人放心的感覺。

**現在遇到比較大的問題是，我一次只能用一個 Simulator 跑驗證，不然會報 conflict。如果有人知道這個怎麼解，拜託告訴我。**

## 2. 只要動到 code 就要開 Worktree

一開始我很鐵齒，覺得這個 feature 很小，我就在 main 上面開發，但每次 Agent 的 feature 開發時長加上驗證都是幾個小時，這種要排程 feature 來開發的事情真的不適合人來做，後來我就寫死無論大小 feature 全部要開 feature worktree，自此之後，我的 terminal 就沒有小於三個 agent sessions 同時運作。只要不是巨大的 refactor 工作，Agent merge 回 main 時都可以自己把衝突解決好。

如何讓自己可以保持在長時間高強度的工作狀態的關鍵也在這——因為要追蹤三條到四條開發主線，所以每送出一個 prompt 之後，就會有下一個 terminal 有問題等著你去解決，所以就會強迫自己思考每一個 session 的下一步，於是就不會有等待跟無聊的時間。

有人說 Agent 開發會破壞心流。我剛開始也是這樣感受。後來發現是用法不對——當你同時掛三條 worktree，每送出一個 prompt 就有下一個 terminal 在等你回應，根本沒有「等待」這個狀態，自然也沒有「無聊」這個狀態。**心流不是被打斷，是被換了一種形狀。**

## 3. 要為每一個 session 建立獨立乾淨的驗證環境

因為每一個 session 都會開發自己的 feature worktree，會有自己的資料夾跟 code logic，都會需要跑驗證，總不能 merge 回去再驗證，所以驗證流程在跑的過程，就要給它們乾淨的環境去跑。例如 web 開發，就要寫好 start server 的 script，然後定義好每一個 session 用哪個 port、資料夾、資料庫去跑驗證，這樣才能真正把平行開發做起來。

## 4. 先抄襲後加 Feature

每一個應用程式背後都有自己的工程 domain，表面上是拉皮，但背後做了多少苦功，通常我們沒特別研究就會忽略，但這些忽略都會在未來變成債務。如果 AI 的強項就是抄襲，就讓它先把核心功能抄起來，再去加自己要的 feature。

我最近才知道，Telegram 為了讓 chat 流暢，在 iPhone app 裡偷養了一個 SQLite。為了讓 input 跟 title 不擋訊息，它們做了半透明設計。為了 pagination 滑得順，本地化下了一堆功夫。

這些細節，使用者一輩子不會注意到，但你不抄就會自己撞——而且通常會撞兩次。

我最近在做 chat 的功能，直接跳進去做，後來重新檢討整個過程才發現，Telegram 的 code 就公開在網路上，先把它的 infra 抄過來真的可以省心很多。太多太多細節設計，真的不是使用者看得到的。

如果我一開始就先把這些核心 infra 抄過來，可以少掉很大一段 debug rotation——就是 A feature 做完 B feature 就壞掉的迴圈，畢竟有些東西就是 infra 的問題，A 跟 B 不可能同時滿足。當然，如果這樣做，我可能也不會發現 chat 的流程是多偉大的設計。

另外，這也是讓 Agent 長時間工作不用介入的關鍵。在開發任務上最花時間的除了驗證，就是開需求。如果沒有做過相關應用，自己開的需求絕對沒辦法一步到位，無論是 infra 的系統規劃跟使用者體驗的刻畫，都是前人一步步坑踩出來的。但如果藍圖建好了，這些都可以讓 AI 一步到位，長時間按照藍圖工作。純開發加驗證，這大概是我唯一可以讓 Agent session 連續工作兩小時以上，不需要我介入的過程。

## 5. Maintainability Counts

這邊的可維護性，是指你丟指令給 Agent 時，它有能力 focus 在改一個地方，就適用到整個專案，不需要 scan 整個專案去找哪裡需要一起更新。

AI 在訓練時，現在一定大多是解決短期問題，只要最終看得到成果，就是成功達成任務，但是做一個中型甚至大型的專案，重要的絕對是長期可維護性，也就是只要重複的邏輯，要整理成 function 甚至 module，以後可以只改一個地方，所有地方普遍適用。

舉個例子來說，我這次開發要在 app 上做 File Explorer，我在三個不同的入口都需要同一個 File Explorer，僅有小部分 UI 調整，Agent 的選擇是分別寫在不同的 file（雖然 Swift 我完全看不懂，但我看得出來它在三個不同的 file 裡寫了三份），但我每次調整時，它就只會動到我指定的那一個介面，並不會適用到其他 File Explorer。我讓它做 Modularize 後，這個問題才被解決。

## 6. File System 就是 Memory System

我在做這個新專案時有一個很大的心態轉變，作為一個資深工程師，要面對自己對於程式碼失去掌握的恐慌，大概是第一個面臨的挑戰。如果做的是一次性的開發，只要支援一定功能後就可以放一邊的專案，倒是沒什麼問題。但如果是要長期維護的專案，用純嘴++寫程式還是有很大的心理負擔。

這次專案我秉持著一個死豬不怕開水燙的原則，反正我也不會寫swift，更不可能有耐心去學這種折磨人的技術。於是...我就想著「做出來算賺到，做不出來也是剛好」，並開始了這一趟奇妙的旅程。我竟驚訝地發現 Agent 在這方面表現極為出色，就是仍然缺乏一套記憶系統，常常會忘記自己做過哪些 feature。

於是，我開始在每一個 feature 開發前，要求 Agent 要先開 implementation plan 跟 verification plan，然後做完之後要產 report，用日期跟當天的第幾個 feature 作為 folder 檔頭命名。然後再叫 Agent 刻一個 find_context command，去這些資料夾當中找到當時開發特定 feature 時做的事情，一方面 debug 可以用、一方面新 feature 開發也可以基於完整的 context 繼續開發。

最近很多人在做 Agent Memory System，這嚴格來說確實很重要，但太過系統化的、高階抽象化的 Memory，對人類反而是障礙。以我一天平均 20 個 commits 的量來說，其實真的要把每一個 commit 的歷史背景、問題重現邏輯、實作方法、驗證步驟全部記錄下來，一個月也就 600 個資料夾，加上 commit logs 加上 session history（~/.codex/sessions or ~/.claude/projects/），grep 檢索的效率目前還是沒有太大問題的，關鍵字到位，其實目前用起來還是體驗很好的。

## 7. 工具相關：Effort 開到最大，慢慢等，總比繞圈圈好

其實，這個專案讓我看清了 Claude 的愚蠢，還有 Codex 的優越，尤其是 Claude 總是無法看清全局，debug rotation 往往讓人懷疑過去一個禮拜到底有沒有進度，加上 Claude 的討好人格極度讓人煩躁，很像一個沒能力的員工整天跟你形式化道歉跟擺爛。Codex 很大程度地解決這個問題，只要沒有 misalignment，基本上它都能完成任務。

## 8. 工具相關：如果你手邊要忙其他事，又不想耽擱開發

Claude 可以買 100 然後 Codex 買 200，在 Telegram 上面丟需求讓 Claude 當 PM 去 PUA Codex 工作（簡單說就是用 Claude 翻譯需求、拆任務、督促進度）。這可以大概延長連續工作時間 1.5 倍，也會減少確認需求的工作，Claude 會翻譯成你不太需要花時間閱讀的報告，讓你快速做決策。

但如果我有整天的時間，我會直接開四個 Codex sessions 開始工作，多一層 PM 對很多小 feature 的開發來說還是很浪費時間。
