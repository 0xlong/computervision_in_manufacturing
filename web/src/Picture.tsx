import { useEffect, useState } from 'react';
import type { Asset, ChallengeImage } from './types';

async function assetUrl(asset: Asset, signal: AbortSignal) {
  const response = await fetch(`/evidence/${asset.path}`, { signal });
  if (!response.ok) throw Error('Image file is unavailable.');
  const bytes = await response.arrayBuffer();
  if (bytes.byteLength > 2_000_000) throw Error('Image exceeds its supported size.');
  const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(n => n.toString(16).padStart(2, '0')).join('');
  if (hash !== asset.sha256) throw Error('Image does not match its saved evidence.');
  return URL.createObjectURL(new Blob([bytes], { type: 'image/png' }));
}

export function Picture({ image, revealed, onReady, onFailure, referenceOutline }: { image: ChallengeImage; revealed: boolean; onReady: (ready: boolean) => void; onFailure?: (failed: boolean) => void; referenceOutline?: boolean }) {
  const [url, setUrl] = useState(''), [maskUrl, setMaskUrl] = useState('');
  const [error, setError] = useState(''), [maskError, setMaskError] = useState('');
  const [zoom, setZoom] = useState(1), [localOutline, setLocalOutline] = useState(false), [retry, setRetry] = useState(0);
  // A supplied value lets the parent place the outline control beside the reference.
  const outline = referenceOutline ?? localOutline;
  useEffect(() => {
    const controller = new AbortController(); let objectUrl = '';
    setError(''); setUrl(''); onReady(false); onFailure?.(false);
    assetUrl(image.display, controller.signal).then(value => {
      if (controller.signal.aborted) { URL.revokeObjectURL(value); return; }
      objectUrl = value; setUrl(value);
    }).catch(() => { if (!controller.signal.aborted) { setError('This picture is missing or changed. Retry this picture.'); onFailure?.(true); } });
    return () => { controller.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [image, retry, onReady, onFailure]);
  useEffect(() => {
    if (!revealed || !outline || !image.mask) return;
    const controller = new AbortController(); let objectUrl = '';
    setMaskError('');
    assetUrl(image.mask, controller.signal).then(value => {
      if (controller.signal.aborted) { URL.revokeObjectURL(value); return; }
      objectUrl = value; setMaskUrl(value);
    }).catch(() => { if (!controller.signal.aborted) setMaskError('The reference outline is unavailable. The original picture remains visible.'); });
    return () => { controller.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl); setMaskUrl(''); };
  }, [image, outline, revealed, retry]);
  return <div className="picture-panel">
    <div className="image-toolbar" aria-label="Image controls">
      <span>Zoom</span>
      <button onClick={() => setZoom(z => Math.max(1, z - .25))} disabled={zoom <= 1} aria-label="Zoom out">−</button>
      <output aria-live="polite">{Math.round(zoom * 100)}%</output>
      <button onClick={() => setZoom(z => Math.min(2.5, z + .25))} disabled={zoom >= 2.5} aria-label="Zoom in">+</button>
      <button onClick={() => setZoom(1)} disabled={zoom === 1}>Fit image</button>
    </div>
    {error ? <div role="alert" className="image-error"><p>{error}</p><button onClick={() => setRetry(n => n + 1)}>Retry picture</button></div> :
      <div className="image-window" tabIndex={0} aria-label="Photograph; use arrow keys to scroll when zoomed">
        {url ? <div className="image-canvas" style={{ width: `${zoom * 100}%` }}>
          <img src={url} alt="Metal nut for your visual inspection" onLoad={e => {
            if (e.currentTarget.naturalWidth !== image.display.dimensions.width_px || e.currentTarget.naturalHeight !== image.display.dimensions.height_px) {
              setError('Image dimensions disagree with the evidence. Retry this picture.'); onReady(false); onFailure?.(true);
            } else onReady(true);
          }} onError={() => { setError('The picture could not be decoded. Retry this picture.'); onReady(false); onFailure?.(true); }} />
          {revealed && outline && maskUrl && <div className="reference-mask" role="img" style={{ maskImage: `url("${maskUrl}")`, WebkitMaskImage: `url("${maskUrl}")` }} aria-label="Dataset reference region" />}
        </div> : <p role="status">Loading photograph…</p>}
      </div>}
    {revealed && referenceOutline === undefined && <div className="outline-controls">{image.mask ? <>
      <button aria-pressed={outline} onClick={() => setLocalOutline(v => !v)}>{outline ? 'Hide reference outline' : 'Show reference outline'}</button>
      <p>Dataset outline, not AI output.</p>
    </> : null}</div>}
    {maskError && <p role="alert">{maskError} <button onClick={() => setRetry(n => n + 1)}>Retry outline</button></p>}
  </div>;
}
