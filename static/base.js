// for static folder
// base.js




document.addEventListener('DOMContentLoaded', function() {
    // Get modal elements
    const logoutTrigger = document.getElementById('logoutTrigger');
    const logoutModal = document.getElementById('logoutModal');
    const cancelLogout = document.getElementById('cancelLogout');
    
    // Show modal when logout is clicked
    if (logoutTrigger) {
        logoutTrigger.addEventListener('click', function(e) {
            e.preventDefault();
            logoutModal.style.display = 'flex';
        });
    }
    
    // Hide modal when cancel is clicked
    if (cancelLogout) {
        cancelLogout.addEventListener('click', function() {
            logoutModal.style.display = 'none';
        });
    }
    
    // Hide modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === logoutModal) {
            logoutModal.style.display = 'none';
        }
    });
    
    // Handle form submission (optional additional handling)
    const logoutForm = document.getElementById('logoutForm');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(e) {
            // You could add additional logout handling here if needed
            // For example, showing a loading spinner
        });
    }
});


// Profile loading script
document.getElementById('profileLink').addEventListener('click', function(e) 
{e.preventDefault();
    
    fetch("{% url 'edit-profile' %}?partial=true")
        .then(response => response.text())
        .then(html => {
            document.getElementById('mainContent').innerHTML = html;
            attachEditProfileEvents();
        })
        .catch(error => {
            console.error('Error loading profile:', error);
            window.location.href = "{% url 'edit-profile' %}";
        });
});

function attachEditProfileEvents() {
    const closeBtn = document.querySelector('.close-btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            window.location.reload();
        });
    }
    
    // Handle form submission
    const form = document.querySelector('.login-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                document.getElementById('mainContent').innerHTML = html;
                attachEditProfileEvents();
            });
        });
    }
}
