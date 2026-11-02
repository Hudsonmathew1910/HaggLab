// Haggi, the HaggLab Assistant: the chat window (templates/components/assistant.html, API in apps/assistant).
// Answers come back as plain text with Markdown links; links are rebuilt here as safe <a> elements
// (site paths and https only), and nothing from the reply is ever inserted as HTML.
(function () {
  var root = document.querySelector('[data-haggi]');
  if (!root || !window.fetch) return;
  root.hidden = false;

  var api = root.getAttribute('data-api');
  var panel = root.querySelector('.haggi__panel');
  var openBtn = root.querySelector('[data-haggi-open]');
  var log = root.querySelector('[data-haggi-log]');
  var form = root.querySelector('[data-haggi-form]');
  var input = root.querySelector('[data-haggi-input]');
  var send = root.querySelector('[data-haggi-send]');
  var chips = root.querySelector('[data-haggi-chips]');
  var busy = false;
  var restored = false;
  var STORE = 'haggi-open';

  function csrf() {
    var field = form.querySelector('input[name=csrfmiddlewaretoken]');
    if (field) return field.value;
    var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  function safeUrl(url) {
    if (/^\/(?!\/)/.test(url) || /^#/.test(url)) return url;
    if (/^https:\/\//i.test(url)) return url;
    return null;
  }

  // Plain text -> paragraphs, "- " lists and [text](url) links, built with DOM nodes only
  function inline(target, text) {
    var re = /\[([^\]]{1,120})\]\(([^)\s]{1,300})\)/g, last = 0, m;
    while ((m = re.exec(text))) {
      if (m.index > last) target.appendChild(document.createTextNode(text.slice(last, m.index)));
      var url = safeUrl(m[2]);
      if (url) {
        var a = document.createElement('a');
        a.href = url;
        a.textContent = m[1];
        if (/^https:/i.test(url) && url.indexOf(location.host) === -1) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
        target.appendChild(a);
      } else {
        target.appendChild(document.createTextNode(m[1]));
      }
      last = re.lastIndex;
    }
    if (last < text.length) target.appendChild(document.createTextNode(text.slice(last)));
  }

  function render(container, text) {
    var list = null;
    text.split(/\n/).forEach(function (line) {
      var item = line.match(/^\s*[-*•]\s+(.*)$/);
      if (item) {
        if (!list) { list = document.createElement('ul'); container.appendChild(list); }
        var li = document.createElement('li');
        inline(li, item[1]);
        list.appendChild(li);
      } else if (line.trim()) {
        list = null;
        var p = document.createElement('p');
        inline(p, line.trim());
        container.appendChild(p);
      }
    });
  }

  function addMessage(role, text, links) {
    var box = document.createElement('div');
    box.className = 'haggi__msg haggi__msg--' + (role === 'user' ? 'user' : 'bot');
    if (role === 'user') {
      var p = document.createElement('p');
      p.textContent = text;
      box.appendChild(p);
    } else {
      render(box, text);
      if (links && links.length) {
        var row = document.createElement('div');
        row.className = 'haggi__links';
        links.forEach(function (l) {
          var url = safeUrl(l.url);
          if (!url) return;
          var a = document.createElement('a');
          a.href = url;
          a.textContent = l.title;
          if (/^https:/i.test(url)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
          row.appendChild(a);
        });
        if (row.children.length) box.appendChild(row);
      }
    }
    log.appendChild(box);
    log.scrollTop = log.scrollHeight;
    return box;
  }

  function addError(text) {
    var box = addMessage('bot', text);
    box.classList.add('haggi__msg--error');
  }

  function typing(on) {
    var t = log.querySelector('.haggi__typing');
    if (on && !t) {
      t = document.createElement('div');
      t.className = 'haggi__msg haggi__msg--bot haggi__typing';
      t.setAttribute('aria-label', 'Haggi is typing');
      t.innerHTML = '<span></span><span></span><span></span>';
      log.appendChild(t);
      log.scrollTop = log.scrollHeight;
    } else if (!on && t) {
      t.remove();
    }
  }

  function call(body) {
    return fetch(api, {
      method: body ? 'POST' : 'GET',
      credentials: 'same-origin',
      headers: body ? { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() } : {},
      body: body ? JSON.stringify(body) : undefined
    }).then(function (r) {
      return r.json().catch(function () { return { ok: false, error: 'Something went wrong. Please try again.' }; });
    });
  }

  function restore() {
    if (restored) return;
    restored = true;
    call().then(function (data) {
      if (!data.ok || !data.messages || !data.messages.length) return;
      if (chips) chips.hidden = true;
      data.messages.forEach(function (m) { addMessage(m.role, m.content, m.links); });
    }).catch(function () {});
  }

  function ask(text) {
    text = (text || '').trim();
    if (!text || busy) return;
    busy = true;
    send.disabled = true;
    if (chips) chips.hidden = true;
    addMessage('user', text);
    input.value = '';
    grow();
    typing(true);
    call({ message: text, page: location.pathname })
      .then(function (data) {
        typing(false);
        if (data.ok) addMessage('bot', data.text, data.links);
        else addError(data.error || 'Something went wrong. Please try again.');
      })
      .catch(function () {
        typing(false);
        addError('I could not reach the server. Please check your connection and try again.');
      })
      .then(function () {
        busy = false;
        send.disabled = false;
        input.focus();
      });
  }

  function open(focus) {
    panel.hidden = false;
    root.classList.add('is-open');
    openBtn.setAttribute('aria-expanded', 'true');
    restore();
    try { sessionStorage.setItem(STORE, '1'); } catch (e) {}
    if (focus !== false) setTimeout(function () { input.focus(); }, 50);
  }

  function close() {
    panel.hidden = true;
    root.classList.remove('is-open');
    openBtn.setAttribute('aria-expanded', 'false');
    try { sessionStorage.removeItem(STORE); } catch (e) {}
    openBtn.focus();
  }

  function grow() {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  }

  openBtn.addEventListener('click', function () { if (panel.hidden) open(); else close(); });
  root.querySelector('[data-haggi-close]').addEventListener('click', close);
  root.querySelector('[data-haggi-reset]').addEventListener('click', function () {
    if (busy) return;
    call({ reset: true }).catch(function () {});
    [].slice.call(log.querySelectorAll('.haggi__msg:not(.haggi__welcome)')).forEach(function (m) { m.remove(); });
    if (chips) chips.hidden = false;
    input.focus();
  });
  if (chips) chips.addEventListener('click', function (e) {
    if (e.target.classList.contains('haggi__chip')) ask(e.target.textContent);
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); ask(input.value); });
  input.addEventListener('input', grow);
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(input.value); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !panel.hidden) close();
  });

  // Keep the chat open while the visitor moves between pages
  try { if (sessionStorage.getItem(STORE) === '1') open(false); } catch (e) {}
})();
