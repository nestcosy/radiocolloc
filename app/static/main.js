document.addEventListener("DOMContentLoaded", function(){
  const playBtn = document.getElementById("playBtn");
  const audio = document.getElementById("audio");
  const now = document.getElementById("now");

  playBtn.onclick = async () => {
    const r = await fetch("/tracks/random");
    if (!r.ok) { alert("Aucun morceau"); return; }
    const j = await r.json();
    const filename = j.filepath.split("/").pop();
    audio.src = "/media/" + filename;
    now.textContent = j.title;
    audio.play();
  };

  document.querySelectorAll(".tagBtn").forEach(b=>{
    b.onclick = async ()=> {
      const tag = b.dataset.tag;
      const r = await fetch("/tracks/by_tag/" + encodeURIComponent(tag));
      if (!r.ok) { alert("Aucun"); return; }
      const j = await r.json();
      const filename = j.filepath.split("/").pop();
      audio.src = "/media/" + filename;
      now.textContent = j.title;
      audio.play();
    };
  });

  const addForm = document.getElementById("addForm");
  if (addForm){
    addForm.addEventListener("submit", async (ev)=>{
      ev.preventDefault();
      const url = document.getElementById("url").value;
      const fd = new FormData();
      fd.append("url", url);
      const r = await fetch("/add", {method:"POST", body: fd});
      const out = document.getElementById("addResult");
      if (r.ok){
        const j = await r.json();
        out.textContent = "Ajouté: " + j.added.map(x=>x.title).join(", ");
      } else {
        const txt = await r.text();
        out.textContent = "Erreur: " + txt;
      }
    });
  }
});
