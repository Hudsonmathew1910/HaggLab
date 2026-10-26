// HaggLab First-Party Analytics Client
(function() {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function trackEvent(name, target) {
    var payload = {
      event: name,
      path: window.location.pathname,
      target: target || ''
    };
    var csrftoken = getCookie('csrftoken');

    if (navigator.sendBeacon) {
      var blob = new Blob([JSON.stringify(payload)], {type: 'application/json'});
      navigator.sendBeacon('/api/analytics/event/', blob);
    } else {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/api/analytics/event/', true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      if (csrftoken) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
      }
      xhr.send(JSON.stringify(payload));
    }
  }

  document.addEventListener('DOMContentLoaded', function() {
    // 1. Project view
    if (window.location.pathname.indexOf('/projects/') === 0 && window.location.pathname.length > 10) {
      trackEvent('project_view', window.location.pathname);
    }

    // 2. Fiverr clicks
    document.querySelectorAll('a[href*="fiverr.com"]').forEach(function(el) {
      el.addEventListener('click', function() {
        trackEvent('fiverr_click', el.getAttribute('href'));
      });
    });

    // 3. CTA clicks
    document.querySelectorAll('.btn').forEach(function(el) {
      el.addEventListener('click', function() {
        trackEvent('cta_click', el.innerText.trim());
      });
    });

    // 4. Form start
    var projectForm = document.querySelector('form[action="/start/"]');
    if (projectForm) {
      var started = false;
      projectForm.querySelectorAll('input, textarea, select').forEach(function(field) {
        field.addEventListener('focus', function() {
          if (!started) {
            started = true;
            trackEvent('form_start', 'start_project');
          }
        }, {once: true});
      });

      projectForm.addEventListener('submit', function() {
        trackEvent('form_submit', 'start_project');
      });
    }
  });

  window.hagglabTrack = trackEvent;
})();
