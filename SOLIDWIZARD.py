import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="實威國際入口網",
    layout="wide"
)

# 隱藏 Streamlit UI（讓畫面更像內部系統）
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ✅ 所有 HTML / CSS / JS 都包在字串（關鍵：不會再報錯）
html_code = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
*{box-sizing:border-box;margin:0;padding:0}

:root{
  --bg:#F4F5F8;
  --card:#fff;
  --text:#111;
  --border:#ddd;
  --accent:#2563EB;
  --radius:14px;
}

body{
  font-family:Arial;
  background:var(--bg);
  color:var(--text);
}

.container{
  max-width:1200px;
  margin:auto;
  padding:30px;
}

h1{
  margin-bottom:20px;
}

.grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
  gap:16px;
}

.card{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:var(--radius);
  overflow:hidden;
  cursor:pointer;
  transition:0.2s;
}

.card:hover{
  transform:translateY(-4px);
}

.card img{
  width:100%;
  aspect-ratio:16/9;
  object-fit:cover;
}

.card-body{
  padding:10px;
}

.btn{
  margin:10px 0;
  padding:8px 12px;
  background:var(--accent);
  color:white;
  border:none;
  border-radius:8px;
  cursor:pointer;
}

/* modal */
.modal{
  position:fixed;
  inset:0;
  background:rgba(0,0,0,0.5);
  display:none;
  align-items:center;
  justify-content:center;
}

.modal.open{display:flex}

.modal-box{
  background:white;
  padding:20px;
  border-radius:12px;
  width:300px;
}

input{
  width:100%;
  margin-bottom:10px;
  padding:8px;
}
</style>
</head>

<body>

<div class="container">
  <h1>實威國際入口網站</h1>
  <button class="btn" onclick="openModal()">+ 新增</button>

  <div class="grid" id="grid"></div>
</div>

<!-- modal -->
<div class="modal" id="modal">
  <div class="modal-box">
    <h3>新增 / 編輯</h3>
    <input id="name" placeholder="名稱">
    <input id="url" placeholder="網址">
    <input type="file" onchange="uploadImg(event)">
    <button class="btn" onclick="save()">儲存</button>
    <button onclick="closeModal()">取消</button>
  </div>
</div>

<script>
let data = JSON.parse(localStorage.getItem("portal") || "[]");
let editIndex = null;
let imgBase64 = "";

function render(){
  const grid = document.getElementById("grid");
  grid.innerHTML = "";

  data.forEach((item,i)=>{
    const div = document.createElement("div");
    div.className = "card";

    div.innerHTML = `
      <img src="${item.img || ''}">
      <div class="card-body">
        <b>${item.name}</b><br>
        <small>${item.url}</small><br>
        <button onclick="event.stopPropagation();edit(${i})">編輯</button>
        <button onclick="event.stopPropagation();del(${i})">刪除</button>
      </div>
    `;

    div.onclick = ()=>window.open(item.url);
    grid.appendChild(div);
  });
}

function openModal(){
  document.getElementById("modal").classList.add("open");
  editIndex=null;
  document.getElementById("name").value="";
  document.getElementById("url").value="";
}

function closeModal(){
  document.getElementById("modal").classList.remove("open");
}

function save(){
  const name = document.getElementById("name").value;
  const url = document.getElementById("url").value;

  if(!name || !url){
    alert("請填寫完整");
    return;
  }

  const obj = {name,url,img:imgBase64};

  if(editIndex===null){
    data.push(obj);
  }else{
    data[editIndex]=obj;
  }

  localStorage.setItem("portal",JSON.stringify(data));
  closeModal();
  render();
}

function edit(i){
  const d = data[i];
  document.getElementById("name").value=d.name;
  document.getElementById("url").value=d.url;
  imgBase64=d.img;
  editIndex=i;
  openModal();
}

function del(i){
  if(confirm("確定刪除?")){
    data.splice(i,1);
    localStorage.setItem("portal",JSON.stringify(data));
    render();
  }
}

function uploadImg(e){
  const file = e.target.files[0];
  const reader = new FileReader();
  reader.onload = ()=>{
    imgBase64 = reader.result;
  };
  reader.readAsDataURL(file);
}

render();
</script>

</body>
</html>
"""

# 顯示（關鍵：components 才能跑 JS）
components.html(html_code, height=900, scrolling=True)
