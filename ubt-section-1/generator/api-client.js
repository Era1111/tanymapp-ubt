/* Optional integration. Not loaded by the lessons; no backend is configured. */
export async function submitAttempt(endpoint, attempt, token) {
  if (!endpoint || !/^https:\/\//.test(endpoint)) throw new Error('Configure an HTTPS API endpoint first.');
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {'Content-Type':'application/json', ...(token ? {Authorization:`Bearer ${token}`} : {})},
    body: JSON.stringify(attempt),
  });
  if (!response.ok) throw new Error(`Attempt was not saved: HTTP ${response.status}`);
  return response.json();
}
