const stations = [
    { code:"WORSHIP", name:"Worship", stream:"https://ais-sa3.cdnstream1.com/2878_64.aac" },
    // … your other 11 stations here …
  ];
  
  // Build station carousel
  const stationList = document.getElementById("station-list");
  stations.forEach(s=>{
    const img = document.createElement("img");
    img.src = s.imageUrl || "/station-placeholder.jpg";
    img.title = s.name;
    img.onclick = ()=>selectStation(s);
    stationList.append(img);
  });
  
  // DOM refs
  const audio   = document.getElementById("audio");
  const playBtn = document.getElementById("play-pause");
  const volume  = document.getElementById("volume");
  const titleEl = document.getElementById("track-title");
  const artEl   = document.getElementById("hero-art");
  const artistEl= document.getElementById("track-artist");
  const histList= document.getElementById("history-list");
  const stName  = document.getElementById("station-name");
  
  playBtn.onclick = () => {
    if (audio.paused) { audio.play(); playBtn.textContent="❚❚"; }
    else { audio.pause(); playBtn.textContent="▶︎"; }
  };
  volume.oninput = ()=>audio.volume = volume.value;
  
  async function selectStation(s){
    stName.textContent = s.name;
    audio.src = s.stream;
    const feedUrl = `/feeds/${s.code.toLowerCase()}-feed.json`;
    try {
      const res = await fetch(feedUrl);
      const data = await res.json();
      const now = data.nowPlaying[0];
      const hist = data.nowPlaying.slice(1,11);
  
      titleEl.textContent  = now.title;
      artistEl.textContent = now.artist;
      artEl.src            = now.imageUrl;
      audio.play(); playBtn.textContent="❚❚";
  
      histList.innerHTML = "";
      hist.forEach(track=>{
        const div = document.createElement("div");
        div.className="history-item";
        div.innerHTML = `
          <img src="${track.imageUrl}" />
          <p>${track.title}</p>
          <p style="font-size:.6rem;color:#888">${track.artist}</p>`;
        histList.append(div);
      });
    } catch(e){ console.error(e) }
  }
  
  // Initialize
  selectStation(stations[0]);
  