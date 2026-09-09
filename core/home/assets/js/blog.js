const data = document.getElementById('cubeArticles');
const articles = JSON.parse(data.textContent);
const canvas = document.getElementById('blogCube');
const points = document.getElementById('cubePoints');
const explorer = document.getElementById('cubeExplorer');
const preview = document.getElementById('articlePreview');
const connector = document.getElementById('cubeConnector');
const status = document.getElementById('cubeStatus');
const range = document.getElementById('growthRange');
const growthToggle = document.getElementById('growthToggle');
const growthControls = document.getElementById('growthControls');
let cube;
let currentIndex = 0;
let lastPoint;

function showArticle(index, source) {
  const article = articles[index];
  if (!article) return;
  currentIndex = index;
  document.getElementById('previewTitle').textContent = article.title;
  document.getElementById('previewMeta').textContent = `${article.category} / ${article.read_minutes} min read`;
  document.getElementById('previewDek').textContent = article.dek;
  document.getElementById('previewLink').href = article.url;
  if (source === 'keyboard' || source === 'focus' || source === 'click') {
    document.getElementById('selectionStatus').textContent = `Selected: ${article.title} Press Enter to reach the article link.`;
  }
}

function updateConnector(point) {
  lastPoint = point;
  if (!point || window.innerWidth <= 760) {
    connector.hidden = true;
    return;
  }
  const rootRect = explorer.getBoundingClientRect();
  const stageRect = canvas.getBoundingClientRect();
  const previewRect = preview.getBoundingClientRect();
  const x = stageRect.left - rootRect.left + point.x;
  const y = stageRect.top - rootRect.top + point.y;
  const endX = previewRect.left - rootRect.left;
  const endY = previewRect.top - rootRect.top + 62;
  const dx = endX - x;
  const dy = endY - y;
  connector.hidden = false;
  connector.style.left = `${x}px`;
  connector.style.top = `${y}px`;
  connector.style.width = `${Math.hypot(dx, dy)}px`;
  connector.style.transform = `rotate(${Math.atan2(dy, dx)}rad)`;
}

function clearSelection() {
  cube?.setSelected(null);
  updateConnector(null);
}

function resetView() {
  cube?.reset();
  showArticle(0);
  document.getElementById('selectionStatus').textContent = '';
  updateConnector(null);
}

function setCount(count) {
  const nextCount = Math.min(articles.length, Math.max(1, Number(count)));
  range.value = String(nextCount);
  document.getElementById('growthCount').value = String(nextCount);
  document.getElementById('growthExplanation').textContent = nextCount <= 9
    ? `${nextCount} of 9 points in the first square. Earlier points keep their place.`
    : nextCount <= 27
      ? `${nextCount} articles, ${Math.ceil(nextCount / 9)} layers. Earlier points keep their place.`
      : `${nextCount} articles. New points extend the cube's outer shell; earlier points keep their place.`;
  cube?.setCount(nextCount);
  if (currentIndex >= nextCount) showArticle(0);
  updateConnector(null);
}

document.getElementById('resetCube').addEventListener('click', resetView);
growthToggle.addEventListener('click', event => {
  const opening = event.currentTarget.getAttribute('aria-expanded') !== 'true';
  event.currentTarget.setAttribute('aria-expanded', String(opening));
  growthControls.hidden = !opening;
});
range.addEventListener('input', () => setCount(range.value));
document.querySelectorAll('[data-count]').forEach(button => {
  button.addEventListener('click', () => setCount(button.dataset.count));
});
explorer.addEventListener('mouseleave', () => {
  if (!explorer.contains(document.activeElement)) clearSelection();
});
explorer.addEventListener('pointerenter', event => {
  if (event.pointerType === 'mouse' && !explorer.contains(document.activeElement)) clearSelection();
}, { once: true });
explorer.addEventListener('focusout', event => {
  if (!explorer.contains(event.relatedTarget)) clearSelection();
});
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  if (!growthControls.hidden && (growthControls.contains(event.target) || event.target === growthToggle)) {
    event.preventDefault();
    growthControls.hidden = true;
    growthToggle.setAttribute('aria-expanded', 'false');
    growthToggle.focus();
  } else if (explorer.contains(event.target)) {
    event.preventDefault();
    resetView();
  }
});
points.addEventListener('keydown', event => {
  if (event.key === 'Enter' && event.target.matches('.cube-pin')) {
    event.preventDefault();
    const index = Number(event.target.dataset.index);
    cube?.setSelected(index);
    showArticle(index, 'keyboard');
    document.getElementById('previewLink').focus();
  }
});
window.addEventListener('resize', () => updateConnector(lastPoint));

try {
  const { createBlogCube } = await import('./blog-cube.js');
  cube = await createBlogCube({
    canvas,
    pointLayer: points,
    articles,
    environmentUrl: canvas.dataset.environment,
    onSelect: showArticle,
    onProject: updateConnector,
    onReady: () => {
      status.hidden = true;
      document.getElementById('cubeTools').hidden = false;
      explorer.dataset.ready = 'true';
    },
    onError: () => {
      status.hidden = false;
      status.textContent = 'Explore the writing below. Every article is available in the list.';
      points.hidden = true;
      explorer.dataset.ready = 'fallback';
    },
  });
  cube?.setSelected(0);
} catch (error) {
  status.textContent = 'Explore the writing below. Every article is available in the list.';
  points.hidden = true;
  explorer.dataset.ready = 'fallback';
  console.error('The cube could not be displayed.', error);
}
window.addEventListener('pagehide', event => {
  if (!event.persisted) cube?.dispose();
});
