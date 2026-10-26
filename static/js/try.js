/**
 * HaggLab Try it pages.
 * Sends the form to /api/try/<slug>/ as JSON and shows the reply.
 * Reply text is always inserted with textContent, never as HTML.
 * Note: form attributes are read with getAttribute(), because a field named "dataset" would
 * hide form.dataset (form fields become properties of the form element).
 */
(() => {
  const form = document.querySelector('.try-form');
  if (!form) return;

  const out = document.querySelector('.try-out');
  const errorBox = form.querySelector('.try-error');
  const log = form.querySelector('[data-log]');
  const kind = form.getAttribute('data-kind');
  const submitBtn = form.querySelector('button[type="submit"]');
  const csrf = form.querySelector('input[name="csrfmiddlewaretoken"]').value;
  const status = form.querySelector('.chat__status');
  const clearBtn = form.querySelector('[data-clear]');
  const messageField = form.querySelector('[name="message"]');
  const projectInitial = (form.getAttribute('data-project') || '?').charAt(0).toUpperCase();

  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  };

  const showError = (message) => {
    errorBox.textContent = message;
    errorBox.hidden = !message;
  };

  const setBusy = (busy) => {
    form.classList.toggle('is-busy', busy);
    submitBtn.disabled = busy;
    submitBtn.setAttribute('aria-busy', String(busy));
  };

  /* "Thinking" indicator: animated dots, elapsed seconds and reassuring hints while the AI works */
  const HINTS = [
    [0, 'Thinking'],
    [6, 'Reading the data'],
    [14, 'Still working, almost there'],
    [30, 'This one is taking longer than usual. AI answers can take up to a minute.'],
  ];
  const startThinking = (container, isChat) => {
    const box = el('div', isChat ? 'chat-row chat-row--ai' : 'try-thinking-wrap');
    if (isChat) box.appendChild(el('span', 'chat-avatar', projectInitial));
    const bubble = el('div', 'try-thinking');
    bubble.setAttribute('role', 'status');
    const dots = el('span', 'try-dots');
    dots.setAttribute('aria-hidden', 'true');
    dots.append(el('i'), el('i'), el('i'));
    const label = el('span', 'try-thinking__text', 'Thinking');
    const timer = el('span', 'try-thinking__time', '');
    bubble.append(dots, label, timer);
    box.appendChild(bubble);
    container.appendChild(box);
    const started = Date.now();
    const tick = setInterval(() => {
      const secs = Math.floor((Date.now() - started) / 1000);
      timer.textContent = secs >= 3 ? `${secs}s` : '';
      const hint = HINTS.filter(([after]) => secs >= after).pop();
      if (label.textContent !== hint[1]) label.textContent = hint[1];
    }, 500);
    if (status) status.textContent = 'Thinking…';
    return () => {
      clearInterval(tick);
      box.remove();
      if (status) status.textContent = 'Ready';
    };
  };

  /* Build the reply view from whichever keys the API returned */
  const renderReply = (reply) => {
    const box = el('div', 'try-reply');
    if (Array.isArray(reply.labels) && reply.labels.length) {
      const labels = el('div', 'try-labels');
      reply.labels.forEach((l) => labels.appendChild(el('span', 'ui-pill', l)));
      box.appendChild(labels);
    }
    if (reply.text) {
      String(reply.text).split(/\n{2,}/).forEach((para) => box.appendChild(el('p', 'try-text', para)));
    }
    if (reply.source) box.appendChild(el('span', 'ui-src', reply.source));
    if (Array.isArray(reply.items) && reply.items.length) {
      const list = el('ul', 'try-items');
      reply.items.forEach((item) => {
        const li = el('li', 'try-item');
        if (kind === 'booking' && item.slot) {
          const btn = el('button', 'try-slot', item.title || item.slot);
          btn.type = 'button';
          btn.dataset.slot = item.slot;
          if (item.meta) btn.appendChild(el('small', null, item.meta));
          li.appendChild(btn);
        } else {
          li.appendChild(el('strong', null, item.title));
          if (item.meta) li.appendChild(el('span', null, item.meta));
        }
        list.appendChild(li);
      });
      box.appendChild(list);
    }
    if (reply.table && Array.isArray(reply.table.columns) && Array.isArray(reply.table.rows)) {
      const wrap = el('div', 'try-table');
      const table = el('table');
      const head = el('tr');
      reply.table.columns.forEach((c) => head.appendChild(el('th', null, c)));
      table.appendChild(el('thead')).appendChild(head);
      const body = el('tbody');
      reply.table.rows.slice(0, 200).forEach((row) => {
        const tr = el('tr');
        (Array.isArray(row) ? row : []).forEach((cell) => tr.appendChild(el('td', null, cell)));
        body.appendChild(tr);
      });
      table.appendChild(body);
      wrap.appendChild(table);
      box.appendChild(wrap);
    }
    if (reply.code) {
      const details = el('details', 'try-code');
      details.appendChild(el('summary', null, 'Show the code that calculated this'));
      details.appendChild(el('pre', null, reply.code));
      box.appendChild(details);
    }
    if (Array.isArray(reply.steps) && reply.steps.length) {
      const steps = el('ol', 'try-steps');
      reply.steps.forEach((s) => {
        const li = el('li', null, s.text);
        if (s.needs_approval) li.appendChild(el('span', 'ui-pill ui-pill--warn', 'Asks you first'));
        steps.appendChild(li);
      });
      box.appendChild(steps);
    }
    return box;
  };

  const collect = () => {
    const data = {};
    new FormData(form).forEach((value, key) => {
      if (key !== 'csrfmiddlewaretoken') data[key] = typeof value === 'string' ? value.trim() : value;
    });
    return data;
  };

  const send = async (data) => {
    setBusy(true);
    showError('');
    if (window.hagglabTrack) window.hagglabTrack('demo_start', form.getAttribute('data-project'));
    try {
      const res = await fetch(form.getAttribute('data-try-url'), {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify(data),
      });
      let reply = {};
      try { reply = await res.json(); } catch (e) { reply = {}; }
      if (!res.ok || !reply.ok) {
        showError(reply.error || `Something went wrong (error ${res.status}). Please try again.`);
        return null;
      }
      return reply;
    } catch (e) {
      showError('Could not reach the server. Check your connection and try again.');
      return null;
    } finally {
      setBusy(false);
    }
  };

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = collect();

    if (kind === 'chat') {
      if (!data.message) { showError('Please type a message first.'); messageField.focus(); return; }
      const mine = el('div', 'chat-row chat-row--me');
      mine.appendChild(el('div', 'ui-msg ui-msg--me', data.message));
      log.appendChild(mine);
      messageField.value = '';
      autogrow();
      if (clearBtn) clearBtn.hidden = false;
      const stop = startThinking(log, true);
      scrollLog();
      const reply = await send(data);
      stop();
      const row = el('div', 'chat-row chat-row--ai');
      row.appendChild(el('span', 'chat-avatar', projectInitial));
      const bubble = el('div', 'ui-msg ui-msg--ai');
      if (reply) {
        bubble.appendChild(renderReply(reply));
      } else {
        bubble.classList.add('ui-msg--error');
        bubble.appendChild(el('p', 'try-text', errorBox.textContent || 'Something went wrong. Please try again.'));
        showError('');
      }
      row.appendChild(bubble);
      log.appendChild(row);
      scrollLog();
      messageField.focus();
      return;
    }

    if (kind === 'booking' && data.action === 'book' && !data.name) {
      showError('Please add your name to book this slot.');
      return;
    }

    out.replaceChildren();
    out.hidden = false;
    const stop = startThinking(out, false);
    out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    const reply = await send(data);
    stop();
    if (!reply) { out.hidden = true; return; }
    if (kind === 'booking' && data.action === 'book') {
      form.querySelector('[data-action]').value = 'slots';
      form.querySelector('[data-slot]').value = '';
      submitBtn.firstChild.textContent = 'Show free slots ';
    }
    out.replaceChildren(renderReply(reply));
    out.hidden = false;
    out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });

  /* Chat helpers */
  function scrollLog() {
    if (log) log.scrollTo({ top: log.scrollHeight, behavior: 'smooth' });
  }
  function autogrow() {
    if (!messageField || !messageField.hasAttribute('data-autogrow')) return;
    messageField.style.height = 'auto';
    messageField.style.height = Math.min(messageField.scrollHeight, 160) + 'px';
  }
  if (messageField && messageField.hasAttribute('data-autogrow')) {
    messageField.addEventListener('input', autogrow);
    messageField.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
        e.preventDefault();
        if (!submitBtn.disabled) form.requestSubmit();
      }
    });
  }
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      log.querySelectorAll('.chat-row:not(.chat-welcome)').forEach((row) => row.remove());
      clearBtn.hidden = true;
      messageField.focus();
    });
  }

  /* Example chips: fill the question; in chat they send straight away */
  form.querySelectorAll('[data-example]').forEach((chip) => {
    chip.addEventListener('click', () => {
      if (!messageField || submitBtn.disabled) return;
      messageField.value = chip.getAttribute('data-example');
      autogrow();
      if (kind === 'chat') form.requestSubmit();
      else messageField.focus();
    });
  });

  /* Booking: picking a slot switches the form from "show slots" to "book" */
  if (kind === 'booking') {
    const action = form.querySelector('[data-action]');
    const slotField = form.querySelector('[data-slot]');
    const dateField = form.querySelector('[name="date"]');
    if (dateField && !dateField.value) dateField.value = new Date().toISOString().slice(0, 10);
    out.addEventListener('click', (e) => {
      const btn = e.target.closest('.try-slot');
      if (!btn) return;
      out.querySelectorAll('.try-slot').forEach((b) => b.classList.toggle('is-picked', b === btn));
      slotField.value = btn.dataset.slot;
      action.value = 'book';
      submitBtn.firstChild.textContent = 'Book ' + btn.dataset.slot + ' ';
      form.querySelector('[name="name"]').focus();
    });
    const resetToSlots = () => {
      action.value = 'slots';
      slotField.value = '';
      submitBtn.firstChild.textContent = 'Show free slots ';
    };
    form.querySelector('[name="resource"]').addEventListener('change', resetToSlots);
    dateField.addEventListener('change', () => {
      action.value = 'slots';
      slotField.value = '';
      submitBtn.firstChild.textContent = 'Show free slots ';
    });
  }
})();
