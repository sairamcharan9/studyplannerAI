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

            console.log('Attempting to log in with:', { email });

            // Send data to backend API
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ identifier: email, password: password }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        let errorMessage = 'Login failed';
                        if (err.detail) {
                            if (Array.isArray(err.detail)) {
                                // FastAPI validation error (422)
                                errorMessage = err.detail.map(e => e.msg).join(', ');
                            } else {
                                errorMessage = err.detail;
                            }
                        }
                        throw new Error(errorMessage);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Login successful:', data);
                // Store user info in localStorage for persistence (simple demo approach)
                localStorage.setItem('user', JSON.stringify(data.user));
                window.location.href = '/'; // Redirect to the home page
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message);
            });
        });
    }
});
