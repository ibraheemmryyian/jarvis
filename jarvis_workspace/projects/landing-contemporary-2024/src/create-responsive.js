// Mobile menu toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenu = document.getElementById('mobile-menu');
    const navLinks = document.getElementById('nav-links');
    
    // Toggle mobile menu
    mobileMenu.addEventListener('click', function() {
        mobileMenu.classList.toggle('active');
        navLinks.classList.toggle('active');
        
        // Update aria-expanded attribute for accessibility
        const isExpanded = navLinks.classList.contains('active');
        mobileMenu.setAttribute('aria-expanded', isExpanded);
    });
    
    // Close menu when clicking on a link (for mobile)
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
            navLinks.classList.remove('active');
            mobileMenu.setAttribute('aria-expanded', 'false');
        });
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideNav = navLinks.contains(event.target) || mobileMenu.contains(event.target);
        
        if (!isClickInsideNav && navLinks.classList.contains('active')) {
            mobileMenu.classList.remove('active');
            navLinks.classList.remove('active');
            mobileMenu.setAttribute('aria-expanded', 'false');
        }
    });
    
    // Keyboard accessibility
    document.addEventListener('keydown', function(event) {
        // Close menu with Escape key
        if (event.key === 'Escape') {
            mobileMenu.classList.remove('active');
            navLinks.classList.remove('active');
            mobileMenu.setAttribute('aria-expanded', 'false');
        }
        
        // Focus management for keyboard users
        if (event.key === 'Tab') {
            const focusableElements = navLinks.querySelectorAll('a, button');
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            if (event.shiftKey && document.activeElement === firstElement) {
                lastElement.focus();
                event.preventDefault();
            } else if (!event.shiftKey && document.activeElement === lastElement) {
                firstElement.focus();
                event.preventDefault();
            }
        }
    });
    
    // Add ARIA attributes for accessibility
    mobileMenu.setAttribute('aria-label', 'Toggle navigation menu');
    mobileMenu.setAttribute('aria-expanded', 'false');
    navLinks.setAttribute('aria-label', 'Main navigation');
});