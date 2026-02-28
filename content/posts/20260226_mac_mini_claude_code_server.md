---
title: 把 Mac Mini 變成 24 小時 Claude Code Server設定筆記
date: '2026-02-26T00:00:00+08:00'
draft: false
categories:
- Tools & DevOps
tags:
- claude-code
- mac-mini
- remote-development
- tailscale
- ssh
cover:
  image: /images/posts/20260226_mac_mini_claude_code_server/cover.jpg
---

最近龍蝦很多，但就是個仰賴包裝的產品。Claude Code (CC) 的失敗就在於宣傳，說實話能力都有到，就是主打給工程師用，離大眾的距離就遠了。

龍蝦的宣傳，搞得自己像是讓一般人變成工程師的橋樑，你上橋才發現盡頭不是對岸，是一堆爬不過的山頭，架 server、拿固定 IP、算 token 成本，這堆麻煩事都省不了。

講白了，龍蝦就是 CC 加上讓你以為你可以的宣傳，但難關終究要面對的。

既然要讓 CC 全天候運轉，那麼就要解決一個問題，就是可以遠端進去開發跟用手機下指令。

於是我就入手了一台 Mac Mini，專門當作 24 小時的遠端開發伺服器。

以下就分享我的實作筆記。

畢竟坑都踩了，總要記錄一些什麼下來。

下面的步驟你可以請CC幫你看，軟體設定的部分幫你做好，硬體的跟UI的設定，讓CC提醒你要做什麼。

---

## Step 1：基本設定 — 讓 Mac Mini 永不休眠

### 關閉自動睡眠

到 **系統設定 > 能源** 中：

| 設定 | 值 | 原因 |
|------|-----|------|
| 防止自動進入睡眠（顯示器關閉時） | **開啟** | 核心設定，讓 Mac 永遠保持喚醒 |
| 喚醒以進行網路存取 | **關閉** | 避免 DarkWake 循環 |
| 啟用 Power Nap | **關閉** | 避免背景維護觸發睡眠/喚醒 |
| 低耗電模式 | **關閉** | 避免省電模式干擾 |

到 **系統設定 > 鎖定畫面** 中：
- **使用電源轉接器時，閒置多久後關閉顯示器** → 設為 **永不**

### Terminal 指令加強

```bash
sudo pmset -a displaysleep 0 disksleep 0 womp 0 powernap 0
sudo pmset -a autorestart 1
```

> `autorestart 1` 會讓 Mac 在斷電後自動重開機！

### 設定自動登入

到 **系統設定 > 一般 > 使用者與群組 > 登入選項**，將「自動登入」設為你的使用者帳號。這樣停電重開後不需要手動登入。

---

## Step 2：手機也能操控 Claude Code

手機連上CC的方法非常簡單，不需要設定遠端連線方法，不用固定IP、不用tailscale反向代理。

CC 終於推出手機操控了！昨天我才受不了 Happy Coder 的 session 紊亂，fork 了一把 Telegram Bot（[CTB](https://github.com/GoatWang/claude-telegram-bot)），把 Claude command 的功能補全上去（影片中 Telegram 的斜線「/」功能），今天 Claude 就官方推出手機功能。

三種方案我都用過了，來比較一下 Happy Coder、CTB 跟 Claude App：

- **Happy Coder**：交互整體做得很好，該有的功能都有，有斜線 commands、選項按鈕、diff view，切換不同 mode（YOLO mode、plan mode）跟 model 都有 UI 可以調整。缺點就是不太穩定，會亂開或開不了 session，租的機器記憶體太小，session 開太多記憶體會爆，所以後來沒用了。
- **CTB**：因為手機端的 app 不用重新刻，用 vibe coding 做客製化很方便，昨天花十分鐘就把 Claude command 做上去了。缺點是只能用 Telegram 現有的 UI widget，diff view 跟同意的流程就犧牲了，也無法選擇 mode 跟 model。不過只要透過電腦開 session，一開好就很穩定。
- **Claude App**：剛推出，基本上跟 CTB 差不多，要透過電腦開 session，目前還沒有把 Claude command 清單的功能做好。不過相信會急起直追，反正 Claude 內部已經進入 agent 奇點，等一個月什麼功能都有了。

### Telegram CTB 操控畫面

![Telegram CTB Access](/images/posts/20260226_mac_mini_claude_code_server/telegram_ctb_access.gif)

### Claude App Remote Control 操控畫面

![Claude App Access](/images/posts/20260226_mac_mini_claude_code_server/claude_app_access.gif)

---

## Step 3：設定遠端存取

你需要能從任何地方連上這台 Mac Mini，有兩種方式：

### 方法 A：Tailscale

[Tailscale](https://tailscale.com) 是一個零設定的 VPN 工具，它會給每台裝置一個固定的虛擬 IP，不管你的實體網路怎麼變，這個 IP 都不會變。

如果沒有要架設網站或其他服務給其他人使用，Tailscale的設定比較簡單，可以先使用，並略過下面的固定IP設定。

要註冊一個帳號，但用量小免費。

**Mac Mini 上：**
1. 從 Mac App Store 下載安裝 **Tailscale**
2. 登入你的帳號（Google / GitHub / Email 都可以）
3. 記下分配到的 IP（例如 `100.85.xx.xx`）
4. 打開 Tailscale 偏好設定，啟用 **「登入時啟動」**

**你的筆電上：**
1. 也安裝 Tailscale，用同一個帳號登入
2. 之後就可以直接：

```bash
ssh your-username@100.85.xx.xx
```

### 方法 B：固定 IP + Port Forwarding

其實很多人不知道如果你的家用網路是由中華電信提供的，[你可以申請一組固定IP](https://123.cht.com.tw/HiNetStaticIp)，申請完大概半小時內就會收到通知信。

![中華電信固定 IP 配發通知](/images/posts/20260226_mac_mini_claude_code_server/hinet_fixed_ip_email.png)

整體的網路架構如下：

```
Internet
  │
  ▼
[ 中華電信 Hinet Modem ] ── IP: https://192.168.1.1 （一定要加https不然找不到）
  │
  ▼
[ WiFi 分享器 ] ── IP: 192.168.0.1
  │  PPPoE 撥號取得固定 IP
  │  Port Forwarding: 外部 222 → 內部 22
  │
  ▼
[ Mac Mini ] ── IP: 192.168.0.188, SSH Port 22
```

設定分四個地方做，下面這些步驟太複雜讓CC開瀏覽器去做也可以，我就這樣搞的：

**1. 中華電信 Modem：登入**

到 `https://192.168.1.1`（注意一定要加 `https`，用 `http` 會找不到）。帳號是 `cht`，密碼的規則是：機型代號前幾碼 + LAN MAC 位址後四碼（小寫）。例如 Alcatel I-040GW 的密碼就是 `40gw` + 後四碼，RTF8207W 就是 `207w` + 後四碼。MAC 位址印在機器背面的貼紙上。（[參考來源](https://iqmore.tw/cht-hinet-alcatel-i-040gw-login)）

![Modem 背面的 MAC 位址貼紙](/images/posts/20260226_mac_mini_claude_code_server/modem_mac_address.png)

**2. 中華電信 Modem：設定 DMZ Host**

登入後到 **進階設定 > NAT > DMZ Host**，把 DMZ Host 設為你的 WiFi 分享器的 IP（通常是 `192.168.1.x`，可以在 Modem 的連線設備清單中找到）。這樣 Modem 會把所有外部流量都轉發到你的 WiFi 分享器。

**3. WiFi 分享器：PPPoE 撥號 + Port Forwarding**

到 WiFi 分享器的管理頁面（通常是 `http://192.168.0.1`），做兩件事：

- **PPPoE 撥號**：把網際網路連線類型從「動態 IP」改成「PPPoE」，填入中華電信提供的帳號密碼。注意帳號要用 `@ip.hinet.net` 結尾才會拿到固定 IP，用 `@hinet.net` 結尾只會拿到浮動 IP。
- **Port Forwarding**：在 NAT / 虛擬伺服器設定裡新增一條規則，外部 Port `222`（不建議直接用 22）→ 內部 IP Mac Mini 的區域網路 IP（例如 `192.168.0.188`）→ 內部 Port `22`。

**4. Mac Mini：開啟遠端登入**

到 **系統設定 > 一般 > 共享 > 遠端登入** → 開啟。這樣 Mac Mini 才會接受 SSH 連線。

設定完就可以從外面連線了：

```bash
ssh -p 222 your-username@your-fixed-ip
```

---

## Step 4：開啟 Screen Sharing（螢幕分享）

有時候需要看到桌面環境（例如安裝 App 或調整系統設定），打開螢幕分享很方便：

1. 到 **系統設定 > 一般 > 共享 > 螢幕共享** → 開啟
2. 從另一台 Mac 開啟 **螢幕共享** App（Spotlight 搜尋 "Screen Sharing"）
3. 輸入 Tailscale IP 或區域網路 IP 即可連入

---

## Step 5：安裝 Claude Code

### 安裝 Node.js（如果還沒有）

```bash
# 用 Homebrew 安裝
brew install node

# 確認版本（需要 Node.js 18+）
node --version
```

### 安裝 Claude Code

```bash
npm install -g @anthropic-ai/claude-code

# 啟動 Claude Code，第一次會引導你登入或設定 API Key
claude
# or enable chrome and yolo mode
claude --dangerously-skip-permissions --chrome
```

---

## Step 6：使用技巧

### 善用 tmux 保持 Session

SSH 斷線後 Claude Code 會中斷，所以強烈建議用 `tmux`：

```bash
# 建立新 session
tmux new -s claude-dev

# 在裡面啟動 claude code
claude

# 要離開時按 Ctrl+B 再按 D（detach）
# 下次 SSH 回來重新 attach：
tmux attach -t claude-dev
```

這樣即使 SSH 斷線，Claude Code 的 session 也不會中斷。

### 用 Headless Mode 跑長時間任務

Claude Code 支援 headless 模式，可配合 crontab 或 airflow 等排程工具設定定時工作或是多併發：

```bash
# 用 -p 指定任務，--allowedTools 控制權限
claude -p "幫我重構 src/ 底下所有的 API handlers，改用新的 error handling pattern" \
  --allowedTools "Read,Write,Edit,Glob,Grep,Bash"
```

---

## 最終確認清單

設定完之後，用以下指令確認一切正常：

```bash
# 確認 Mac 不會睡眠
pmset -g

# 確認 Tailscale 運作中
tailscale status

# 確認 SSH 正常
ssh your-username@your-tailscale-ip "echo 'SSH OK'"

# 確認 Claude Code 正常
claude --version
```

---

## 架構總覽

```
你的筆電（咖啡廳 / 公司 / 家裡）
  │
  ├── Tailscale VPN ──→ Mac Mini (100.85.xx.xx)
  │                        ├── tmux session
  │                        │     └── Claude Code
  │                        └── 你的專案程式碼
  │
  └── 固定 IP（備援）──→ Router ──→ Mac Mini (192.168.0.188:22)
```

---

*有問題歡迎留言討論！*
