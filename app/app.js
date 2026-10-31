// Page behaviour: the day switcher on Today, the saved checkboxes on the checklist, and offline support.
const days = [...document.querySelectorAll('.day')];
const chips = [...document.querySelectorAll('.chips button')];

function showDay(date) {
  days.forEach((day) => { day.hidden = day.dataset.date !== date; });
  chips.forEach((chip) => chip.classList.toggle('on', chip.dataset.date === date));
  localStorage.setItem('shownDay', date);
}

if (days.length) {
  // Today in the trip's timezone, so the right day shows even when the phone's clock is elsewhere.
  const today = new Date().toLocaleDateString('en-CA', { timeZone: document.body.dataset.timezone });
  const dates = days.map((day) => day.dataset.date);
  const chosen = dates.includes(today) ? today : (dates.includes(localStorage.getItem('shownDay')) ? localStorage.getItem('shownDay') : dates[0]);
  chips.forEach((chip) => chip.addEventListener('click', () => showDay(chip.dataset.date)));
  showDay(chosen);
}

const boxes = [...document.querySelectorAll('input[type=checkbox][data-id]')];
function updateProgress() {
  const progress = document.getElementById('progress');
  if (progress) progress.textContent = `${boxes.filter((box) => box.checked).length} of ${boxes.length} done`;
}
boxes.forEach((box) => {
  box.checked = localStorage.getItem(`check:${box.dataset.id}`) === '1';
  box.addEventListener('change', () => { localStorage.setItem(`check:${box.dataset.id}`, box.checked ? '1' : '0'); updateProgress(); });
});
updateProgress();

if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js');
