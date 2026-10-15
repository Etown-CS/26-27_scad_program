// SCAD registration form script.
// On submit, sends the form data as JSON to the Django API.

const form = document.getElementById('scad-form');
const membersBox = document.getElementById('group-members');
const API_URL = '/api/submissions/';

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

form.addEventListener('submit', async function (event) {
  event.preventDefault(); // stop the page from reloading

  const data = Object.fromEntries(new FormData(form));

  // Django's security token goes in a header, not in the data
  const csrfToken = data.csrfmiddlewaretoken;
  delete data.csrfmiddlewaretoken;

  // Group members become a list, one entry per person (matches the person table)
  data.group_members = Array.from(membersBox.querySelectorAll('.member-row')).map(function (row) {
    return {
      first_name: row.querySelector('.member-first').value.trim(),
      last_name: row.querySelector('.member-last').value.trim(),
      email: row.querySelector('.member-email').value.trim(),
    };
  });

  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(data),
    });

    // Django sends back JSON like {"message": "..."} or {"error": "..."}
    const result = await response.json().catch(function () { return {}; });

    if (response.ok) {
      showMessage('Thank you! Your registration was received.', 'success');
      form.reset();
      membersBox.innerHTML = '';
    } else {
      showMessage(result.error || 'Something went wrong. Please try again.', 'error');
    }
  } catch (error) {
    showMessage('Could not reach the server. Please try again.', 'error');
  } finally {
    button.disabled = false;
  }
});

// Shows a success or error box under the submit button
function showMessage(text, type) {
  let box = document.getElementById('form-message');
  if (!box) {
    box = document.createElement('p');
    box.id = 'form-message';
    form.appendChild(box);
  }
  box.className = 'message ' + type;
  box.textContent = text;
}