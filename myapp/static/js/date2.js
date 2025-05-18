document.addEventListener('DOMContentLoaded', function() {
    // Key view containers
    const cardStack = document.querySelector('.card-stack');
    const actionButtons = document.querySelector('.action-buttons');
    const profileSection = document.getElementById('profile-section');
    const matchesSection = document.getElementById('matches-section');
    const matchesList = document.querySelector('.matches-list');

    // Helper: Return a fallback image URL based on gender from static files.
    function getFallbackImageURL(gender) {
        if (gender && gender.toLowerCase() === 'male') {
            const num = Math.floor(Math.random() * 6) + 1;
            return window.location.origin + '/static/images/mprofile' + num + '.jpg';
        } else {
            const num = Math.floor(Math.random() * 8) + 1;
            return window.location.origin + '/static/images/profile' + num + '.jpg';
        }
    }

    // Helper: Return an absolute URL for images; if missing, return a fallback based on gender.
    function getImageURL(url, gender) {
        if (!url) {
            return getFallbackImageURL(gender);
        }
        if (url.startsWith('/')) {
            return window.location.origin + url;
        }
        return url;
    }

    // --- Dummy Matches Local Storage Helpers ---
    function saveDummyMatch(matchData) {
        let dummyMatches = JSON.parse(localStorage.getItem('dummyMatches') || '[]');
        // Optional: Check for duplicate based on match id.
        if (!dummyMatches.find(m => m.id === matchData.id)) {
            dummyMatches.push(matchData);
            localStorage.setItem('dummyMatches', JSON.stringify(dummyMatches));
        }
    }

    function getDummyMatches() {
        return JSON.parse(localStorage.getItem('dummyMatches') || '[]');
    }

    // Optional: Clear dummy matches (can be called on logout, for example)
    function clearDummyMatches() {
        localStorage.removeItem('dummyMatches');
    }

    // --- Bottom Navigation Handling ---
    const navItems = document.querySelectorAll('.bottom-nav .nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            const view = item.dataset.view;
            switch (view) {
                case 'cards':
                    if (cardStack) cardStack.style.display = 'flex';
                    if (actionButtons) actionButtons.style.display = 'flex';
                    if (profileSection) profileSection.style.display = 'none';
                    if (matchesSection) matchesSection.style.display = 'none';
                    loadDummyUsers();
                    break;
                case 'profile':
                    if (profileSection) profileSection.style.display = 'block';
                    if (cardStack) cardStack.style.display = 'none';
                    if (actionButtons) actionButtons.style.display = 'none';
                    if (matchesSection) matchesSection.style.display = 'none';
                    break;
                case 'discover':
                    if (cardStack) cardStack.style.display = 'none';
                    if (actionButtons) actionButtons.style.display = 'none';
                    if (profileSection) profileSection.style.display = 'none';
                    if (matchesSection) matchesSection.style.display = 'none';
                    console.log('Discover view not implemented yet');
                    break;
                case 'matches':
                    if (matchesSection) matchesSection.style.display = 'block';
                    if (cardStack) cardStack.style.display = 'none';
                    if (actionButtons) actionButtons.style.display = 'none';
                    if (profileSection) profileSection.style.display = 'none';
                    loadMatches();
                    break;
                default:
                    break;
            }
        });
    });

    // --- Swipe Functionality ---
    function setupSwipe() {
        const cards = document.querySelectorAll('.card');
        let currentIndex = 0;
        if (!cards.length) return;

        // Set stacking order
        cards.forEach((card, index) => {
            card.style.zIndex = cards.length - index;
            card.style.transform = 'none';
        });

        // Touch event handlers
        cards.forEach(card => {
            let startX, startY, moveX, moveY;
            card.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
            }, { passive: true });
            card.addEventListener('touchmove', (e) => {
                if (!startX || !startY) return;
                moveX = e.touches[0].clientX - startX;
                moveY = e.touches[0].clientY - startY;
                if (Math.abs(moveX) > Math.abs(moveY)) {
                    e.preventDefault();
                    card.style.transform = `translateX(${moveX}px) rotate(${moveX * 0.1}deg)`;
                }
            }, { passive: false });
            card.addEventListener('touchend', () => {
                if (!moveX) return;
                if (Math.abs(moveX) > 100) {
                    handleSwipeAction(card, moveX > 0 ? 'right' : 'left');
                } else {
                    card.style.transform = 'none';
                }
                startX = startY = moveX = moveY = null;
            });
        });

        // Button event handlers
        const btnPass = document.querySelector('.btn-pass');
        const btnLike = document.querySelector('.btn-like');
        if (btnPass && btnLike) {
            btnPass.addEventListener('click', () => {
                if (currentIndex < cards.length) {
                    handleSwipeAction(cards[currentIndex], 'left');
                }
            });
            btnLike.addEventListener('click', () => {
                if (currentIndex < cards.length) {
                    handleSwipeAction(cards[currentIndex], 'right');
                }
            });
        }

        function handleSwipeAction(card, direction) {
            const userId = card.dataset.userId;
            if (!userId) {
                console.error("Missing userId in card dataset", card);
                return;
            }
            const action = direction === 'right' ? 'like' : 'pass';
            const isMock = card.dataset.isMock === 'true';
            // Build payload; if dummy, include hobbies.
            let payload = {
                profile_id: parseInt(userId, 10),
                action: action,
                is_mock: isMock
            };
            if (isMock) {
                if (card.dataset.hobbies) {
                    try {
                        payload.hobbies = JSON.parse(card.dataset.hobbies);
                    } catch (e) {
                        console.error("Error parsing hobbies:", e);
                        payload.hobbies = [];
                    }
                } else {
                    payload.hobbies = [];
                }
            }
    
            console.log("Sending payload:", payload);
    
            card.style.transition = 'transform 0.5s ease';
            card.style.transform = `translateX(${direction === 'right' ? 500 : -500}px) rotate(${direction === 'right' ? 30 : -30}deg)`;
            
            fetch('/api/swipe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(payload)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Response from /api/swipe/:", data);
                if (data.status === 'match') {
                    console.log('Match detected!');
                    alert("Match success!");
                    // If dummy profile, save match locally.
                    if (isMock) {
                        let matchData = {
                            id: payload.profile_id,
                            name: card.querySelector('h2').textContent, // Contains name and age; you may parse if needed.
                            relationship_type: (card.querySelector('.card-relationship') ? 
                                                   card.querySelector('.card-relationship').textContent.replace('Looking for: ', '') : 'N/A'),
                            image: card.querySelector('.card-image').style.backgroundImage
                                    .replace(/^url\(["']?/, '').replace(/["']?\)$/, '')
                        };
                        saveDummyMatch(matchData);
                    }
                    loadMatches();
                }
            })
            .catch(error => console.error("Error in handleSwipeAction:", error));
            
            setTimeout(() => {
                card.remove();
                currentIndex++;
                if (currentIndex > cards.length - 3) {
                    loadDummyUsers();
                }
            }, 300);
        }
    }

    // Helper: Get CSRF token from cookie.
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // --- Load Dummy Users ---
    async function loadDummyUsers() {
        if (!cardStack) return;
        cardStack.innerHTML = '<div class="loading-message"><i class="fas fa-spinner fa-spin"></i> Loading profiles...</div>';
        try {
            const response = await fetch('/api/dummy-users/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const users = await response.json();
            if (users.error) {
                throw new Error(users.error);
            }
            cardStack.innerHTML = '';
            users.forEach(user => {
                const card = document.createElement('div');
                card.className = 'card';
                card.dataset.userId = user.id;
                // Mark dummy profiles and store hobbies.
                card.dataset.isMock = "true";
                card.dataset.hobbies = JSON.stringify(user.hobbies || []);
    
                card.innerHTML = `
                    <div class="card-image" style="background-image: url(${getImageURL(user.image, user.gender)})"></div>
                    <div class="card-info">
                        <h2>${user.name}, ${user.age}</h2>
                        <p class="card-location"><i class="fas fa-map-marker-alt"></i> ${user.location}</p>
                        <p class="card-height">Height: ${user.height}</p>
                        <p class="card-bio">${user.bio || 'No bio available'}</p>
                        <p class="card-relationship">Looking for: ${user.relationship_type || 'N/A'}</p>
                        <div class="hobbies-container">
                            ${user.hobbies.map(hobby => `<span class="hobby-tag">${hobby}</span>`).join('')}
                        </div>
                    </div>
                `;
                cardStack.appendChild(card);
            });
            setupSwipe();
        } catch (error) {
            console.error("Error loading dummy users:", error);
            cardStack.innerHTML = `<div class="error-message">Error loading profiles: ${error.message}</div>`;
        }
    }

    // --- Load Matches (Merges server matches and dummy matches from localStorage) ---
    async function loadMatches() {
        if (!matchesList) return;
        matchesList.innerHTML = '<div class="loading-message"><i class="fas fa-spinner fa-spin"></i> Loading matches...</div>';
        try {
            const response = await fetch('/api/matches/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const serverMatches = await response.json();
            const dummyMatches = getDummyMatches();
            // Merge the two arrays.
            const allMatches = serverMatches.concat(dummyMatches);
    
            matchesList.innerHTML = '';
            if (allMatches.length === 0) {
                matchesList.innerHTML = '<p>You have no matches yet.</p>';
            } else {
                allMatches.forEach(match => {
                    const matchCard = document.createElement('div');
                    matchCard.className = 'match-card';
                    matchCard.innerHTML = `
                        <div class="match-image" style="background-image: url(${getImageURL(match.image, match.gender)})"></div>
                        <div class="match-info">
                            <h3>${match.name}</h3>
                            <p>Looking for: ${match.relationship_type || 'N/A'}</p>
                        </div>
                    `;
                    matchesList.appendChild(matchCard);
                });
            }
        } catch (error) {
            console.error("Error loading matches:", error);
            matchesList.innerHTML = `<div class="error-message">Error loading matches: ${error.message}</div>`;
        }
    }
    
    // Trigger default view: show swipe cards ("cards" view)
    const defaultNav = document.querySelector('.bottom-nav .nav-item[data-view="cards"]');
    if (defaultNav) defaultNav.click();
});
