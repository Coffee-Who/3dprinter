import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="實威國際入口網")

html_code = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- ⭐ Firebase -->
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore-compat.js"></script>

<style>
body{font-family:sans-serif;background:#111;color:#fff;margin:0;padding:20px}
.card{background:#222;padding:10px;margin:10px;border-radius:10px}
</style>
</head>

<body>
<h2>SWTC Portal（Firebase 同步版）</h2>
<div id="app"></div>

<script>
// ================= CONFIG =================
const firebaseConfig = {
  apiKey: "AIzaSyBhgfPGUgGsWr4VmOUeaEe_cC0RNSx8I7U",
  authDomain: "swtc-portal-6930c.firebaseapp.com",
  projectId: "swtc-portal-6930c",
  storageBucket: "swtc-portal-6930c.firebasestorage.app",
  messagingSenderId: "447508396321",
  appId: "1:447508396321:web:ee8d1faaa0331590e5e660"
};

firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// ================= DEFAULT =================
const DEFAULT = {
  categories: [
    {
      name: "內部系統",
      cards: [
        {title:"CRM", url:"http://example.com"}
      ]
    }
  ]
};

let appData = null;

// ================= LOAD =================
async function loadData(){
  const doc = await db.collection("portal").doc("data").get();

  if(doc.exists){
    return doc.data();
  }else{
    await db.collection("portal").doc("data").set(DEFAULT);
    return DEFAULT;
  }
}

// ================= SAVE =================
async function saveData(){
  await db.collection("portal").doc("data").set(appData);
}

// ================= REALTIME =================
function listenRealtime(){
  db.collection("portal").doc("data")
    .onSnapshot(doc=>{
      if(doc.exists){
        appData = doc.data();
        render();
      }
    });
}

// ================= RENDER =================
function render(){
  const app = document.getElementById("app");
  app.innerHTML = "";

  appData.categories.forEach((cat,ci)=>{
    const div = document.createElement("div");
    div.innerHTML = "<h3>"+cat.name+"</h3>";

    cat.cards.forEach((c,ki)=>{
      const card = document.createElement("div");
      card.className="card";
      card.innerHTML = "<b>"+c.title+"</b><br>"+c.url;
      div.appendChild(card);
    });

    // 新增按鈕
    const btn = document.createElement("button");
    btn.innerText = "新增";
    btn.onclick = async ()=>{
      const name = prompt("名稱");
      const url = prompt("網址");

      if(!name || !url) return;

      appData.categories[ci].cards.push({title:name,url:url});
      await saveData();
    };

    div.appendChild(btn);
    app.appendChild(div);
  });
}

// ================= INIT =================
(async ()=>{
  appData = await loadData();
  render();
  listenRealtime();
})();
</script>

</body>
</html>
"""

components.html(html_code, height=1200, scrolling=True)
