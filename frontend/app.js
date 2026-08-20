const form = document.getElementById('task-form');
const titleInput = document.getElementById('title');
const descriptionInput = document.getElementById('description');
const dueDateInput = document.getElementById('due-date');
const priorityInput = document.getElementById('priority');
const categoryInput = document.getElementById('category');
const list = document.getElementById('task-list');
const searchInput = document.getElementById('search');
const filterCompletedSelect = document.getElementById('filter-completed');
const filterPrioritySelect = document.getElementById('filter-priority');
const filterCategorySelect = document.getElementById('filter-category');
const sortBySelect = document.getElementById('sort-by');
const sortOrderSelect = document.getElementById('sort-order');

async function fetchTasks() {
  const params = new URLSearchParams();
  if (searchInput.value) params.set('search', searchInput.value);
  if (filterCompletedSelect.value) params.set('completed', filterCompletedSelect.value);
  if (filterPrioritySelect.value) params.set('priority', filterPrioritySelect.value);
  if (filterCategorySelect.value) params.set('category', filterCategorySelect.value);
  if (sortBySelect.value) {
    params.set('sort_by', sortBySelect.value);
    params.set('order', sortOrderSelect.value);
  }

  const query = params.toString();
  const res = await fetch(query ? `/tasks?${query}` : '/tasks');
  const tasks = await res.json();
  renderTasks(tasks);
}

function renderTasks(tasks) {
  list.innerHTML = '';
  tasks.forEach((task) => {
    const li = document.createElement('li');
    if (task.completed) li.classList.add('completed');

    const span = document.createElement('span');
    span.className = 'title';
    span.textContent = task.title;
    span.addEventListener('click', () => toggleTask(task));

    const prioritySpan = document.createElement('span');
    prioritySpan.className = `priority priority-${task.priority}`;
    prioritySpan.textContent = task.priority;

    const categorySpan = document.createElement('span');
    categorySpan.className = 'category';
    categorySpan.textContent = task.category;

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.className = 'btn-delete';
    deleteBtn.addEventListener('click', () => deleteTask(task.id));

    const notesArea = document.createElement('textarea');
    notesArea.className = 'notes-textarea';
    notesArea.value = task.notes;

    const saveNotesBtn = document.createElement('button');
    saveNotesBtn.textContent = 'Save Notes';
    saveNotesBtn.className = 'btn-secondary';
    saveNotesBtn.addEventListener('click', () => saveNotes(task.id, notesArea.value));

    const dueDateField = document.createElement('input');
    dueDateField.type = 'date';
    dueDateField.className = 'due-date-input';
    dueDateField.value = task.due_date || '';

    const saveDueDateBtn = document.createElement('button');
    saveDueDateBtn.textContent = 'Save Due Date';
    saveDueDateBtn.className = 'btn-secondary';
    saveDueDateBtn.addEventListener('click', () => saveDueDate(task.id, dueDateField.value));

    li.appendChild(span);
    li.appendChild(prioritySpan);
    li.appendChild(categorySpan);
    li.appendChild(deleteBtn);
    li.appendChild(notesArea);
    li.appendChild(saveNotesBtn);
    li.appendChild(dueDateField);
    li.appendChild(saveDueDateBtn);
    list.appendChild(li);
  });
}

async function toggleTask(task) {
  await fetch(`/tasks/${task.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: !task.completed }),
  });
  fetchTasks();
}

async function deleteTask(id) {
  await fetch(`/tasks/${id}`, { method: 'DELETE' });
  fetchTasks();
}

async function saveNotes(id, notes) {
  await fetch(`/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes }),
  });
  fetchTasks();
}

async function saveDueDate(id, dueDate) {
  await fetch(`/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ due_date: dueDate || null }),
  });
  fetchTasks();
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  await fetch('/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: titleInput.value,
      description: descriptionInput.value,
      due_date: dueDateInput.value || null,
      priority: priorityInput.value,
      category: categoryInput.value,
    }),
  });
  titleInput.value = '';
  descriptionInput.value = '';
  dueDateInput.value = '';
  priorityInput.value = 'medium';
  categoryInput.value = 'Other';
  fetchTasks();
});

searchInput.addEventListener('input', fetchTasks);
filterCompletedSelect.addEventListener('change', fetchTasks);
filterPrioritySelect.addEventListener('change', fetchTasks);
filterCategorySelect.addEventListener('change', fetchTasks);
sortBySelect.addEventListener('change', fetchTasks);
sortOrderSelect.addEventListener('change', fetchTasks);

fetchTasks();
