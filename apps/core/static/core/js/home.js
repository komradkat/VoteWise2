// static/js/home.js
// static/js/home.js
document.addEventListener('DOMContentLoaded', () => {
  // --- Mobile Menu Toggle ---
  const mobileMenuToggle = document.getElementById('mobileMenuToggle');
  const mainNav = document.querySelector('.main-nav');

  if (mobileMenuToggle && mainNav) {
    mobileMenuToggle.addEventListener('click', () => {
      mainNav.classList.toggle('active');
    });
  }

  // --- Election Results Logic ---
  const API_URL = '/api/election/current/';
  const banner = document.getElementById('urgencyBanner');
  const countdownEl = document.getElementById('countdown');
  
  // Elements that might only exist on results page
  const totalVotesEl = document.getElementById('totalVotes');
  const statusEl = document.getElementById('electionStatus');
  const candidatesGrid = document.getElementById('candidatesGrid');
  const loading = document.getElementById('loadingContainer');
  const errorContainer = document.getElementById('errorContainer');
  const noData = document.getElementById('noDataContainer');
  const resultsNote = document.getElementById('resultsNote');

  let electionEndTime = null;

  const updateCountdown = () => {
    if (!electionEndTime || !countdownEl) return;
    const now = new Date().getTime();
    const distance = electionEndTime - now;

    if (distance <= 0) {
      countdownEl.textContent = "00:00:00";
      if (banner) {
          banner.classList.add('closed');
          const bannerText = banner.querySelector('#bannerText');
          if (bannerText) bannerText.textContent = "Voting has ended";
      }
      return;
    }

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    countdownEl.textContent = `${hours.toString().padStart(2, '0')}:${minutes
      .toString()
      .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const fetchResults = async () => {
    // Only proceed if we have a container to show results in
    if (!candidatesGrid) return;

    try {
      const res = await fetch(API_URL);
      const data = await res.json();

      if (!data.active) {
        if (loading) loading.style.display = 'none';
        if (noData) noData.style.display = 'block';
        if (banner) banner.style.display = 'none';
        return;
      }

      // Show everything
      if (loading) loading.style.display = 'none';
      if (candidatesGrid) candidatesGrid.style.display = 'grid';
      if (resultsNote) resultsNote.style.display = 'block';
      if (banner) banner.style.display = 'block';

      // Update banner & countdown
      electionEndTime = new Date(data.end_date).getTime();
      updateCountdown();
      // Clear existing interval if any (though this function is called once/interval)
      // Actually, updateCountdown is light, we can just call it.
      // But we need a separate interval for the countdown tick.
    } catch (err) {
      if (loading) loading.style.display = 'none';
      if (errorContainer) {
          errorContainer.style.display = 'block';
          errorContainer.innerHTML = `<p>Unable to load results. Please try again later.</p>`;
      }
      return; // Stop processing on error
    }

    // We need to fetch data again to get 'data' variable for rendering
    // Or better, refactor to not lose scope. 
    // Re-fetching inside try block is better.
    // Let's just continue inside the try block above.
  };
  
  // Refactored fetchResults to be cleaner and actually render
  const fetchAndRender = async () => {
      if (!candidatesGrid) return; // specific to results page

      try {
          const res = await fetch(API_URL);
          const data = await res.json();

          if (!data.active) {
              if (loading) loading.style.display = 'none';
              if (noData) noData.style.display = 'block';
              if (banner) banner.style.display = 'none';
              return;
          }

          if (loading) loading.style.display = 'none';
          if (candidatesGrid) candidatesGrid.style.display = 'grid';
          if (resultsNote) resultsNote.style.display = 'block';
          if (banner) banner.style.display = 'block';

          electionEndTime = new Date(data.end_date).getTime();
          updateCountdown();

          if (totalVotesEl) totalVotesEl.textContent = data.total_votes.toLocaleString();
          if (statusEl) {
              statusEl.textContent = data.is_closed ? "CLOSED" : "ONGOING";
              statusEl.className = data.is_closed ? "status closed" : "status";
          }

          if (candidatesGrid) {
              candidatesGrid.innerHTML = data.candidates
                .sort((a, b) => b.votes - a.votes)
                .map((c, i) => `
                  <div class="candidate-card ${i === 0 && data.is_closed ? 'winner' : ''}">
                    <div class="candidate-header">
                      <img src="${c.photo || '/static/img/default-avatar.png'}" alt="${c.name}">
                      <h3>${c.name}</h3>
                      <div class="position">${c.position}</div>
                    </div>
                    <div class="candidate-body">
                      <div class="progress-container">
                        <div class="progress-bar">
                          <div class="progress-fill" style="width: ${c.percentage}%"></div>
                        </div>
                        <div class="progress-text">
                          <span>${c.votes.toLocaleString()} votes</span>
                          <span>${c.percentage.toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                `).join('');
          }

      } catch (err) {
          console.error(err);
          if (loading) loading.style.display = 'none';
          if (errorContainer) {
              errorContainer.style.display = 'block';
              errorContainer.innerHTML = `<p>Unable to load results.</p>`;
          }
      }
  };

  // Start Countdown Interval
  setInterval(updateCountdown, 1000);

  // Start Polling
  fetchAndRender();
  setInterval(fetchAndRender, 10000);
});