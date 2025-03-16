<script>
 
  document.getElementById('showLogin').addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
  });

 
  document.getElementById('showRegister').addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
  });

// Redirect after login form submission
document.getElementById('loginForm').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent the default submission (if using AJAX, remove if not needed)
  
  // Perform your login validation here if desired.
  // If validation is successful, redirect to the user profile page:
  window.location.href = '/profile/';  // Adjust the URL based on your Django URL configuration.
});

// Redirect after registration form submission
document.getElementById('registerForm').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent the default submission (if using AJAX, remove if not needed)
  
  // Perform your registration validation here if desired.
  // If registration is successful, redirect to the user profile page:
  window.location.href = '/profile/';  // Adjust the URL based on your Django URL configuration.
});
</script>
