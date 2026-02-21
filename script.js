// ─── Tab Switching ───────────────────────────────────────────────────────────

const tabs = document.querySelectorAll('.tab');
const forms = document.querySelectorAll('.form');

function switchTab(tabName) {
  tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
  forms.forEach(f => f.classList.toggle('active', f.id === tabName));
  clearAllErrors();
}

tabs.forEach(tab => {
  tab.addEventListener('click', () => switchTab(tab.dataset.tab));
});

document.querySelectorAll('[data-switch]').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    switchTab(link.dataset.switch);
  });
});


// ─── Validation Helpers ──────────────────────────────────────────────────────

function showError(inputId, message) {
  const input = document.getElementById(inputId);
  const error = document.getElementById(inputId + '-error');
  input.classList.add('invalid');
  if (error) error.textContent = message;
}

function clearAllErrors() {
  document.querySelectorAll('input').forEach(i => i.classList.remove('invalid'));
  document.querySelectorAll('.error').forEach(e => e.textContent = '');
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

document.querySelectorAll('input').forEach(input => {
  input.addEventListener('input', () => {
    input.classList.remove('invalid');
    const errEl = document.getElementById(input.id + '-error');
    if (errEl) errEl.textContent = '';
  });
});


// ─── Toast ───────────────────────────────────────────────────────────────────

function showToast(message, duration = 3000) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}


// ─── Login ───────────────────────────────────────────────────────────────────

document.getElementById('login').addEventListener('submit', function (e) {
  e.preventDefault();
  clearAllErrors();

  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  let valid = true;

  if (!email) {
    showError('login-email', 'Email is required.');
    valid = false;
  } else if (!isValidEmail(email)) {
    showError('login-email', 'Please enter a valid email.');
    valid = false;
  }

  if (!password) {
    showError('login-password', 'Password is required.');
    valid = false;
  }

  if (!valid) return;

  showToast('Signed in successfully!');
  this.reset();
});


// ─── Register ────────────────────────────────────────────────────────────────

document.getElementById('register').addEventListener('submit', function (e) {
  e.preventDefault();
  clearAllErrors();

  const name     = document.getElementById('reg-name').value.trim();
  const email    = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const confirm  = document.getElementById('reg-confirm').value;
  let valid = true;

  if (!name) {
    showError('reg-name', 'Name is required.');
    valid = false;
  }

  if (!email) {
    showError('reg-email', 'Email is required.');
    valid = false;
  } else if (!isValidEmail(email)) {
    showError('reg-email', 'Please enter a valid email.');
    valid = false;
  }

  if (!password) {
    showError('reg-password', 'Password is required.');
    valid = false;
  } else if (password.length < 8) {
    showError('reg-password', 'Password must be at least 8 characters.');
    valid = false;
  }

  if (!confirm) {
    showError('reg-confirm', 'Please confirm your password.');
    valid = false;
  } else if (password && confirm !== password) {
    showError('reg-confirm', 'Passwords do not match.');
    valid = false;
  }

  if (!valid) return;

  showToast('Account created! You can now sign in.');
  this.reset();
  setTimeout(() => switchTab('login'), 1500);
});