# -*- coding: utf-8 -*-
INDEX_HTML = r"""<!DOCTYPE html>
<html lang="ru" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ПБК Wallet</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏦</text></svg>">
<style>
:root {
  --bg: #f5faff; --bg-alt: #ffffff; --card: #ffffff;
  --card-glass: rgba(255,255,255,0.55);
  --sidebar-glass: rgba(255,255,255,0.5);
  --topbar-glass: rgba(255,255,255,0.55);
  --glass-border: rgba(255,255,255,0.7);
  --glass-highlight: rgba(255,255,255,0.6);
  --primary: #2196f3; --primary-dark: #1565c0; --primary-light: #bbdefb; --primary-soft: #e3f2fd;
  --text: #0d2a4a; --text-muted: #5a7996; --border: #d6e6f7;
  --shadow: 0 8px 24px rgba(33,150,243,0.10);
  --danger: #e53935; --success: #2e7d32;
}
[data-theme="dark"] {
  --bg: #0b1c2c; --bg-alt: #102a43; --card: #143654;
    --card-glass: rgba(20,54,84,0.5);
  --sidebar-glass: rgba(16,42,67,0.45);
  --topbar-glass: rgba(16,42,67,0.5);
  --glass-border: rgba(255,255,255,0.12);
  --glass-highlight: rgba(255,255,255,0.08);
  --primary: #64b5f6; --primary-dark: #2196f3; --primary-light: #1e4d75; --primary-soft: #17385a;
  --text: #eaf3fb; --text-muted: #9fb8d0; --border: #1e4d75;
  --shadow: 0 8px 24px rgba(0,0,0,0.35);
  --danger: #ef5350; --success: #66bb6a;
}
[data-theme="graphite"] {
  --card-glass: rgba(42,42,42,0.5);
  --sidebar-glass: rgba(36,36,36,0.55);
  --topbar-glass: rgba(36,36,36,0.55);
  --glass-border: rgba(255,255,255,0.1);
  --glass-highlight: rgba(255,255,255,0.06);
  --topbar-glass: rgba(36,36,36,0.75);
  --primary: #90a4ae; --primary-dark: #607d8b; --primary-light: #37474f; --primary-soft: #37474f;
  --text: #eceff1; --text-muted: #b0bec5; --border: #37474f;
  --shadow: 0 8px 24px rgba(0,0,0,0.5);
  --danger: #ef5350; --success: #66bb6a;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  transition: background .25s, color .25s;
  min-height: 100vh;
  position: relative;
}
body.glass {
  background:
    radial-gradient(circle at 15% 20%, rgba(33,150,243,0.25), transparent 45%),
    radial-gradient(circle at 85% 80%, rgba(124,77,255,0.22), transparent 50%),
    radial-gradient(circle at 60% 30%, rgba(0,229,255,0.15), transparent 45%),
    radial-gradient(circle at 30% 90%, rgba(255,64,129,0.15), transparent 50%),
    var(--bg);
  background-attachment: fixed;
}
[data-theme="dark"] body.glass {
  background:
    radial-gradient(circle at 15% 20%, rgba(33,150,243,0.35), transparent 45%),
    radial-gradient(circle at 85% 80%, rgba(124,77,255,0.3), transparent 50%),
    radial-gradient(circle at 60% 30%, rgba(0,229,255,0.2), transparent 45%),
    radial-gradient(circle at 30% 90%, rgba(255,64,129,0.2), transparent 50%),
    var(--bg);
  background-attachment: fixed;
}
button { font-family: inherit; cursor: pointer; }
input, button { font-size: 15px; }
.hidden { display: none !important; }

/* iOS 26 Liquid Glass — сильный блюр + saturate + светлая рамка */
body.glass .sidebar {
  background: var(--sidebar-glass);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border-right: 1px solid var(--glass-border);
  box-shadow: inset -1px 0 0 var(--glass-highlight), 0 8px 32px rgba(0,0,0,0.06);
}
body.glass .topbar {
  background: var(--topbar-glass);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border-bottom: 1px solid var(--glass-border);
  box-shadow: inset 0 -1px 0 var(--glass-highlight);
}
body.glass .card {
  background: var(--card-glass);
  backdrop-filter: blur(30px) saturate(160%);
  -webkit-backdrop-filter: blur(30px) saturate(160%);
  border: 1px solid var(--glass-border);
  box-shadow:
    inset 0 1px 0 var(--glass-highlight),
    inset 0 -1px 0 rgba(0,0,0,0.03),
    0 8px 32px rgba(0,0,0,0.08);
}
body.glass .auth-card {
  background: var(--card-glass);
  backdrop-filter: blur(50px) saturate(180%);
  -webkit-backdrop-filter: blur(50px) saturate(180%);
  border: 1px solid var(--glass-border);
  box-shadow:
    inset 0 1px 0 var(--glass-highlight),
    0 20px 60px rgba(0,0,0,0.15);
}
body.glass .topbar-user {
  background: var(--card-glass);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--glass-border);
}
body.glass .btn {
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
}
body.glass .balance-card {
  backdrop-filter: blur(30px) saturate(180%);
  -webkit-backdrop-filter: blur(30px) saturate(180%);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.3),
    0 12px 40px rgba(33,150,243,.4);
}
body.glass .chat-messages {
  background: var(--card-glass);
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
  border: 1px solid var(--glass-border);
}

.auth-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; background: linear-gradient(135deg, var(--primary-soft) 0%, var(--bg) 60%); }
.auth-card { background: var(--card); border-radius: 24px; padding: 40px 32px; width: 100%; max-width: 420px; box-shadow: var(--shadow); border: 1px solid var(--border); position: relative; }
.auth-logo { display: flex; align-items: center; justify-content: center; gap: 10px; font-weight: 800; font-size: 28px; color: var(--primary-dark); margin-bottom: 8px; }
.auth-logo svg { color: var(--primary); }
.auth-disclaimer { text-align: center; color: var(--text-muted); font-size: 11px; margin-bottom: 20px; }
.auth-tabs { display: flex; gap: 8px; margin-bottom: 20px; }
.tab-btn { flex: 1; padding: 10px; border: none; border-radius: 12px; background: var(--primary-soft); color: var(--primary-dark); font-weight: 600; }
.tab-btn.active { background: var(--primary); color: #fff; }
.auth-form { display: flex; flex-direction: column; gap: 12px; }
.auth-form input { padding: 14px 16px; border-radius: 12px; border: 1px solid var(--border); background: var(--bg-alt); color: var(--text); }
.auth-hint { color: var(--text-muted); font-size: 12px; text-align: center; }
.auth-theme { position: absolute; top: 16px; right: 16px; }
.theme-toggle { background: var(--primary-soft); color: var(--primary-dark); border: none; border-radius: 50%; width: 40px; height: 40px; font-size: 18px; }

.btn { border: none; padding: 12px 20px; border-radius: 12px; font-weight: 600; background: var(--primary); color: #fff; box-shadow: 0 4px 12px rgba(33,150,243,.25); }
.btn:hover { background: var(--primary-dark); }
.btn-ghost { background: transparent; color: var(--primary-dark); box-shadow: none; border: 1px solid var(--border); }
.btn-danger { background: var(--danger); }
.btn-small { padding: 6px 12px; font-size: 13px; }

.app-body { display: flex; min-height: 100vh; }
.sidebar { width: 250px; background: var(--card); border-right: 1px solid var(--border); padding: 20px 14px; display: flex; flex-direction: column; gap: 6px; position: sticky; top: 0; height: 100vh; transition: background .25s; overflow-y: auto; }
.sidebar-logo { display: flex; align-items: center; gap: 12px; font-weight: 900; font-size: 24px; padding: 8px 10px 22px; background: linear-gradient(135deg, #2196f3, #1565c0, #7c4dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.sidebar-logo svg { color: #2196f3; filter: drop-shadow(0 2px 6px rgba(33,150,243,.4)); }

.nav-divider { height: 1px; background: var(--border); margin: 10px 12px; opacity: 0.6; }

.nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 14px; color: var(--text); text-decoration: none; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border-left: 3px solid transparent; }
.nav-item:hover { background: var(--primary-soft); transform: translateX(3px); border-left-color: var(--primary); }
.nav-item:hover .nav-icon { transform: scale(1.2) rotate(-5deg); }
.nav-item.active { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: #fff; box-shadow: 0 6px 20px rgba(33,150,243,.4); border-left-color: transparent; }
.nav-item.active .nav-icon { filter: drop-shadow(0 0 6px rgba(255,255,255,.6)); }
.nav-icon { font-size: 20px; transition: transform 0.2s ease; display: inline-block; width: 26px; text-align: center; }

.nav-item[data-page="wallet"]:hover { background: linear-gradient(135deg, #e3f2fd, #bbdefb); }
.nav-item[data-page="transfer"]:hover { background: linear-gradient(135deg, #e8f5e9, #c8e6c9); }
.nav-item[data-page="chat"]:hover { background: linear-gradient(135deg, #fff3e0, #ffe0b2); }
.nav-item[data-page="about"]:hover { background: linear-gradient(135deg, #f3e5f5, #e1bee7); }
.nav-item[data-page="support"]:hover { background: linear-gradient(135deg, #ffebee, #ffcdd2); }
.nav-item[data-page="settings"]:hover { background: linear-gradient(135deg, #eceff1, #cfd8dc); }
.nav-item[data-page="profile"]:hover { background: linear-gradient(135deg, #e0f7fa, #b2ebf2); }
.nav-item[data-page="admin"]:hover { background: linear-gradient(135deg, #fffde7, #fff9c4); }

[data-theme="dark"] .nav-item[data-page="wallet"]:hover { background: linear-gradient(135deg, #1565c0, #0d47a1); }
[data-theme="dark"] .nav-item[data-page="transfer"]:hover { background: linear-gradient(135deg, #2e7d32, #1b5e20); }
[data-theme="dark"] .nav-item[data-page="chat"]:hover { background: linear-gradient(135deg, #e65100, #bf360c); }
[data-theme="dark"] .nav-item[data-page="about"]:hover { background: linear-gradient(135deg, #6a1b9a, #4a148c); }
[data-theme="dark"] .nav-item[data-page="support"]:hover { background: linear-gradient(135deg, #c62828, #8e0000); }
[data-theme="dark"] .nav-item[data-page="settings"]:hover { background: linear-gradient(135deg, #455a64, #263238); }
[data-theme="dark"] .nav-item[data-page="profile"]:hover { background: linear-gradient(135deg, #00838f, #006064); }
[data-theme="dark"] .nav-item[data-page="admin"]:hover { background: linear-gradient(135deg, #f9a825, #f57f17); }

.sidebar-bottom { margin-top: auto; padding-top: 12px; border-top: 1px solid var(--border); display: flex; justify-content: center; }

.main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.topbar { padding: 16px 28px; border-bottom: 1px solid var(--border); background: var(--card); display: flex; justify-content: flex-end; align-items: center; gap: 14px; }
.topbar-user { display: flex; align-items: center; gap: 10px; padding: 8px 14px; background: var(--primary-soft); border-radius: 999px; font-weight: 600; color: var(--primary-dark); }
.topbar-uid { opacity: .7; font-weight: 500; font-size: 13px; }
.content { padding: 28px; max-width: 1200px; width: 100%; }
.page { display: none; }
.page.active { display: block; }

.card { background: var(--card); border-radius: 20px; padding: 24px; box-shadow: var(--shadow); border: 1px solid var(--border); margin-bottom: 20px; }
.card h3 { margin-bottom: 12px; color: var(--primary-dark); }
.muted { color: var(--text-muted); font-size: 14px; margin-bottom: 12px; }
input[type="number"], input[type="text"], input[type="password"], select { width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--border); background: var(--bg-alt); color: var(--text); margin-bottom: 10px; }

.balance-card { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: #fff; border-radius: 24px; padding: 32px; margin-bottom: 24px; }
.balance-label { opacity: .85; font-size: 13px; letter-spacing: 1.5px; }
.balance-amount { font-size: 44px; font-weight: 800; margin: 6px 0 8px; }
.balance-uid { opacity: .85; font-size: 14px; }

.actions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }

.tap-coin { width: 180px; height: 180px; border-radius: 50%; border: none; background: linear-gradient(135deg, #ffd700, #ff9800); cursor: pointer; box-shadow: 0 8px 24px rgba(255,152,0,.5); display: flex; align-items: center; justify-content: center; margin: 20px auto; user-select: none; }
.tap-coin:active { transform: scale(0.92); }
.tap-coin:disabled { opacity: 0.5; cursor: wait; }
.coin-icon { font-size: 80px; }
.tap-counter { color: var(--text-muted); font-size: 14px; margin-top: 10px; }
.tap-counter b { color: var(--primary-dark); font-size: 18px; }

.tx-list { list-style: none; }
.tx-list li { padding: 14px 0; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; gap: 12px; }
.tx-list li:last-child { border-bottom: none; }
.tx-comment { color: var(--text-muted); font-size: 13px; margin-top: 4px; }
.tx-amount { font-weight: 700; white-space: nowrap; }
.tx-amount.plus { color: var(--success); }
.tx-amount.minus { color: var(--danger); }

.chat-card { display: flex; flex-direction: column; height: calc(100vh - 180px); min-height: 400px; }
.chat-messages { flex: 1; overflow-y: auto; padding: 14px; background: var(--bg-alt); border-radius: 14px; border: 1px solid var(--border); margin-bottom: 12px; font-size: 14px; line-height: 1.6; }
.chat-messages > div { padding: 4px 0; }
.chat-input-row { display: flex; gap: 10px; }
.chat-input-row input { margin-bottom: 0; flex: 1; }

.team-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-top: 12px; }
.team-card { text-align: center; padding: 20px 16px; border-radius: 16px; background: var(--primary-soft); }
.team-avatar { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin: 0 auto 12px; display: block; border: 3px solid var(--primary); background: var(--card); box-shadow: 0 4px 16px rgba(33,150,243,.3); }
.team-name { font-weight: 700; color: var(--primary-dark); font-size: 17px; }
.team-role { color: var(--text-muted); font-size: 13px; margin-top: 4px; }

.profile-row { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
.profile-avatar-big { font-size: 64px; width: 96px; height: 96px; display: flex; align-items: center; justify-content: center; background: var(--primary-soft); border-radius: 50%; }
.profile-username { font-size: 24px; font-weight: 700; color: var(--primary-dark); }

.avatar-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin: 12px 0 20px; }
.avatar-option { font-size: 28px; padding: 10px; border-radius: 12px; border: 2px solid transparent; background: var(--primary-soft); }
.avatar-option.selected { border-color: var(--primary); }

.settings-row { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid var(--border); }
.settings-label { font-weight: 600; }
.settings-desc { color: var(--text-muted); font-size: 13px; }

.switch { position: relative; display: inline-block; width: 52px; height: 28px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: var(--border); transition: .3s; border-radius: 28px; }
.slider:before { position: absolute; content: ""; height: 22px; width: 22px; left: 3px; bottom: 3px; background: white; transition: .3s; border-radius: 50%; }
input:checked + .slider { background: var(--primary); }
input:checked + .slider:before { transform: translateX(24px); }

#toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(80px); background: var(--primary-dark); color: #fff; padding: 14px 22px; border-radius: 12px; max-width: 90%; transition: all .3s; z-index: 100; opacity: 0; }
#toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
#toast.error { background: var(--danger); }
#toast.success { background: var(--success); }

.admin-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.admin-table th, .admin-table td { padding: 10px; text-align: left; border-bottom: 1px solid var(--border); }
.admin-table th { color: var(--primary-dark); font-weight: 700; }
.admin-table tr:hover { background: var(--primary-soft); }

@media (max-width: 720px) {
  .sidebar { width: 68px; padding: 14px 8px; }
  .sidebar-logo span, .nav-item span:not(.nav-icon) { display: none; }
  .nav-item { justify-content: center; padding: 12px; }
  .content { padding: 16px; }
  .avatar-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
</head><body>

<div class="auth-wrap" id="auth-screen">
  <div class="auth-card">
    <div class="auth-theme">
      <button class="theme-toggle" id="theme-toggle-auth" onclick="toggleTheme()">🌙</button>
    </div>
    <div class="auth-logo">
      <svg viewBox="0 0 24 24" width="34" height="34" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2 L12 6"/><path d="M9 22 L12 6 L15 22"/><path d="M10 15 L14 15"/><path d="M8.5 22 L15.5 22"/>
      </svg>
      <span>ПБК</span>
    </div>
    <div class="auth-disclaimer">Демонстрационный проект. Все операции виртуальные.</div>

    <div class="auth-tabs">
      <button class="tab-btn active" id="tab-login" onclick="switchTab('login')">Вход</button>
      <button class="tab-btn" id="tab-register" onclick="switchTab('register')">Регистрация</button>
    </div>

    <form class="auth-form" id="form-login" onsubmit="doLogin(event)">
      <input type="text" id="login-username" placeholder="Ник" required minlength="3" maxlength="20">
      <input type="password" id="login-password" placeholder="Пароль" required minlength="3" maxlength="20">
      <button class="btn" type="submit">Войти</button>
    </form>

    <form class="auth-form hidden" id="form-register" onsubmit="doRegister(event)">
      <input type="text" id="reg-username" placeholder="Ник (3–20 символов)" required minlength="3" maxlength="20">
      <input type="password" id="reg-password" placeholder="Пароль (3–20 символов)" required minlength="3" maxlength="20">
      <input type="password" id="reg-password2" placeholder="Подтвердите пароль" required minlength="3" maxlength="20">
      <button class="btn" type="submit">Создать аккаунт</button>
      <div class="auth-hint">Вам будет присвоен уникальный UID</div>
    </form>
  </div>
</div>

<div class="app-body hidden" id="app-screen">
  <aside class="sidebar">
    <div class="sidebar-logo">
      <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2 L12 6"/>
        <path d="M9 22 L12 6 L15 22"/>
        <path d="M10 15 L14 15"/>
        <path d="M8.5 22 L15.5 22"/>
      </svg>
      <span>ПБК</span>
    </div>

    <a class="nav-item active" data-page="wallet" onclick="switchPage('wallet')">
      <span class="nav-icon">🏦</span><span>Кошелёк</span>
    </a>
    <a class="nav-item" data-page="transfer" onclick="switchPage('transfer')">
      <span class="nav-icon">💸</span><span>Перевести</span>
    </a>
    <a class="nav-item" data-page="chat" onclick="switchPage('chat')">
      <span class="nav-icon">💬</span><span>Чат</span>
    </a>

    <div class="nav-divider"></div>

    <a class="nav-item" data-page="about" onclick="switchPage('about')">
      <span class="nav-icon">👥</span><span>О нас</span>
    </a>
    <a class="nav-item" data-page="support" onclick="switchPage('support')">
      <span class="nav-icon">🆘</span><span>Поддержка</span>
    </a>

    <div class="nav-divider"></div>

    <a class="nav-item" data-page="settings" onclick="switchPage('settings')">
      <span class="nav-icon">⚙️</span><span>Настройки</span>
    </a>
    <a class="nav-item" data-page="profile" onclick="switchPage('profile')">
      <span class="nav-icon">👤</span><span>Профиль</span>
    </a>
    <a class="nav-item hidden" data-page="admin" id="admin-nav" onclick="switchPage('admin')">
      <span class="nav-icon">🛡</span><span>Админка</span>
    </a>

    <div class="sidebar-bottom">
      <button class="theme-toggle" id="theme-toggle-app" onclick="toggleTheme()">🌙</button>
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <div class="topbar-user">
        <span id="top-avatar">👤</span>
        <span id="top-username">—</span>
        <span class="topbar-uid" id="top-uid">#—</span>
      </div>
    </div>

    <div class="content">

      <section class="page active" id="page-wallet">
        <div class="balance-card">
          <div class="balance-label">ТЕКУЩИЙ БАЛАНС</div>
          <div class="balance-amount" id="balance">— ₽</div>
          <div class="balance-uid">UID: <span id="wallet-uid">#—</span></div>
        </div>
        <div class="actions-grid">
          <div class="card" style="text-align: center;">
            <h3>Заработать</h3>
            <div class="muted">Тапай монетку — +2₽ за тап</div>
            <button class="tap-coin" onclick="doTap()" id="tap-btn">
              <span class="coin-icon">💰</span>
            </button>
            <div class="tap-counter">Всего тапов: <b id="total-taps">0</b></div>
          </div>
          <div class="card">
            <h3>Снять</h3>
            <div class="muted">Иногда даже работает!</div>
            <input type="number" id="withdraw-amount" placeholder="Сумма, ₽" min="1">
            <button class="btn btn-ghost" onclick="doWithdraw()">Снять</button>
          </div>
        </div>
        <div class="card">
          <h3>История операций</h3>
          <ul class="tx-list" id="tx-list"><li class="muted">Загрузка...</li></ul>
        </div>
      </section>

      <section class="page" id="page-transfer">
        <div class="card">
          <h3>Перевод по UID</h3>
          <div class="muted">Введите UID получателя (4 цифры).</div>
          <input type="number" id="transfer-uid" placeholder="UID получателя" min="1000" max="9999">
          <input type="number" id="transfer-amount" placeholder="Сумма, ₽" min="1">
          <button class="btn" onclick="doTransfer()">Перевести</button>
        </div>
      </section>

      <section class="page" id="page-chat">
        <div class="card chat-card">
          <h3>Общий чат</h3>
          <div class="chat-messages" id="chat-messages"></div>
          <div class="chat-input-row">
            <input type="text" id="chat-input" placeholder="Написать сообщение..." onkeydown="if(event.key==='Enter')sendChat()">
            <button class="btn" onclick="sendChat()">Отправить</button>
          </div>
        </div>
      </section>

      <section class="page" id="page-about">
        <div class="card">
          <h3>О нас</h3>
          <div class="muted">Команда ПБК Wallet</div>
          <div class="team-grid">
            <div class="team-card">
              <img class="team-avatar" src="__AVATAR_TAKAYO__" alt="Takayo">
              <div class="team-name">Takayo</div>
              <div class="team-role">CEO</div>
            </div>
            <div class="team-card">
              <img class="team-avatar" src="__AVATAR_SANDGAR__" alt="Sandgar">
              <div class="team-name">Sandgar</div>
              <div class="team-role">CTO</div>
            </div>
            <div class="team-card">
              <img class="team-avatar" src="__AVATAR_LAZARET__" alt="Лазарет">
              <div class="team-name">Лазарет 21 🇯🇲</div>
              <div class="team-role">Дизайнер</div>
            </div>
          </div>
        </div>
      </section>

      <section class="page" id="page-support">
        <div class="card chat-card">
          <h3>Поддержка</h3>
          <div class="muted">Бот отвечает 24/7 (или никогда)</div>
          <div class="chat-messages" id="support-messages"></div>
          <div class="chat-input-row">
            <input type="text" id="support-input" placeholder="Ваш вопрос..." onkeydown="if(event.key==='Enter')sendSupport()">
            <button class="btn" onclick="sendSupport()">Отправить</button>
          </div>
        </div>
      </section>

      <section class="page" id="page-settings">
        <div class="card">
          <h3>Настройки</h3>
          <div class="settings-row">
            <div><div class="settings-label">Тема оформления</div><div class="settings-desc">Светлая, тёмная, системная или графит</div></div>
            <select id="setting-theme" onchange="applyTheme(this.value)" style="width:auto;margin:0;min-width:160px;">
              <option value="light">☀️ Светлая</option>
              <option value="dark">🌙 Тёмная</option>
              <option value="system">💻 Системная</option>
              <option value="graphite">⬛ Графит</option>
            </select>
          </div>
          <div class="settings-row">
            <div><div class="settings-label">Язык интерфейса</div><div class="settings-desc">Русский или English</div></div>
            <select id="setting-lang" onchange="applyLang(this.value)" style="width:auto;margin:0;min-width:160px;">
              <option value="ru">🇷🇺 Русский</option>
              <option value="en">🇬🇧 English</option>
            </select>
          </div>
          <div class="settings-row">
            <div><div class="settings-label">Жидкое стекло</div><div class="settings-desc">Полупрозрачные панели с размытием</div></div>
            <label class="switch">
              <input type="checkbox" id="setting-glass" onchange="toggleGlass(this.checked)">
              <span class="slider"></span>
            </label>
          </div>
        </div>
      </section>

      <section class="page" id="page-profile">
        <div class="card">
          <h3>Профиль</h3>
          <div class="profile-row">
            <div class="profile-avatar-big" id="profile-avatar">👤</div>
            <div>
              <div class="profile-username" id="profile-username">—</div>
              <div class="muted" style="margin:4px 0 0;">UID: <span id="profile-uid">#—</span></div>
            </div>
          </div>
          <h4 style="margin-bottom:6px;">Сменить ник</h4>
          <div class="muted">3–20 символов, только уникальный</div>
          <input type="text" id="new-username" placeholder="Новый ник" minlength="3" maxlength="20">
          <button class="btn" onclick="changeUsername()">Сохранить ник</button>
          <h4 style="margin: 20px 0 6px;">Выбор аватара</h4>
          <div class="muted">Из готовых или загрузите свою картинку</div>
          <div class="avatar-grid" id="avatar-grid"></div>
          <input type="file" id="avatar-file" accept="image/*" onchange="uploadAvatar(event)" style="margin-top:10px;">
          <button class="btn btn-danger" onclick="logout()" style="margin-top: 20px;">Выйти из аккаунта</button>
        </div>
      </section>

      <section class="page" id="page-admin">
        <div class="card">
          <h3>🛡 Админка</h3>
          <div class="muted">Управление пользователями ПБК Wallet</div>
          <div id="admin-users-container"><div class="muted">Загрузка...</div></div>
        </div>
      </section>

    </div>
  </main>
</div>

<div id="toast"></div><script>
const TEAM = [
  { name: "Takayo", role: "CEO" },
  { name: "Sandgar", role: "CTO" },
  { name: "Лазарет 21 🇯🇲", role: "Дизайнер" }
];

function showToast(msg, type) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'show ' + (type || '');
  clearTimeout(el._t);
  el._t = setTimeout(() => el.className = '', 3200);
}

function resolveTheme(theme) {
  if (theme === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return theme;
}
function applyTheme(theme) {
  localStorage.setItem("pbk-theme", theme);
  document.documentElement.setAttribute("data-theme", resolveTheme(theme));
  const sel = document.getElementById("setting-theme");
  if (sel) sel.value = theme;
  updateThemeIcons();
}
function toggleTheme() {
  const cur = localStorage.getItem("pbk-theme") || "light";
  const next = (cur === "dark" || cur === "graphite") ? "light" : "dark";
  applyTheme(next);
}
function updateThemeIcons() {
  const cur = localStorage.getItem("pbk-theme") || "light";
  const icon = (cur === "dark" || cur === "graphite") ? "☀️" : "🌙";
  const a = document.getElementById('theme-toggle-auth');
  const b = document.getElementById('theme-toggle-app');
  if (a) a.textContent = icon;
  if (b) b.textContent = icon;
}
function applyLang(lang) { localStorage.setItem("pbk-lang", lang); }
function toggleGlass(on) {
  localStorage.setItem("pbk-glass", on ? "1" : "0");
  document.body.classList.toggle("glass", on);
}

const API = '';
function getToken() { return localStorage.getItem('pbk-token'); }
function setToken(t) { localStorage.setItem('pbk-token', t); }
function clearToken() { localStorage.removeItem('pbk-token'); }

async function api(url, opts) {
  opts = opts || {};
  opts.headers = opts.headers || {};
  const tok = getToken();
  if (tok) opts.headers['Authorization'] = 'Bearer ' + tok;
  if (opts.body && !(opts.body instanceof FormData) && typeof opts.body === 'object') {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(opts.body);
  }
  const res = await fetch(API + url, opts);
  if (res.status === 401) { clearToken(); showAuth(); throw new Error('unauthorized'); }
  return res;
}

function switchTab(which) {
  document.getElementById('tab-login').classList.toggle('active', which === 'login');
  document.getElementById('tab-register').classList.toggle('active', which === 'register');
  document.getElementById('form-login').classList.toggle('hidden', which !== 'login');
  document.getElementById('form-register').classList.toggle('hidden', which !== 'register');
}

async function doRegister(e) {
  e.preventDefault();
  const username = document.getElementById('reg-username').value.trim();
  const p1 = document.getElementById('reg-password').value;
  const p2 = document.getElementById('reg-password2').value;
  if (p1 !== p2) { showToast('Пароли не совпадают', 'error'); return; }
  if (p1.length < 3 || p1.length > 20) { showToast('Пароль: 3–20 символов', 'error'); return; }
  const device_hash = await getDeviceFingerprint();
  const device_type = getDeviceType();
  const device_browser = getBrowser();
  const device_os = getOS();
  const res = await fetch('/api/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password: p1, device_hash, device_type, device_browser, device_os})
  });
  const data = await res.json();
  if (!res.ok) { showToast(data.detail || 'Ошибка', 'error'); return; }
  setToken(data.access_token);
  showToast('Добро пожаловать! UID: #' + data.uid, 'success');
  setTimeout(() => { showApp(); }, 500);
}

async function doLogin(e) {
  e.preventDefault();
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const body = new URLSearchParams();
  body.append('username', username);
  body.append('password', password);
  const res = await fetch('/api/login', {method: 'POST', body});
  const data = await res.json();
  if (!res.ok) { showToast(data.detail || 'Ошибка входа', 'error'); return; }
  setToken(data.access_token);
  showToast('Успешный вход', 'success');
  setTimeout(() => { showApp(); }, 400);
}

function logout() {
  clearToken();
  if (ws) { try { ws.close(); } catch(e){} ws = null; }
  showAuth();
}

function showAuth() {
  document.getElementById('auth-screen').classList.remove('hidden');
  document.getElementById('app-screen').classList.add('hidden');
}

async function showApp() {
  document.getElementById('auth-screen').classList.add('hidden');
  document.getElementById('app-screen').classList.remove('hidden');
  await loadMe();
  await loadTransactions();
  await loadChat();
  renderAvatarGrid();
  updateThemeIcons();
  document.getElementById("setting-theme").value = localStorage.getItem("pbk-theme") || "light";
  document.getElementById("setting-lang").value = localStorage.getItem("pbk-lang") || "ru";
  const glass = localStorage.getItem("pbk-glass") === "1";
  document.getElementById("setting-glass").checked = glass;
  document.body.classList.toggle("glass", glass);
}

function switchPage(name) {
  document.querySelectorAll('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.page === name));
  document.querySelectorAll('.page').forEach(el => el.classList.toggle('active', el.id === 'page-' + name));
  if (name === 'chat') setTimeout(scrollChatBottom, 60);
  if (name === 'support') setTimeout(scrollSupportBottom, 60);
  if (name === 'admin') loadAdminUsers();
}

async function loadMe() {
  const res = await api('/api/me');
  const d = await res.json();
  document.getElementById('balance').textContent = d.balance.toFixed(2) + ' ₽';
  document.getElementById('wallet-uid').textContent = '#' + d.uid;
  document.getElementById('top-username').textContent = d.username;
  document.getElementById('top-avatar').textContent = (d.avatar && d.avatar.length <= 4) ? d.avatar : '👤';
  document.getElementById('top-uid').textContent = '#' + d.uid;
  document.getElementById('profile-username').textContent = d.username;
  document.getElementById('profile-uid').textContent = '#' + d.uid;
  window._currentAvatar = d.avatar;
  updateProfileAvatar(d.avatar);
  if (d.is_admin) {
    document.getElementById('admin-nav').classList.remove('hidden');
  } else {
    document.getElementById('admin-nav').classList.add('hidden');
  }
  try {
    const tapsRes = await api('/api/transactions');
    const txs = await tapsRes.json();
    const tapCount = txs.filter(t => t.type === 'tap').length;
    const totalEl = document.getElementById('total-taps');
    if (totalEl) totalEl.textContent = tapCount;
  } catch(e) {}
}

function updateProfileAvatar(av) {
  const el = document.getElementById('profile-avatar');
  if (!el) return;
  if (av && av.startsWith('data:image')) el.innerHTML = '<img src="' + av + '" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">';
  else el.textContent = av || '👤';
}

async function doTap() {
  const btn = document.getElementById('tap-btn');
  btn.disabled = true;
  try {
    const res = await api('/api/tap', {method: 'POST'});
    const d = await res.json();
    if (res.ok) {
      document.getElementById('balance').textContent = d.balance.toFixed(2) + ' ₽';
      document.getElementById('total-taps').textContent = d.total_taps;
      showToast('+2₽', 'success');
      await loadTransactions();
    }
  } catch(e) {}
  btn.disabled = false;
}

async function doWithdraw() {
  const amt = parseFloat(document.getElementById('withdraw-amount').value);
  if (!amt || amt <= 0) { showToast('Введите сумму', 'error'); return; }
  const res = await api('/api/withdraw', {method:'POST', body: {amount: amt}});
  const d = await res.json();
  showToast(d.message, 'error');
  document.getElementById('withdraw-amount').value = '';
  await loadTransactions();
}

async function loadTransactions() {
  const res = await api('/api/transactions');
  const list = await res.json();
  const ul = document.getElementById('tx-list');
  if (!list.length) { ul.innerHTML = '<li class="muted">Пока пусто</li>'; return; }
  ul.innerHTML = list.map(t => {
    const plus = ['deposit','bonus','transfer_in','tap','admin_gift'].includes(t.type) && t.amount > 0;
    const cls = plus ? 'plus' : 'minus';
    const sign = plus ? '+' : '';
    return `<li><div><div>${escapeHtml(t.comment)}</div><div class="tx-comment">${t.created_at}</div></div><div class="tx-amount ${cls}">${sign}${t.amount}₽</div></li>`;
  }).join('');
}

async function doTransfer() {
  const uid = parseInt(document.getElementById('transfer-uid').value);
  const amt = parseFloat(document.getElementById('transfer-amount').value);
  if (!uid || !amt || amt <= 0) { showToast('Заполните все поля', 'error'); return; }
  const res = await api('/api/transfer', {method:'POST', body: {to_uid: uid, amount: amt}});
  const d = await res.json();
  if (!res.ok) { showToast(d.detail || 'Ошибка', 'error'); return; }
  showToast(d.message, 'success');
  document.getElementById('transfer-uid').value = '';
  document.getElementById('transfer-amount').value = '';
  await loadMe();
  await loadTransactions();
}

let ws = null;

async function loadChat() {
  try {
    const res = await api('/api/messages');
    const list = await res.json();
    const box = document.getElementById('chat-messages');
    box.innerHTML = '';
    list.forEach(m => {
      const div = document.createElement('div');
      div.textContent = `[${m.created_at}] ${m.username}: ${m.text}`;
      box.appendChild(div);
    });
    scrollChatBottom();
  } catch(e) {}
  connectWS();
}

function connectWS() {
  if (ws) return;
  const tok = getToken();
  if (!tok) return;
  const url = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/chat?token=' + encodeURIComponent(tok);
  try { ws = new WebSocket(url); } catch(e) { return; }
  ws.onmessage = (ev) => {
    const box = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.textContent = ev.data;
    box.appendChild(div);
    scrollChatBottom();
  };
  ws.onclose = () => { ws = null; };
}

function sendChat() {
  const inp = document.getElementById('chat-input');
  const text = inp.value.trim();
  if (!text) return;
  if (!ws || ws.readyState !== 1) { showToast('Нет соединения...', 'error'); connectWS(); return; }
  ws.send(text);
  inp.value = '';
}

function scrollChatBottom() {
  const box = document.getElementById('chat-messages');
  if (box) box.scrollTop = box.scrollHeight;
}

async function sendSupport() {
  const inp = document.getElementById('support-input');
  const text = inp.value.trim();
  if (!text) return;
  addSupportMsg('Вы: ' + text);
  inp.value = '';
  const res = await api('/api/support', {method:'POST', body: {message: text}});
  const d = await res.json();
  addSupportMsg('Поддержка: ' + d.reply);
}
function addSupportMsg(text) {
  const box = document.getElementById('support-messages');
  const div = document.createElement('div');
  div.textContent = text;
  box.appendChild(div);
  scrollSupportBottom();
}
function scrollSupportBottom() {
  const box = document.getElementById('support-messages');
  if (box) box.scrollTop = box.scrollHeight;
}

const AVATARS = ['👤','🏦','💠','🅿️','🦊','🐼','🐸','🦉','🐙','🦄','🐧','🐯'];
function renderAvatarGrid() {
  const grid = document.getElementById('avatar-grid');
  grid.innerHTML = '';
  AVATARS.forEach(a => {
    const b = document.createElement('button');
    b.className = 'avatar-option' + (a === window._currentAvatar ? ' selected' : '');
    b.textContent = a;
    b.onclick = () => setAvatar(a);
    grid.appendChild(b);
  });
}
async function setAvatar(a) {
  const res = await api('/api/avatar', {method:'POST', body: {avatar: a}});
  const d = await res.json();
  if (!res.ok) { showToast(d.detail || 'Ошибка', 'error'); return; }
  window._currentAvatar = a;
  updateProfileAvatar(a);
  document.getElementById('top-avatar').textContent = a;
  renderAvatarGrid();
  showToast('Аватар обновлён', 'success');
}

async function uploadAvatar(e) {
  const file = e.target.files[0];
  if (!file) return;
  if (file.size > 2 * 1024 * 1024) { showToast('Файл больше 2 МБ', 'error'); return; }
  const reader = new FileReader();
  reader.onload = async () => {
    const dataUrl = reader.result;
    const res = await api('/api/avatar', {method:'POST', body: {avatar: dataUrl}});
    const d = await res.json();
    if (!res.ok) { showToast(d.detail || 'Ошибка', 'error'); return; }
    window._currentAvatar = dataUrl;
    updateProfileAvatar(dataUrl);
    document.getElementById('top-avatar').textContent = '👤';
    renderAvatarGrid();
    showToast('Аватар загружен', 'success');
  };
  reader.readAsDataURL(file);
}

async function changeUsername() {
  const newName = document.getElementById('new-username').value.trim();
  if (newName.length < 3 || newName.length > 20) { showToast('Ник: 3–20 символов', 'error'); return; }
  const res = await api('/api/username', {method:'POST', body: {username: newName}});
  const d = await res.json();
  if (!res.ok) { showToast(d.detail || 'Ошибка', 'error'); return; }
  setToken(d.access_token);
  document.getElementById('new-username').value = '';
  showToast('Ник изменён', 'success');
  await loadMe();
}

async function loadAdminUsers() {
  const container = document.getElementById('admin-users-container');
  container.innerHTML = '<div class="muted">Загрузка...</div>';
  try {
    const res = await api('/api/admin/users');
    if (!res.ok) { container.innerHTML = '<div class="muted">Нет доступа</div>'; return; }
    const users = await res.json();
    let html = '<table class="admin-table"><thead><tr>' +
      '<th>UID</th><th>Ник</th><th>Баланс</th><th>Устройство</th><th>Браузер</th><th>ОС</th><th>Регистрация</th><th>Действия</th>' +
      '</tr></thead><tbody>';
    users.forEach(u => {
      const devIcon = u.device_type === 'mobile' ? '📱' : u.device_type === 'tablet' ? '📱' : '💻';
      html += `<tr>
        <td>#${u.uid}</td>
        <td>${escapeHtml(u.username)}</td>
        <td>${u.balance.toFixed(2)}₽</td>
        <td>${devIcon} ${u.device_type}</td>
        <td>${u.device_browser}</td>
        <td>${u.device_os}</td>
        <td style="font-size:11px;">${u.created_at.slice(0,16)}</td>
        <td>
          <button class="btn btn-small" onclick="adminGiveMoney(${u.uid}, 100)">+100</button>
          <button class="btn btn-small" onclick="adminGiveMoney(${u.uid}, 1000)">+1000</button>
        </td>
      </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
  } catch(e) {
    container.innerHTML = '<div class="muted">Ошибка загрузки</div>';
  }
}

async function adminGiveMoney(uid, amount) {
  const res = await api('/api/admin/give-money', {method:'POST', body: {uid: uid, amount: amount}});
  const d = await res.json();
  if (!res.ok) { showToast(d.detail || 'Ошибка', 'error'); return; }
  showToast(d.message, 'success');
  loadAdminUsers();
  loadMe();
}

function getDeviceType() {
  const ua = navigator.userAgent;
  if (/iPad|Tablet|PlayBook|Silk/i.test(ua)) return 'tablet';
  if (/Mobile|Android|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)) return 'mobile';
  return 'desktop';
}
function getBrowser() {
  const ua = navigator.userAgent;
  if (ua.indexOf('Firefox') > -1) return 'Firefox';
  if (ua.indexOf('Edg') > -1) return 'Edge';
  if (ua.indexOf('OPR') > -1 || ua.indexOf('Opera') > -1) return 'Opera';
  if (ua.indexOf('Chrome') > -1) return 'Chrome';
  if (ua.indexOf('Safari') > -1) return 'Safari';
  return 'Other';
}
function getOS() {
  const ua = navigator.userAgent;
  if (ua.indexOf('Windows') > -1) return 'Windows';
  if (ua.indexOf('Android') > -1) return 'Android';
  if (/iPhone|iPad|iPod/.test(ua)) return 'iOS';
  if (ua.indexOf('Mac') > -1) return 'macOS';
  if (ua.indexOf('Linux') > -1) return 'Linux';
  return 'Other';
}

async function getDeviceFingerprint() {
  const parts = [
    navigator.userAgent, navigator.language,
    screen.width + 'x' + screen.height,
    screen.colorDepth,
    new Date().getTimezoneOffset(),
    navigator.hardwareConcurrency || 0,
    navigator.platform || ''
  ];
  try {
    const c = document.createElement('canvas');
    const ctx = c.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125,1,62,20);
    ctx.fillStyle = '#069';
    ctx.fillText('PBK-Wallet', 2, 15);
    parts.push(c.toDataURL());
  } catch(e) {}
  const str = parts.join('|');
  const buf = new TextEncoder().encode(str);
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2,'0')).join('');
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

document.addEventListener('DOMContentLoaded', () => {
  applyTheme(localStorage.getItem("pbk-theme") || "light");
  const glass = localStorage.getItem("pbk-glass") === "1";
  document.body.classList.toggle("glass", glass);
  updateThemeIcons();
  if (getToken()) showApp();
  else showAuth();
});
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  if (localStorage.getItem("pbk-theme") === "system") {
    document.documentElement.setAttribute("data-theme", resolveTheme("system"));
  }
});
</script>
</body>
</html>
"""