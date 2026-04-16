import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="實威國際入口網", layout="wide")

# 隱藏 Streamlit UI
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
*{box-sizing:border-box;margin:0;padding:0}

:root{
  --bg:#0F1117;
  --card:#1A1D27;
  --text:#EEE;
  --border:#2A2D3E;
  --accent:#3B82F6;
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

.section{
  margin-bottom:30px;
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
  margin:5px 5px 5px 0;
  padding:6px 10px;
  background:var(--accent);
  color:white;
  border:none;
  border-radius:6px;
  cursor:pointer;
  font-size:12px;
}

/* modal */
.modal{
  position:fixed;
  inset:0;
  background:rgba(0,0,0,0.6);
  display:none;
  align-items:center;
  justify-content:center;
}

.modal.open{display:flex}

.modal-box{
  background:#fff;
  color:#000;
  padding:20px;
  border-radius:12px;
  width:320px;
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

  <button class="btn" onclick="addCategory()">+ 新增分類</button>

  <div id="sections"></div>
</div>

<!-- modal -->
<div class="modal" id="modal">
  <div class="modal-box">
    <h3 id="modal-title">新增</h3>
    <input id="name" placeholder="名稱">
    <input id="url" placeholder="網址">
    <input type="file" onchange="uploadImg(event)">
    <button class="btn" onclick="save()">儲存</button>
    <button onclick="closeModal()">取消</button>
  </div>
</div>

<script>
let data = JSON.parse(localStorage.getItem("portal_v2") || "[]");
let currentCat = null;
let editIndex = null;
let imgBase64 = "";

function saveData(){
  localStorage.setItem("portal_v2", JSON.stringify(data));
}

function render(){
  const sections = document.getElementById("sections");
  sections.innerHTML = "";

  data.forEach((cat,ci)=>{
    const sec = document.createElement("div");
    sec.className="section";

    sec.innerHTML = `
      <h2>${cat.name}</h2>
      <button class="btn" onclick="addCard(${ci})">+ 新增連結</button>
      <button class="btn" onclick="deleteCategory(${ci})">刪除分類</button>
      <div class="grid" id="grid-${ci}"></div>
    `;

    sections.appendChild(sec);

    const grid = sec.querySelector(".grid");

    cat.cards.forEach((c,i)=>{
      const card = document.createElement("div");
      card.className="card";

      card.innerHTML = `
        <img src="${c.img || ''}">
        <div class="card-body">
          <b>${c.name}</b><br>
          <small>${c.url}</small><br>
          <button onclick="event.stopPropagation();edit(${ci},${i})">編輯</button>
          <button onclick="event.stopPropagation();del(${ci},${i})">刪除</button>
        </div>
      `;

      card.onclick = ()=>window.open(c.url);
      grid.appendChild(card);
    });
  });
}

function addCategory(){
  const name = prompt("分類名稱");
  if(!name) return;
  data.push({name:name,cards:[]});
  saveData();
  render();
}

function deleteCategory(ci){
  if(confirm("刪除分類?")){
    data.splice(ci,1);
    saveData();
    render();
  }
}

function addCard(ci){
  currentCat = ci;
  editIndex = null;
  imgBase64 = "";
  openModal("新增連結");
}

function edit(ci,i){
  currentCat = ci;
  editIndex = i;
  const d = data[ci].cards[i];
  document.getElementById("name").value=d.name;
  document.getElementById("url").value=d.url;
  imgBase64=d.img;
  openModal("編輯連結");
}

function del(ci,i){
  if(confirm("刪除?")){
    data[ci].cards.splice(i,1);
    saveData();
    render();
  }
}

function openModal(title){
  document.getElementById("modal-title").innerText=title;
  document.getElementById("modal").classList.add("open");
}

function closeModal(){
  document.getElementById("modal").classList.remove("open");
  document.getElementById("name").value="";
  document.getElementById("url").value="";
}

function save(){
  const name = document.getElementById("name").value;
  const url = document.getElementById("url").value;

  if(!name||!url){alert("請填寫完整");return;}

  const obj={name,url,img:imgBase64};

  if(editIndex===null){
    data[currentCat].cards.push(obj);
  }else{
    data[currentCat].cards[editIndex]=obj;
  }

  saveData();
  closeModal();
  render();
}

function uploadImg(e){
  const file = e.target.files[0];
  const reader = new FileReader();
  reader.onload = ()=>{imgBase64 = reader.result};
  reader.readAsDataURL(file);
}

render();
</script>

</body>
</html>
"""

components.html(html_code, height=1000, scrolling=True)
