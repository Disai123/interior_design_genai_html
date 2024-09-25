// Base URL for the API
const baseURL = 'http://127.0.0.1:8000';

// Function to show the login form and hide the register form
function showLoginForm() {
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('register-form').style.display = 'none';
}

// Function to show the register form and hide the login form
function showRegisterForm() {
  document.getElementById('login-form').style.display = 'none';
  document.getElementById('register-form').style.display = 'block';
}

// Function to toggle the Forgot Password modal
function toggleForgotPasswordModal() {
  const modal = document.getElementById('forgot-password-modal');
  modal.style.display = modal.style.display === 'block' ? 'none' : 'block';
}

// Function to handle the login process
function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;

  const data = {
    username: email,
    password: password,
  };

  fetch(baseURL + '/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
    .then(response => response.json())
    .then(data => {
      if (data.token) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('username', data.username);
        localStorage.setItem('email', data.email);
        window.location.href = '/frontend/start-design.html';
      } else {
        alert('Login Failed');
      }
    })
    .catch(error => {
      console.log(error);
      alert('Error:', error.message);
    });
}

// Function to handle the registration process
function handleRegister(event) {
  event.preventDefault();

  const username = document.getElementById('register-username').value;
  const email = document.getElementById('register-email').value;
  const password1 = document.getElementById('register-password').value;
  const password2 = document.getElementById('register-password2').value;

  const data = {
    username: username,
    email: email,
    password1: password1,
    password2: password2,
  };

  fetch(baseURL + '/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
    .then(response => response.json())
    .then(data => {
      alert('Successfully created user!');
      showLoginForm();
    })
    .catch(error => {
      alert('Error:', error.message);
    });
}

// Function to handle the forgot password process
function handleForgotPassword(event) {
  event.preventDefault();

  const email = document.getElementById('forgot-email').value;

  fetch(baseURL + '/forgot-password/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email: email }),
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById('forgot-password-message').innerText = 'Reset link sent to your email.';
    })
    .catch(error => {
      document.getElementById('forgot-password-message').innerText = 'Error sending email. Please try again.';
    });
}
