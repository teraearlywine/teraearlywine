// All example amounts are integer cents for the same reporting period.
const sales = [{ name: 'Sale A', cents: 40000 }, { name: 'Sale B', cents: 20000 }];
const postedRefund = 4000;
const ledger = { sales: 60000, refund: -4000 };
const dollars = new Intl.NumberFormat('en-US', {
  style: 'currency', currency: 'USD', maximumFractionDigits: 0,
});
const money = cents => dollars.format(cents / 100);

const layerDetails = {
  source: {
    title: 'Source records',
    hint: 'Read the two completed sales and any posted refund.',
  },
  rule: {
    title: 'Business rule',
    hint: 'Subtract posted refunds from completed sales.',
  },
  check: {
    title: 'Ledger check',
    hint: 'Compare reported net sales with the posted ledger balance.',
  },
};

const figure = document.querySelector('.cs-figure');
const layerInputs = document.querySelectorAll('.cs-layer-control input');
const layerOrder = Object.keys(layerDetails);
const refund = document.getElementById('sales-refund');
const nextButton = document.getElementById('next-sales-layer');

function renderExample(layer = figure.dataset.layer) {
  for (const input of layerInputs) input.checked = input.value === layer;
  const gross = sales.reduce((sum, sale) => sum + sale.cents, 0);
  const deductions = refund.checked ? postedRefund : 0;
  const net = gross - deductions;
  const balance = ledger.sales + (refund.checked ? ledger.refund : 0);
  const records = sales.map(sale => sale.name + ' +' + money(sale.cents));
  if (refund.checked) records.push('Refund −' + money(deductions));
  const readout = {
    source: [records.join(' / '), 'Each amount comes from a separate posted record in this sample.'],
    rule: [
      money(gross) + ' − ' + money(deductions) + ' = ' + money(net),
      refund.checked ? 'Both sales are complete. The posted refund reduces net sales by $40.' : 'Both sales are complete. There are no posted refunds in this scenario.',
    ],
    check: [
      money(net) + ' reported − ' + money(balance) + ' ledger = ' + money(net - balance),
      'The sample ledger agrees with the reported number for this period.',
    ],
  };
  figure.dataset.layer = layer;
  figure.querySelector('.cs-pin-label').textContent = layerDetails[layer].title;
  figure.querySelector('.cs-hint').textContent = layerDetails[layer].hint;
  document.getElementById('sales-layer-title').textContent = layerDetails[layer].title;
  document.getElementById('sales-total').textContent = money(net);
  document.getElementById('sales-formula').textContent = readout[layer][0];
  document.getElementById('sales-explanation').textContent = readout[layer][1];
}

for (const input of layerInputs) {
  input.addEventListener('change', () => renderExample(input.value));
}
refund.addEventListener('change', () => renderExample());
nextButton.addEventListener('click', () => {
  const current = layerOrder.indexOf(figure.dataset.layer);
  renderExample(layerOrder[(current + 1) % layerOrder.length]);
});
renderExample();
for (const control of document.querySelectorAll('[data-demo-control]')) {
  control.hidden = false;
}
