const form = document.getElementById('task-form');
const titleInput = document.getElementById('title');
const descriptionInput = document.getElementById('description');
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

    const prioritySpan = document.createElement('span');
    prioritySpan.className = `priority priority-${task.priority}`;
    prioritySpan.textContent = task.priority;

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.addEventListener('click', () => deleteTask(task.id));

    li.appendChild(span);
    li.appendChild(prioritySpan);
    li.appendChild(deleteBtn);
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

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  await fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: titleInput.value,
      description: descriptionInput.value,
      priority: priorityInput.value,
    }),
  });
  titleInput.value = '';
  descriptionInput.value = '';
  priorityInput.value = 'medium';
  fetchTasks();
});

searchInput.addEventListener('input', fetchTasks);
filterCompletedSelect.addEventListener('change', fetchTasks);
filterPrioritySelect.addEventListener('change', fetchTasks);
sortBySelect.addEventListener('change', fetchTasks);
sortOrderSelect.addEventListener('change', fetchTasks);

fetchTasks();
