<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>實威國際入口網</title>

<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#F4F5F8;
  --surface:#ffffff;
  --text:#111111;
  --accent:#2563EB;
  --border:#E2E4EC;
  --radius:16px;
}

body{
  font-family:Arial;
  background:var(--bg);
  color:var(--text);
}

.page-wrap{
  max-width:1200px;
  margin:auto;
  padding:20px;
}

.header{
  display:flex;
  justify-content:space-between;
  margin-bottom:20px;
}

.btn{
  padding:6px 12px;
  border:1px solid var(--border);
  background:#fff;
  cursor:pointer;
  border-radius:8px;
}

.hero{
  text-align:center;
  margin-bottom:30px;
}

.cards-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
  gap:16px;
}

.card{
  background:#fff;
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:10px;
  text-decoration:none;
  color:inherit;
}

.card:hover{
  transform:translateY(-3px);
}

.card-title{
  font-weight:bold;
}
</style>
</head>

<body>

<div class="page-wrap">

  <div class="header">
    <h2>實威國際 Portal</h2>
    <button class="btn">管理登入</button>
  </div>

  <div class="hero">
    <h1>入口網站</h1>
    <p>系統快速入口</p>
  </div>

  <div class="cards-grid">
    <a class="card" href="https://www.swtc.com" target="_blank">
      <div class="card-title">實威官網</div>
    </a>

    <a class="card" href="https://formlabs.com" target="_blank">
      <div class="card-title">Formlabs</div>
    </a>

    <a class="card" href="https://my.solidworks.com" target="_blank">
      <div class="card-title">SOLIDWORKS</div>
    </a>
  </div>

</div>

</body>
</html>
