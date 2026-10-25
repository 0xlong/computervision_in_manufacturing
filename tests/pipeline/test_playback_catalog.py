"""Complete saved-picture packaging, with generated failure cases and real asset checks."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image
import pytest
from pipeline.playback_catalog import PlaybackCatalog, build_catalog, validate_catalog
from test_public_bundle import bundled, package, sample


def test_package_full_membership_without_changing_bundle_or_existing_assets(bundled):
    bundle, root, _, output = bundled
    before = {p: p.read_bytes() for p in output.rglob('*') if p.is_file()}
    catalog = build_catalog(root, output)
    assert len(catalog['images']) == bundle['runs'][0]['report']['expected'] == 6
    assert PlaybackCatalog.model_validate(catalog).root == catalog
    assert validate_catalog(catalog, bundle) == catalog
    assert all(p.read_bytes() == content for p, content in before.items())
    assert build_catalog(root, output) == catalog


@pytest.mark.parametrize('change', ['bundle', 'manifest', 'missing', 'duplicate', 'label', 'unsafe', 'mask', 'version', 'challenge'])
def test_reject_catalog_inconsistencies(bundled, change):
    bundle, root, _, output = bundled
    data = deepcopy(build_catalog(root, output))
    if change == 'bundle': data['bundle_id'] = 'another-bundle'
    if change == 'manifest': data['manifest_sha256'] = 'f' * 64
    if change == 'missing': data['images'].pop()
    if change == 'duplicate': data['images'].append(data['images'][0])
    if change == 'label': data['images'][0]['label'] = 'normal'
    if change == 'unsafe': data['images'][0]['display']['path'] = '../private.png'
    if change == 'mask': next(i for i in data['images'] if i['mask'])['mask']['dimensions']['width_px'] += 1
    if change == 'version': data['schema_version'] = 9
    if change == 'challenge': data['images'][0]['display']['sha256'] = 'f' * 64
    with pytest.raises(ValueError): validate_catalog(data, bundle)


def test_preflight_does_not_overwrite_changed_public_assets_or_catalog(bundled):
    _, root, _, output = bundled
    catalog = build_catalog(root, output)
    target = output / catalog['images'][0]['display']['path']
    target.write_bytes(b'changed')
    with pytest.raises(ValueError, match='Preserve changed'): build_catalog(root, output)
    assert target.read_bytes() == b'changed'


@pytest.mark.parametrize('change', ['manifest', 'source', 'catalog'])
def test_preflight_rejects_changed_inputs_before_copying_new_assets(bundled, change):
    _, root, _, output = bundled
    if change == 'manifest':
        target = root / 'evaluator/image-manifest.v2.json'
        target.write_text(target.read_text(encoding='utf-8') + '\n', encoding='utf-8')
    elif change == 'source':
        next((root / 'evaluator/images').glob('*.png')).write_bytes(b'changed source')
    else:
        (output / 'playback.v1.json').write_text('{}', encoding='utf-8')
    before = {p: p.read_bytes() for p in output.rglob('*') if p.is_file()}
    with pytest.raises(ValueError): build_catalog(root, output)
    assert {p: p.read_bytes() for p in output.rglob('*') if p.is_file()} == before


def test_all_genuine_public_playback_assets_match_hashes_dimensions_and_reference_labels():
    public = Path('web/public/evidence')
    bundle = json.loads((public / 'bundle.json').read_text(encoding='utf-8'))
    catalog = validate_catalog(json.loads((public / 'playback.v1.json').read_text(encoding='utf-8')), bundle)
    assert len(catalog['images']) == 115
    for item in catalog['images']:
        for kind in ('display', 'mask'):
            asset = item[kind]
            if asset is None: continue
            assert sha256((public / asset['path']).read_bytes()).hexdigest() == asset['sha256']
            with Image.open(public / asset['path']) as image:
                image.load()
                assert image.size == (asset['dimensions']['width_px'], asset['dimensions']['height_px'])
                if kind == 'mask': assert set(image.tobytes()) <= {0, 255}
