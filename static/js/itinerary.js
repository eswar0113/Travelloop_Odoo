function appendActivityCard(stopId, data) {
  const container = document.getElementById('activities-' + stopId);
  const empty = document.getElementById('empty-' + stopId);

  const icons = {
    sightseeing: '📸', food: '🍜', adventure: '🏔️', culture: '🏛️'
  };
  const colorMap = {
    sightseeing: 'bg-sky-100 text-sky-600',
    food: 'bg-amber-100 text-amber-600',
    adventure: 'bg-emerald-100 text-emerald-600',
    culture: 'bg-purple-100 text-purple-600'
  };

  const icon = icons[data.category] || '⭐';
  const color = colorMap[data.category] || 'bg-slate-200 text-slate-500';

  const div = document.createElement('div');
  div.id = 'sa-' + data.sa_id;
  div.className = 'flex items-center gap-3 p-3 bg-slate-50 rounded-xl';
  div.innerHTML = `
    <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${color}">${icon}</div>
    <div class="flex-1 min-w-0">
      <p class="text-sm font-semibold text-slate-700 truncate">${data.activity}</p>
      <p class="text-xs text-slate-400">$${Math.round(data.cost)}</p>
    </div>
    <button onclick="removeActivity(${data.sa_id}, 'sa-${data.sa_id}')"
            class="text-red-400 hover:text-red-600 p-1 rounded transition">
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  `;

  if (empty) empty.remove();

  if (!container) {
    const stopCard = document.querySelector(`[data-id] .p-4`);
    const newContainer = document.createElement('div');
    newContainer.id = 'activities-' + stopId;
    newContainer.className = 'space-y-2';
    newContainer.appendChild(div);
    document.querySelector(`[data-id="${stopId}"] .p-4`).appendChild(newContainer);
  } else {
    container.appendChild(div);
  }
}
