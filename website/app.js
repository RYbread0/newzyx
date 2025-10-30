const summariesEl = document.getElementById('summaries');
const updatedEl = document.getElementById('updated');
const whichDayEl = document.getElementById('whichDay');
const player = document.getElementById('player');

// --- Modal helpers ---
const modal = document.getElementById('dateModal');
const openModal = () => { modal.classList.add('open'); modal.setAttribute('aria-hidden', 'false'); };
const closeModal = () => { modal.classList.remove('open'); modal.setAttribute('aria-hidden', 'true'); };

document.getElementById('calendarBtn').addEventListener('click', openModal);
document.querySelectorAll('[data-close]').forEach(el => el.addEventListener('click', closeModal));
document.getElementById('dateCancel').addEventListener('click', closeModal);

// Convert yyyy-mm-dd to folder "M.D.YY" (no leading zeros, 2-digit year)
function toFolderName(dateStr) {
  const [yyyy, mm, dd] = dateStr.split('-').map(n => parseInt(n, 10));
  const shortYear = (yyyy % 100).toString().padStart(2, '0'); // 25
  const m = String(mm); // no leading zero
  const d = String(dd); // no leading zero
  return `${m}.${d}.${shortYear}`; // e.g., 9.16.25
}

// Build path for a file given an optional folder ('' = latest/root)
function pathFor(folder, filename) {
  return folder ? `${folder}/${filename}` : filename;
}

async function loadSummaries(pathTxt) {
  const url = `${pathTxt}?t=${Date.now()}`; // cache-bust
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error('Could not load ' + pathTxt);
  const text = await res.text();
  summariesEl.textContent = text;

  const lastMod = res.headers.get('Last-Modified');
  const when = lastMod ? new Date(lastMod) : new Date();
  updatedEl.textContent = 'Updated ' + when.toLocaleString();
}

async function loadDay(folder /* e.g., "9.16.25" or "" for latest */) {
  const txtPath = pathFor(folder, 'kids_summaries.txt');
  const mp3Path = pathFor(folder, 'kids_3min_summary.mp3');

  whichDayEl.textContent = 'Showing: ' + (folder ? folder : 'Latest');
  summariesEl.textContent = 'Loading summaries…';
  player.src = mp3Path + `?t=${Date.now()}`;

  try {
    await loadSummaries(txtPath);
  } catch (e) {
    summariesEl.textContent = 'Could not load summaries for this date.';
    updatedEl.textContent = '—';
  }
}

document.getElementById('dateApply').addEventListener('click', async () => {
  const val = document.getElementById('dateInput').value; // yyyy-mm-dd
  if (!val) return;
  const folder = toFolderName(val);
  closeModal();
  await loadDay(folder);
});

document.getElementById('latestBtn').addEventListener('click', () => loadDay(''));

// Initial load (Latest/root)
loadDay('');
