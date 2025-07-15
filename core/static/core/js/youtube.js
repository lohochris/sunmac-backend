function fetchYouTubeVideos(query) {
  const apiKey = "AIzaSyDmXtyOMkvPc-yQHasR0vbUxWyvExdwCEk";
  const maxResults = 5;

  if (!query || query.trim().length === 0) return;

  fetch(`https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(query)}&type=video&key=${apiKey}&maxResults=${maxResults}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      const container = document.getElementById('youtube-results');
      container.innerHTML = ''; // Clear old results

      if (!data.items || data.items.length === 0) {
        container.innerHTML = '<p>No related YouTube videos found.</p>';
        return;
      }

      data.items.forEach(video => {
        const videoId = video.id.videoId;
        const title = video.snippet.title;
        const thumbnail = video.snippet.thumbnails.medium.url;

        const videoElement = document.createElement('div');
        videoElement.classList.add('youtube-video');
        videoElement.innerHTML = `
          <a href="https://www.youtube.com/watch?v=${videoId}" target="_blank" style="text-decoration: none; color: inherit;">
            <img src="${thumbnail}" alt="${title}" style="width: 100%; border-radius: 8px;" />
            <p style="margin-top: 8px; font-weight: bold; font-size: 0.95rem;">${title}</p>
          </a>
        `;

        container.appendChild(videoElement);
      });
    })
    .catch(error => {
      console.error('YouTube API error:', error);
      const container = document.getElementById('youtube-results');
      container.innerHTML = '<p style="color: red;">⚠️ Error fetching YouTube videos. Please try again later.</p>';
    });
}
