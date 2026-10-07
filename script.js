// SCAD registration form script.
// Right now it only handles submitting. Later this is where we can:
//  - save the submission to Supabase
//  - hide the panel section when "Poster" is picked
//  - show a live word count for the abstract
//  - check for an @etown.edu email

const form = document.getElementById('scad-form');

form.addEventListener('submit', function (event) {
  event.preventDefault(); // stop the page from reloading

  const data = Object.fromEntries(new FormData(form));
  console.log(data);

  // TODO: send `data` to Supabase here

  alert('Submitted! (check the console for the data)');
});
