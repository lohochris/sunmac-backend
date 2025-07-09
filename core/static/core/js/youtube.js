function fetchYouTubeVideos(query) {
  const apiKey = "YOUR_YOUTUBE_API_KEY"; // 
  const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(query)}&type=video&maxResults=3&key=${apiKey}`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById("youtube-results");
      container.innerHTML = ""; 

      data.items.forEach(item => {
        const videoId = item.id.videoId;
        const title = item.snippet.title;

        const videoElement = `
          <div class="youtube-video">
            <iframe width="360" height="200" src="https://www.youtube.com/embed/${videoId}" 
              frameborder="0" allowfullscreen></iframe>
            <p>${title}</p>
          </div>
        `;
        container.innerHTML += videoElement;
      });
    })
    .catch(error => {
      console.error("Error fetching YouTube videos:", error);
    });
}
