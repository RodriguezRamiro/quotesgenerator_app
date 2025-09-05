//static/js/app.js

let lastExternalQuote = null;
let editingId = null;

// Fetch a random local quote
async function getRandomQuote() {
  const res = await fetch('/api/quotes/random');
  const data = await res.json();
  document.getElementById('quote-text').innerText = `"${data.text}"`;
  document.getElementById('quote-author').innerText = `- ${data.author}`;
  document.getElementById('saveBtn').disabled = true;
}

// Fetch a random external quote
async function getExternalQuote() {
  const res = await fetch('/api/quotes/external');
  const data = await res.json();
  lastExternalQuote = data;
  document.getElementById('quote-text').innerText = `"${data.text}"`;
  document.getElementById('quote-author').innerText = `- ${data.author}`;
  document.getElementById('saveBtn').disabled = false;
}

// Save the last external quote
async function saveExternalQuote() {
  if (!lastExternalQuote) return;
  const res = await fetch('/api/quotes/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(lastExternalQuote)
  });
  const result = await res.json();
  alert(result.message || "Saved!");
  document.getElementById('saveBtn').disabled = true;
  loadAllQuotes();
}

// Delete a quote
async function deleteQuote(id) {
  if (!confirm("Do you want to delete this Quote?")) return;

  const res = await fetch(`/api/quotes/${id}`, { method: 'DELETE' });
  const data = await res.json();
  alert(data.message || data.error);
  loadAllQuotes();
}

// Load all quotes
async function loadAllQuotes() {
  const res = await fetch('/api/quotes');
  const data = await res.json();
  const container = document.getElementById('all-quotes');
  container.innerHTML = data.map(q => `
    <div class="quote-item" id="quote-${q.id}">
      <p>"${q.text}" — ${q.author}</p>
      <button onclick="openModal(${q.id}, \`${q.text}\`, \`${q.author}\`)">Edit</button>
      <button class="delete-btn" onclick="deleteQuote(${q.id})">Delete</button>
    </div>
  `).join("");
}

// Open modal for editing
function openModal(id, text, author) {
  editingId = id;
  document.getElementById('edit-text').value = text;
  document.getElementById('edit-author').value = author;
  document.getElementById('editModal').style.display = 'flex';
}

// Save edits
async function saveEdit() {
  const text = document.getElementById('edit-text').value;
  const author = document.getElementById('edit-author').value;

  const res = await fetch(`/api/quotes/${editingId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, author })
  });

  if (res.ok) {
    alert('Quote updated successfully!');
    closeModal();
    loadAllQuotes();
  } else {
    alert('Failed to update quote.');
  }
}

// Close modal
function closeModal() {
  editingId = null;
  document.getElementById('editModal').style.display = 'none';
}

// Close modal if clicked outside
window.addEventListener('click', (e) => {
  const modal = document.getElementById('editModal');
  if (e.target === modal) {
    closeModal();
  }
});

// Handle add-quote form submission
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById('quote-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = document.getElementById('new-quote-text').value;
    const author = document.getElementById('new-quote-author').value;

    const res = await fetch('/api/quotes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, author })
    });

    if (res.ok) {
      alert('Quote added successfully!');
      document.getElementById('quote-form').reset();
      loadAllQuotes();
    } else {
      alert('Failed to add quote.');
    }
  });

  // Initial load of all quotes
  loadAllQuotes();
});
