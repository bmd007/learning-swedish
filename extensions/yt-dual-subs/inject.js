(() => {
  const isTrack = url => typeof url === 'string' && url.includes('/api/timedtext');
  const send = (url, body) => {
    if (body) window.postMessage({ source: 'yt-dual-subs', url, body }, '*');
  };

  const origFetch = window.fetch;
  window.fetch = async function (...args) {
    const res = await origFetch.apply(this, args);
    try {
      const url = args[0] instanceof Request ? args[0].url : String(args[0]);
      if (isTrack(url)) res.clone().text().then(body => send(url, body), () => {});
    } catch (e) {}
    return res;
  };

  const origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url, ...rest) {
    if (isTrack(String(url))) {
      this.addEventListener('load', () => {
        try {
          const rt = this.responseType;
          const body = rt === 'json' ? JSON.stringify(this.response)
            : rt === '' || rt === 'text' ? this.responseText
            : null;
          send(this.responseURL || String(url), body);
        } catch (e) {}
      });
    }
    return origOpen.call(this, method, url, ...rest);
  };
})();
