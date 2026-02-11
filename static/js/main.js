/**
 * Enhanced JavaScript utilities for Stock Research Platform
 */

// CSRF Token handling
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

const csrftoken = getCookie('csrftoken');

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add to portfolio
async function addToPortfolio(callId) {
    const entryPrice = prompt('Enter your entry price:');
    if (!entryPrice) return;

    const quantity = prompt('Enter quantity:');
    if (!quantity) return;

    const formData = new FormData();
    formData.append('call_id', callId);
    formData.append('entry_price', entryPrice);
    formData.append('quantity', quantity);
    formData.append('csrfmiddlewaretoken', csrftoken);

    try {
        const response = await fetch('/portfolio/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Added to portfolio successfully!', 'success');
        } else {
            showNotification(data.error || 'Failed to add to portfolio', 'danger');
        }
    } catch (error) {
        showNotification('An error occurred', 'danger');
    }
}

// Add to watchlist
async function addToWatchlist(callId) {
    const formData = new FormData();
    formData.append('call_id', callId);
    formData.append('csrfmiddlewaretoken', csrftoken);

    try {
        const response = await fetch('/watchlist/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Added to watchlist!', 'success');
        } else {
            showNotification(data.error || 'Failed to add to watchlist', 'danger');
        }
    } catch (error) {
        showNotification('An error occurred', 'danger');
    }
}

// Exit position
async function exitPosition(itemId) {
    const exitPrice = prompt('Enter exit price:');
    if (!exitPrice) return;

    if (!confirm('Are you sure you want to exit this position?')) return;

    const formData = new FormData();
    formData.append('exit_price', exitPrice);
    formData.append('csrfmiddlewaretoken', csrftoken);

    try {
        const response = await fetch(`/portfolio/${itemId}/exit/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        });

        if (response.ok) {
            showNotification('Position closed successfully!', 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showNotification('Failed to close position', 'danger');
        }
    } catch (error) {
        showNotification('An error occurred', 'danger');
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    console.log('Stock Research Platform initialized');
});
