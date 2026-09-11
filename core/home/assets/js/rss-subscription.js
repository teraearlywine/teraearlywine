const address = document.getElementById('rssAddress');
const copyButton = document.getElementById('rssCopy');
const status = document.getElementById('rss-copy-status');

if (address && copyButton && status) {
  copyButton.hidden = false;
  copyButton.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(address.value);
      status.textContent = 'Feed address copied. Paste it into your reader to finish subscribing.';
    } catch {
      address.focus();
      address.select();
      address.setSelectionRange(0, address.value.length);
      status.textContent = 'Select Copy from your device’s menu, or press Ctrl+C (⌘C on Mac). Then paste the address into your reader.';
    }
  });
}
