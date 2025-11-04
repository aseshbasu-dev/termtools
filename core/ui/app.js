// TermTools Professional Dark Theme JavaScript
// Built by Asesh Basu
// Minimal, professional interactions without animations

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark theme features
    initializeTheme();
    
    // Setup console auto-scroll
    setupConsoleAutoScroll();
    
    // Setup button interactions
    setupButtonInteractions();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
});

function initializeTheme() {
    // Detect system theme preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // TermTools uses dark theme by default, but respect system preferences
    if (!prefersDark) {
        console.log('System prefers light theme, but TermTools uses professional dark theme');
    }
    
    // Set theme metadata
    document.documentElement.setAttribute('data-theme', 'dark');
}

function setupConsoleAutoScroll() {
    const consoleElements = document.querySelectorAll('.console');
    
    consoleElements.forEach(console => {
        // Auto-scroll to bottom when new content is added
        const observer = new MutationObserver(() => {
            console.scrollTop = console.scrollHeight;
        });
        
        observer.observe(console, {
            childList: true,
            subtree: true
        });
    });
}

function setupButtonInteractions() {
    // Add professional button feedback without animations
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        // Add click feedback
        button.addEventListener('click', function(e) {
            // Subtle visual feedback
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 100);
        });
        
        // Add ripple effect for better UX (minimal)
        button.addEventListener('mousedown', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Create subtle ripple without overdoing it
            const ripple = document.createElement('span');
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255,255,255,0.1);
                width: 10px;
                height: 10px;
                left: ${x-5}px;
                top: ${y-5}px;
                pointer-events: none;
                transform: scale(0);
                transition: transform 0.3s ease;
            `;
            
            this.style.position = 'relative';
            this.appendChild(ripple);
            
            // Trigger ripple
            setTimeout(() => ripple.style.transform = 'scale(4)', 0);
            
            // Remove ripple
            setTimeout(() => ripple.remove(), 300);
        });
    });
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Professional keyboard shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'l':
                    // Clear console
                    e.preventDefault();
                    clearConsole();
                    break;
                case 'h':
                    // Show help
                    e.preventDefault();
                    showHelp();
                    break;
                case 'q':
                    // Quick quit
                    e.preventDefault();
                    if (confirm('Exit TermTools?')) {
                        window.close();
                    }
                    break;
            }
        }
        
        // Escape key
        if (e.key === 'Escape') {
            // Cancel current operation or close modal
            cancelCurrentOperation();
        }
    });
}

function clearConsole() {
    const consoles = document.querySelectorAll('.console');
    consoles.forEach(console => {
        console.textContent = 'Console cleared.\n';
    });
}

function showHelp() {
    // Professional help display
    const helpContent = `
TermTools Keyboard Shortcuts:
• Ctrl+L: Clear console
• Ctrl+H: Show this help
• Ctrl+Q: Exit application
• Esc: Cancel operation

Professional Dark Theme Features:
• High contrast for readability
• Reduced eye strain
• Clean, minimal design
• No distracting animations
• Accessibility focused
    `;
    
    alert(helpContent);
}

function cancelCurrentOperation() {
    // Cancel any running operations
    console.log('Operation cancelled by user');
}

// Utility functions for professional UX
function addToConsole(message, type = 'info') {
    const consoles = document.querySelectorAll('.console');
    const timestamp = new Date().toLocaleTimeString();
    
    const typePrefix = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    
    const formattedMessage = `[${timestamp}] ${typePrefix[type] || '•'} ${message}\n`;
    
    consoles.forEach(console => {
        console.textContent += formattedMessage;
        console.scrollTop = console.scrollHeight;
    });
}

function showNotification(message, type = 'info') {
    // Professional toast notification (minimal)
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--panel-bg);
        color: var(--text-primary);
        padding: 12px 16px;
        border-radius: 4px;
        border-left: 4px solid var(--accent-primary);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Export functions for use in other scripts
window.TermTools = {
    addToConsole,
    showNotification,
    clearConsole,
    showHelp
};

// Professional error handling
window.addEventListener('error', function(e) {
    console.error('TermTools Error:', e.error);
    addToConsole(`Error: ${e.message}`, 'error');
});

// Prevent context menu in production (professional apps)
if (window.location.protocol !== 'file:') {
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });
}
