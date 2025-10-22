// static/js/login.js

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Basic client-side validation
            if (!email || !password) {
                alert('Please enter both email and password.');
                return;
            }

            if (!/^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/.test(email)) {
                alert('Please enter a valid email address.');
                return;
            }

            console.log('Attempting to log in with:', { email, password });

            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Login successful!');
                    window.location.href = '/dashboard'; // Redirect to a dashboard page
                } else {
                    alert('Login failed: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred during login. Please try again.');
            });
        });
    }
});
