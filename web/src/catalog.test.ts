import { expect, it } from 'vitest';
import genuine from '../public/evidence/bundle.json';
import catalog from '../public/evidence/playback.v1.json';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json';
import fixtureCatalog from '../../tests/fixtures/playback-catalog.fixture.json';
import { parseBundle, parsePlaybackCatalog } from './bundle';
import { differentAnswerIndices } from './comparison';

it('keeps the six-record test catalog distinct from the five-picture visitor challenge', () => {
  expect(parsePlaybackCatalog(fixtureCatalog, parseBundle(fixture)).images).toHaveLength(6);
});

it('matches all 115 references, preserves challenge assets and finds all 26 disagreements', () => {
  const bundle = parseBundle(genuine);
  const parsed = parsePlaybackCatalog(catalog, bundle);
  expect(parsed.images).toHaveLength(115);
  const different = differentAnswerIndices(bundle, parsed.images.map(i => i.image_id));
  expect(different).toHaveLength(26);
  expect(parsed.images[different.at(-1)!].image_id).toBe('img-000102');
  expect(parsed.images.filter(i => i.label === 'normal')).toHaveLength(22);
});

it('accepts equivalent JSON property ordering without changing picture identity', () => {
  const reordered = JSON.parse(JSON.stringify(catalog), (_, value) => value && typeof value === 'object' && !Array.isArray(value) ? Object.fromEntries(Object.entries(value).reverse()) : value);
  expect(parsePlaybackCatalog(reordered, parseBundle(genuine)).images).toHaveLength(115);
});

it.each(['version', 'bundle', 'manifest', 'missing', 'duplicate', 'label', 'path', 'mask', 'challenge', 'extra'])('rejects %s catalog corruption', change => {
  const bundle = parseBundle(genuine), data = structuredClone(catalog);
  if (change === 'version') data.schema_version = 99;
  if (change === 'bundle') data.bundle_id = 'other-bundle';
  if (change === 'manifest') data.manifest_sha256 = '0'.repeat(64);
  if (change === 'missing') data.images.pop();
  if (change === 'duplicate') data.images[1] = data.images[0];
  if (change === 'label') data.images[0].label = 'normal';
  if (change === 'path') data.images[0].display.path = '../outside.png';
  if (change === 'mask') data.images[0].mask!.dimensions.width_px++;
  if (change === 'challenge') data.images.find(i => i.image_id === bundle.challenge.image_ids[0])!.display.sha256 = '0'.repeat(64);
  if (change === 'extra') Object.assign(data, { unexpected: true });
  expect(() => parsePlaybackCatalog(data, bundle)).toThrow();
});
