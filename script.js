// SCAD registration form script.

const form = document.getElementById('scad-form');
const membersBox = document.getElementById('group-members');

// "Add a group member" adds a row with first name, last name and email
document.getElementById('add-member').addEventListener('click', function () {
  const row = document.createElement('div');
  row.className = 'member-row';
  row.innerHTML = `
    <input type="text" class="member-first" placeholder="First name" aria-label="First name" required>
    <input type="text" class="member-last" placeholder="Last name" aria-label="Last name" required>
    <input type="email" class="member-email" placeholder="Email" aria-label="Email" required>
    <button type="button" class="remove-member" aria-label="Remove group member">✕</button>
  `;
  row.querySelector('.remove-member').addEventListener('click', function () {
    row.remove();
  });
  membersBox.appendChild(row);
});

form.addEventListener('submit', function (event) {
  event.preventDefault(); // stop the page from reloading

  const data = Object.fromEntries(new FormData(form));

  // Group members become a list, one entry per person (matches the person table)
  data.group_members = Array.from(membersBox.querySelectorAll('.member-row')).map(function (row) {
    return {
      first_name: row.querySelector('.member-first').value.trim(),
      last_name: row.querySelector('.member-last').value.trim(),
      email: row.querySelector('.member-email').value.trim(),
    };
  });

  console.log(data);

  // TODO: send `data` to the Django API here

  alert('Submitted! (check the console for the data)');
});
