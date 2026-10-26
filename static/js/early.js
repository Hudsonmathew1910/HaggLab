/* Runs before first paint: marks JavaScript as on so reveal styles apply without a flash.
   Safety net: if site.js never loads, everything is shown after 2.5 seconds. */
document.documentElement.classList.add('js');
setTimeout(function () { if (!window.hagglabReady) document.documentElement.classList.add('reveal-all'); }, 2500);
