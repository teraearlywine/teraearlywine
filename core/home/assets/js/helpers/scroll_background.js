
// Calculate how far down the user is (0 to 1)
const scrollFraction = window.scrollY / (document.body.scrollHeight - window.innerHeight);

// Convert that fraction into a percent for the background position
const posX = scrollFraction * 100;   // 0% -> 100% horizontally
const posYStart = 20;               // Starting Y position
const posYEnd = 80;                 // Ending Y position
const posY = posYStart + scrollFraction * (posYEnd - posYStart);


export function initScrollBackground() {

    /*
    As the user scrolls down the page, move the background. 
    The first function updates the background style (found in animations)
    
    */
    function updateBackground() {
        // Move the gradient horizontally & vertically as the user scrolls
        document.body.style.backgroundPosition = `${posX}% ${posY}%`;
    }

    // Add background changes here:
    window.addEventListener("scroll", updateBackground, { passive: true });

    // Also fire once on load in case the user is initially scrolled
    updateBackground();
}