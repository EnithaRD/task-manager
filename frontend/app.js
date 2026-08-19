const form = document.getElementById('task-form');
const titleInput = document.getElementById('title');
const descriptionInput = document.getElementById('description');
const dueDateInput = document.getElementById('due-date');
const priorityInput = document.getElementById('priority');
const list = document.getElementById('task-list');
const searchInput = document.getElementById('search');
const filterCompletedSelect = document.getElementById('filter-completed');
const filterPrioritySelect = document.getElementById('filter-priority');
const sortBySelect = document.getElementById('sort-by');
const sortOrderSelect = document.getElementById('sort-order');

async function fetchTasks() {
  const params = new URLSearchParams();
  if (searchInput.value) params.set('search', searchInput.value);
  if (filterCompletedSelect.value) params.set('completed', filterCompletedSelect.value);
  if (filterPrioritySelect.value) params.set('priority', filterPrioritySelect.value);
  if (sortBySelect.value) {
    params.set('sort_by', sortBySelect.value);
    params.set('order', sortOrderSelect.value);
  }

  const query = params.toString();
  const res = await fetch(query ? `/api/tasks?${query}` : '/api/tasks');
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

    const priorityBadge = document.createElement('span');
    priorityBadge.className = `priority priority-${task.priority}`;
    priorityBadge.textContent = task.priority;

    const prioritySelect = document.createElement('select');
    prioritySelect.className = 'priority-select';
    ['low', 'medium', 'high'].forEach((value) => {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = value;
      if (value === task.priority) option.selected = true;
      prioritySelect.appendChild(option);
    });

    const savePriorityBtn = document.createElement('button');
    savePriorityBtn.textContent = 'Save Priority';
    savePriorityBtn.className = 'btn-secondary';
    savePriorityBtn.addEventListener('click', () => savePriority(task.id, prioritySelect.value));

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
    li.appendChild(priorityBadge);
    li.appendChild(deleteBtn);
    li.appendChild(notesArea);
    li.appendChild(saveNotesBtn);
    li.appendChild(dueDateField);
    li.appendChild(saveDueDateBtn);
    li.appendChild(prioritySelect);
    li.appendChild(savePriorityBtn);
    list.appendChild(li);
  });
}

async function toggleTask(task) {
  await fetch(`/api/tasks/${task.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: !task.completed }),
  });
  fetchTasks();
}

async function deleteTask(id) {
  await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
  fetchTasks();
}

async function saveNotes(id, notes) {
  await fetch(`/api/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes }),
  });
  fetchTasks();
}

async function saveDueDate(id, dueDate) {
  await fetch(`/api/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ due_date: dueDate || null }),
  });
  fetchTasks();
}

async function savePriority(id, priority) {
  await fetch(`/api/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ priority }),
  });
  fetchTasks();
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  await fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: titleInput.value,
      description: descriptionInput.value,
      due_date: dueDateInput.value || null,
      priority: priorityInput.value,
    }),
  });
  titleInput.value = '';
  descriptionInput.value = '';
  dueDateInput.value = '';
  priorityInput.value = 'medium';
  fetchTasks();
});

searchInput.addEventListener('input', fetchTasks);
filterCompletedSelect.addEventListener('change', fetchTasks);
filterPrioritySelect.addEventListener('change', fetchTasks);
sortBySelect.addEventListener('change', fetchTasks);
sortOrderSelect.addEventListener('change', fetchTasks);

fetchTasks();
