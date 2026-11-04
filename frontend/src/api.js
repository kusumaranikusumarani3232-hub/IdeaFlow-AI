// API client helper for IdeaFlow AI

const API_BASE = '';

export async function fetchProjects() {
  const res = await fetch(`${API_BASE}/api/projects`);
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function fetchProjectDetails(id) {
  const res = await fetch(`${API_BASE}/api/projects/${id}`);
  if (!res.ok) throw new Error('Failed to fetch project details');
  return res.json();
}

export async function createProject(data) {
  const res = await fetch(`${API_BASE}/api/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to create project');
  return res.json();
}

export async function updateTaskStatus(taskId, status) {
  const res = await fetch(`${API_BASE}/api/projects/tasks/${taskId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  if (!res.ok) throw new Error('Failed to update task');
  return res.json();
}

export async function createTask(projectId, taskData) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(taskData)
  });
  if (!res.ok) throw new Error('Failed to create task');
  return res.json();
}

export async function createDecision(projectId, decisionData) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/decisions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(decisionData)
  });
  if (!res.ok) throw new Error('Failed to create decision');
  return res.json();
}

export async function createDraft(projectId, draftData) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/drafts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(draftData)
  });
  if (!res.ok) throw new Error('Failed to create draft');
  return res.json();
}

export async function sendChatMessage(projectId, content, senderName = 'Alex (Creator)') {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, sender_name: senderName, platform: 'web' })
  });
  if (!res.ok) throw new Error('Failed to send message');
  return res.json();
}

export async function fetchSwitchStatus() {
  const res = await fetch(`${API_BASE}/api/switch/status`);
  if (!res.ok) throw new Error('Failed to fetch Switch status');
  return res.json();
}

export async function fetchSwitchEvents(limit = 30) {
  const res = await fetch(`${API_BASE}/api/switch/events?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch Switch events');
  return res.json();
}

export async function sendManualBeat() {
  const res = await fetch(`${API_BASE}/api/switch/beat`, { method: 'POST' });
  return res.json();
}

export async function updateRuntimeConfig(config) {
  const res = await fetch(`${API_BASE}/api/switch/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });
  if (!res.ok) throw new Error('Failed to update runtime config');
  return res.json();
}



export async function fetchDiscordStatus() {
  const res = await fetch(`${API_BASE}/api/discord/status`);
  if (!res.ok) throw new Error('Failed to fetch Discord status');
  return res.json();
}

export async function simulateDiscordMessage(content, author = 'Alex', channelName = '#creative-lounge') {
  const res = await fetch(`${API_BASE}/api/discord/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, author, channel_name: channelName })
  });
  if (!res.ok) throw new Error('Failed to simulate Discord message');
  return res.json();
}

export async function fetchProjectSummary(projectId) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/summary`);
  if (!res.ok) throw new Error('Failed to fetch project summary');
  return res.json();
}

export async function aiBrainstorm(concept, category = 'video', vibe = 'Cinematic, inspiring') {
  const res = await fetch(`${API_BASE}/api/ai/brainstorm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ concept, category, vibe })
  });
  if (!res.ok) throw new Error('Failed to brainstorm');
  return res.json();
}

export async function aiDecompose(projectId, goal) {
  const res = await fetch(`${API_BASE}/api/ai/decompose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, goal })
  });
  if (!res.ok) throw new Error('Failed to decompose goal');
  return res.json();
}

export async function aiGenerateScript(projectId, prompt) {
  const res = await fetch(`${API_BASE}/api/ai/script`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, prompt })
  });
  if (!res.ok) throw new Error('Failed to generate script');
  return res.json();
}

