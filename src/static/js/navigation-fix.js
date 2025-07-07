/**
 * Navigation Fix for Sidebar
 * Ensures all navigation links are clickable
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Navigation fix loaded');
    
    // Remove any blocking overlays
    const overlays = document.querySelectorAll('.overlay, .modal-backdrop');
    overlays.forEach(overlay => {
        if (!overlay.classList.contains('show')) {
            overlay.style.display = 'none';
        }
    });
    
    // Ensure all nav links are clickable
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        // Remove any pointer-events: none
        link.style.pointerEvents = 'auto';
        
        // Add click handler for non-submenu links
        if (!link.parentElement.classList.contains('has-submenu')) {
            link.addEventListener('click', function(e) {
                // Don't prevent default for normal navigation
                console.log('Navigation clicked:', this.href);
            });
        }
    });
    
    // Fix z-index issues
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.style.zIndex = '100';
    }
    
    // Ensure submenu links are also clickable
    const subLinks = document.querySelectorAll('.nav-sublink');
    subLinks.forEach(link => {
        link.style.pointerEvents = 'auto';
        link.addEventListener('click', function(e) {
            console.log('Submenu navigation clicked:', this.href);
        });
    });
    
    // Debug: Log all navigation links
    console.log('Found navigation links:', navLinks.length);
    console.log('Found submenu links:', subLinks.length);
});

// Also handle dynamic content
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                // Re-apply fixes for dynamically added content
                const newLinks = document.querySelectorAll('.nav-link, .nav-sublink');
                newLinks.forEach(link => {
                    link.style.pointerEvents = 'auto';
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}