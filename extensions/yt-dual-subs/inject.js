(() => {
  const isTrack = url => typeof url === 'string' && url.includes('/api/timedtext');
  const send = (url, body) => {
    if (body) window.postMessage({ source: 'yt-dual-subs', url, body }, '*');
  };
  const origFetch = window.fetch;
  const fetchedFor = new Set();
  document.addEventListener('yt-navigate-finish', () => fetchedFor.clear());

  function swedishTracks(videoId) {
    try {
      const pr = document.querySelector('#movie_player')?.getPlayerResponse?.();
      if (pr?.videoDetails?.videoId !== videoId) return null;
      return (pr.captions?.playerCaptionsTracklistRenderer?.captionTracks ?? [])
        .filter(t => t.languageCode?.toLowerCase().startsWith('sv'))
        .map(t => new URL(t.baseUrl, location.origin).searchParams);
    } catch (e) {
      return null;
    }
  }

  // YouTube only serves a track when the request carries the player's bot token (pot), so the
  // other Swedish tracks are fetched by reusing the URL of a request the player already made.
  function fetchSwedishTracks(captured) {
    const base = new URL(captured, location.origin);
    const v = base.searchParams.get('v');
    if (!v || fetchedFor.has(v)) return;
    fetchedFor.add(v);
    const tracks = swedishTracks(v) ?? [
      new URLSearchParams({ lang: 'sv' }),
      new URLSearchParams({ lang: 'sv', kind: 'asr' }),
    ];
    for (const t of tracks) {
      const u = new URL(base);
      for (const k of ['lang', 'kind', 'name', 'tlang']) u.searchParams.delete(k);
      for (const k of ['lang', 'kind', 'name']) if (t.get(k)) u.searchParams.set(k, t.get(k));
      u.searchParams.set('fmt', 'json3');
      origFetch(u.href, { credentials: 'include' })
        .then(r => r.text())
        .then(body => send(u.href, body), () => {});
    }
  }

  const onCaptured = (url, body) => {
    send(url, body);
    fetchSwedishTracks(url);
  };

  window.fetch = async function (...args) {
    const res = await origFetch.apply(this, args);
    try {
      const url = args[0] instanceof Request ? args[0].url : String(args[0]);
      if (isTrack(url)) res.clone().text().then(body => onCaptured(url, body), () => {});
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
          onCaptured(this.responseURL || String(url), body);
        } catch (e) {}
      });
    }
    return origOpen.call(this, method, url, ...rest);
  };
})();
