document.addEventListener('DOMContentLoaded', function() {
    // Define key view containers from your updated date.html
    const cardStack = document.querySelector('.card-stack');
    const actionButtons = document.querySelector('.action-buttons');
    const profileSection = document.getElementById('profile-section');
    const matchesSection = document.getElementById('matches-section');
    const matchesList = document.querySelector('.matches-list');
    
    // Set up bottom navigation handling
    const navItems = document.querySelectorAll('.bottom-nav .nav-item');
    navItems.forEach(item => {
         item.addEventListener('click', function(e) {
              e.preventDefault();
              // Remove active class from all nav items
              navItems.forEach(nav => nav.classList.remove('active'));
              // Add active class to the clicked item
              item.classList.add('active');
              const view = item.dataset.view;
              switch(view) {
                  case 'cards':
                      if(cardStack) cardStack.style.display = 'flex';
                      if(actionButtons) actionButtons.style.display = 'flex';
                      if(profileSection) profileSection.style.display = 'none';
                      if(matchesSection) matchesSection.style.display = 'none';
                      loadDummyUsers();  // Now fetching real dummy users from DB
                      break;
                  case 'profile':
                      if(profileSection) profileSection.style.display = 'block';
                      if(cardStack) cardStack.style.display = 'none';
                      if(actionButtons) actionButtons.style.display = 'none';
                      if(matchesSection) matchesSection.style.display = 'none';
                      break;
                  case 'discover':
                      if(cardStack) cardStack.style.display = 'none';
                      if(actionButtons) actionButtons.style.display = 'none';
                      if(profileSection) profileSection.style.display = 'none';
                      if(matchesSection) matchesSection.style.display = 'none';
                      console.log('Discover view not implemented yet');
                      break;
                  case 'matches':
                      if(matchesSection) matchesSection.style.display = 'block';
                      if(cardStack) cardStack.style.display = 'none';
                      if(actionButtons) actionButtons.style.display = 'none';
                      if(profileSection) profileSection.style.display = 'none';
                      loadMatches();
                      break;
                  default:
                      break;
              }
         });
    });

    // ----- Swipe Functionality -----
    function setupSwipe() {
        const cards = document.querySelectorAll('.card');
        let currentIndex = 0;
        if (!cards.length) return;

        // Set up stacking order for cards
        cards.forEach((card, index) => {
            card.style.zIndex = cards.length - index;
            card.style.transform = 'none';
        });

        // Attach touch event handlers for each card
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

        // Button event handlers for swipe actions
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
            const action = direction === 'right' ? 'like' : 'pass';
            // Build the payload as a normal user (no is_mock special-case needed now)
            let payload = {
                profile_id: userId,
                action: action
            };
            
            card.style.transition = 'transform 0.5s ease';
            card.style.transform = `translateX(${direction === 'right' ? 500 : -500}px) rotate(${direction === 'right' ? 30 : -30}deg)`;
            
            // Send swipe action to server using the handle_swipe endpoint
            fetch('/api/swipe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'match') {
                    console.log('Match detected!');
                    alert("Match success!");
                    loadMatches();
                }
            })
            .catch(error => console.error('Error:', error));
            
            setTimeout(() => {
                card.remove();
                currentIndex++;
                if (currentIndex > cards.length - 3) {
                    loadDummyUsers();
                }
            }, 300);
        }
    }

    // Helper: Get CSRF token from cookie
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

    // Load dummy profiles via the fetch_dummy_users view
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
                // Since these are now real users, no need for an isMock flag
                // Build the card HTML to include relationship type
                card.innerHTML = `
                    <div class="card-image" style="background-image: url(${user.image || 'https://via.placeholder.com/300x400'})"></div>
                    <div class="card-info">
                        <h2>${user.name}, ${user.age}</h2>
                        <p class="card-location"><i class="fas fa-map-marker-alt"></i> ${user.location}</p>
                        <p class="card-height">Height: ${user.height}</p>
                        <p class="card-bio">${user.bio || 'No bio available'}</p>
                        <p class="card-relationship">Looking for: ${user.relationship_type}</p>
                        <div class="hobbies-container">
                            ${user.hobbies.map(hobby => `<span class="hobby-tag">${hobby}</span>`).join('')}
                        </div>
                    </div>
                `;
                cardStack.appendChild(card);
            });
            setupSwipe();
        } catch (error) {
            console.error('Error loading profiles:', error);
            cardStack.innerHTML = `<div class="error-message">Error loading profiles: ${error.message}</div>`;
        }
    }

    // Function to load matches (messaging view)
    async function loadMatches() {
        if (!matchesList) return;
        matchesList.innerHTML = '<div class="loading-message"><i class="fas fa-spinner fa-spin"></i> Loading matches...</div>';
        try {
            const response = await fetch('/api/matches/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const matches = await response.json();
            matchesList.innerHTML = '';
            if (matches.length === 0) {
                matchesList.innerHTML = '<p>You have no matches yet.</p>';
            } else {
                matches.forEach(match => {
                    const matchCard = document.createElement('div');
                    matchCard.className = 'match-card';
                    matchCard.innerHTML = `
                        <div class="match-image" style="background-image: url(${match.image || 'https://via.placeholder.com/150'})"></div>
                        <div class="match-info">
                            <h3>${match.name}</h3>
                            <p>Looking for: ${match.relationship_type}</p>
                        </div>
                    `;
                    matchesList.appendChild(matchCard);
                });
            }
        } catch (error) {
            console.error('Error loading matches:', error);
            matchesList.innerHTML = `<div class="error-message">Error loading matches: ${error.message}</div>`;
        }
    }

    // Trigger default view: show swipe cards ("cards" view)
    const defaultNav = document.querySelector('.bottom-nav .nav-item[data-view="cards"]');
    if (defaultNav) defaultNav.click();
});
