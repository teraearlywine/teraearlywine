// Get elements by ID
const experienceElement = document.getElementById('experience');
const popup = document.getElementById('popup');
const popupOverlay = document.getElementById('popupOverlay');
const closeBtn = document.getElementById('closeBtn');

// Open popup function
function openPopup() {
    popup.classList.add('active');
    popupOverlay.classList.add('active');
}

// Close popup function
function closePopup() {
    popup.classList.remove('active');
    popupOverlay.classList.remove('active');
}

// Event listeners for opening and closing the popup
experienceElement.addEventListener('click', openPopup);
closeBtn.addEventListener('click', closePopup);
popupOverlay.addEventListener('click', closePopup);