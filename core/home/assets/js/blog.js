const articles = JSON.parse(document.getElementById('stackArticles').textContent);
const layers = [...document.querySelectorAll('[data-sheet]')];
const older = document.getElementById('olderSheet');
const newer = document.getElementById('newerSheet');
const count = document.getElementById('sheetCount');
const status = document.getElementById('sheetStatus');
let selected = articles.length - 1;

function showSheet(index) {
  if (index < 0 || index >= articles.length) return;
  selected = index;
  const article = articles[index];
  layers.forEach((layer, position) => {
    layer.classList.toggle('selected-sheet', position === index);
    layer.classList.toggle('lifted-sheet', position > index);
  });
  document.getElementById('previewTitle').textContent = article.title;
  document.getElementById('previewMeta').textContent = article.category + ' / ' + article.read_minutes + ' min read';
  document.getElementById('previewDek').textContent = article.dek;
  document.getElementById('previewLink').href = article.url;
  count.textContent = 'Sheet ' + (index + 1) + ' of ' + articles.length;
  older.setAttribute('aria-disabled', String(index === 0));
  newer.setAttribute('aria-disabled', String(index === articles.length - 1));
  status.textContent = count.textContent + '. ' + article.title;
}

if (articles.length) {
  showSheet(selected);
  if (articles.length > 1) {
    document.getElementById('stackNavigation').hidden = false;
    older.addEventListener('click', () => showSheet(selected - 1));
    newer.addEventListener('click', () => showSheet(selected + 1));
    document.getElementById('stackHoverSurface').addEventListener('pointerenter', event => {
      if (event.pointerType === 'mouse') showSheet(selected - 1);
    });
    document.getElementById('stackHoverHint').hidden = false;
  }
}

const archive = document.getElementById('allEssays');
document.getElementById('archiveLink').addEventListener('click', () => { archive.open = true; });
if (window.location.hash === '#archive') archive.open = true;
