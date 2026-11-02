// /start: show only what belongs to the chosen service: its packages (required), extras, a running total
// and its order questions. "When do you need it?" and "Budget" are for a custom project ("Not sure yet") only.
// Without JavaScript everything is listed, and the server checks and drops whatever does not match the service.
(function () {
  var service = document.getElementById('id_service');
  var select = document.getElementById('id_package_choice');
  if (!service || !select) return;
  var groups = [].slice.call(select.querySelectorAll('optgroup'));
  var pkgField = document.querySelector('[data-pkg-field]');
  var extrasField = document.querySelector('[data-extras-field]');
  var extraGroups = [].slice.call(extrasField.querySelectorAll('[data-service]'));
  var asksField = document.querySelector('[data-asks-field]');
  var askGroups = asksField ? [].slice.call(asksField.querySelectorAll('[data-service]')) : [];
  var details = [].slice.call(document.querySelectorAll('[data-pkg]'));
  var customOnly = [].slice.call(document.querySelectorAll('[data-custom-only]'));
  var empty = document.querySelector('[data-pkg-empty]');
  var total = document.querySelector('[data-pkg-total]');
  var rate = parseFloat(total ? total.getAttribute('data-rate') : '') || 0;

  function showTotal() {
    var picked = select.options[select.selectedIndex];
    var on = !!select.value && !pkgField.hidden;
    if (!total) return;
    total.hidden = !on;
    if (!on) return;
    var sum = parseFloat(picked.getAttribute('data-price')) || 0;
    [].forEach.call(extrasField.querySelectorAll('input:checked'), function (i) {
      sum += parseFloat(i.getAttribute('data-price')) || 0;
    });
    var text = 'Total: $' + sum;
    if (rate) text += ' \u2248 \u20b9' + (Math.floor(sum * rate / 100 + 0.5) * 100).toLocaleString('en-US');
    total.textContent = text + '. Delivery time comes from the package and any faster-delivery extra.';
  }

  function showDetails() {
    details.forEach(function (d) { d.hidden = d.getAttribute('data-pkg') !== select.value; });
    showTotal();
  }

  function showGroups(list, code) {
    var any = false;
    list.forEach(function (g) {
      var on = g.getAttribute('data-service') === code;
      g.hidden = !on;
      if (on && g.querySelector('input, select, textarea')) any = true;
    });
    return any;
  }

  function update() {
    var code = service.value;
    var keep = null;
    groups.forEach(function (g) {
      if (g.getAttribute('data-service') === code) { keep = g; if (!g.parentNode) select.appendChild(g); }
      else if (g.parentNode) { g.parentNode.removeChild(g); }
    });
    if (!keep || select.selectedIndex < 0) select.value = '';
    pkgField.hidden = !keep;
    if (empty) {
      empty.hidden = !!keep;
      empty.textContent = empty.getAttribute(code ? 'data-custom' : 'data-none');
    }
    // When and budget: only for a custom project, or a service with no packages
    customOnly.forEach(function (f) { f.hidden = !(code && !keep); });

    extrasField.hidden = !showGroups(extraGroups, code);
    extraGroups.forEach(function (g) {
      if (g.hidden) [].forEach.call(g.querySelectorAll('input'), function (i) { i.checked = false; });
    });
    if (asksField) asksField.hidden = !showGroups(askGroups, code);
    showDetails();
  }

  service.addEventListener('change', update);
  select.addEventListener('change', showDetails);
  extrasField.addEventListener('change', showTotal);
  update();
})();
