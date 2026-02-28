// ─── Toast Notification ──────────────────────────────────────────────────────

function showToast(message) {
  var toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');

  setTimeout(function() {
    toast.classList.remove('show');
  }, 3000);
}


// ─── Error Helpers ───────────────────────────────────────────────────────────

function showError(inputId, message) {
  var input = document.getElementById(inputId);
  var errorSpan = document.getElementById(inputId + '-error');
  input.classList.add('invalid');
  errorSpan.textContent = message;
}

function clearErrors() {
  var inputs = document.querySelectorAll('input');
  for (var i = 0; i < inputs.length; i++) {
    inputs[i].classList.remove('invalid');
  }

  var errors = document.querySelectorAll('.error');
  for (var i = 0; i < errors.length; i++) {
    errors[i].textContent = '';
  }
}

function isValidEmail(email) {
  return email.includes('@') && email.includes('.');
}

// Clear error when user starts typing
var allInputs = document.querySelectorAll('input');
for (var i = 0; i < allInputs.length; i++) {
  allInputs[i].oninput = function() {
    this.classList.remove('invalid');
    var errorSpan = document.getElementById(this.id + '-error');
    if (errorSpan) {
      errorSpan.textContent = '';
    }
  };
}


// ─── Login Form ──────────────────────────────────────────────────────────────

var loginForm = document.getElementById('login-form');

if (loginForm) {
  loginForm.onsubmit = function(e) {
    e.preventDefault();
    clearErrors();

    var email = document.getElementById('login-email').value.trim();
    var password = document.getElementById('login-password').value;
    var isValid = true;

    if (email === '') {
      showError('login-email', 'Email is required.');
      isValid = false;
    } else if (!isValidEmail(email)) {
      showError('login-email', 'Please enter a valid email.');
      isValid = false;
    }

    if (password === '') {
      showError('login-password', 'Password is required.');
      isValid = false;
    }

    if (!isValid) {
      return;
    }

    showToast('Signed in successfully!');
    this.reset();
  };
}


// ─── Register Form ───────────────────────────────────────────────────────────

var registerForm = document.getElementById('register-form');

if (registerForm) {
  registerForm.onsubmit = function(e) {
    e.preventDefault();
    clearErrors();

    var idnum    = document.getElementById('reg-idnum').value.trim();
    var name     = document.getElementById('reg-name').value.trim();
    var email    = document.getElementById('reg-email').value.trim();
    var level    = document.getElementById('reg-level').value.trim();
    var address  = document.getElementById('reg-address').value.trim();
    var password = document.getElementById('reg-password').value;
    var confirm  = document.getElementById('reg-confirm').value;
    var isValid  = true;

    if (idnum === '') {
      showError('reg-idnum', 'ID Number is required.');
      isValid = false;
    }

    if (name === '') {
      showError('reg-name', 'Name is required.');
      isValid = false;
    }

    if (email === '') {
      showError('reg-email', 'Email is required.');
      isValid = false;
    } else if (!isValidEmail(email)) {
      showError('reg-email', 'Please enter a valid email.');
      isValid = false;
    }

    if (level === '') {
      showError('reg-level', 'Year level is required.');
      isValid = false;
    }

    if (address === '') {
      showError('reg-address', 'Address is required.');
      isValid = false;
    }

    if (password === '') {
      showError('reg-password', 'Password is required.');
      isValid = false;
    } else if (password.length < 8) {
      showError('reg-password', 'Password must be at least 8 characters.');
      isValid = false;
    }

    if (confirm === '') {
      showError('reg-confirm', 'Please confirm your password.');
      isValid = false;
    } else if (confirm !== password) {
      showError('reg-confirm', 'Passwords do not match.');
      isValid = false;
    }

    if (!isValid) {
      return;
    }

    showToast('Account created! You can now sign in.');
    this.reset();

    setTimeout(function() {
      window.location.href = 'login.html';
    }, 1500);
  };
}