// Wait for DOM to load 
document.addEventListener("DOMContentLoaded", function() {

  // Query DOM
  const form = document.querySelector('form');
  
  // Attach submit handler
  form.addEventListener('submit', event => {

    event.preventDefault();
    
    // Submit form with fetch
    const data = new FormData(form);

    fetch('/submit_form', {
      method: 'POST',
      body: data 
    })
      .then(response => {
        console.log('Success!');  
      })
      .catch(error => {
        console.error('Error:', error);
      });

  });

});
