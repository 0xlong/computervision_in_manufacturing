"""Package every evaluated picture for local saved playback; never calls a provider."""

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil

from jsonschema import Draft202012Validator
from PIL import Image
from pydantic import JsonValue, RootModel, model_validator
from pipeline.contracts import read_manifest
from pipeline.public_bundle import REGISTRY, ROOT, validate_bundle

SCHEMA = json.loads((ROOT / 'schemas/playback-catalog.v1.schema.json').read_text(encoding='utf-8'))
VALIDATOR = Draft202012Validator(SCHEMA, registry=REGISTRY)


class PlaybackCatalog(RootModel[dict[str, JsonValue]]):
    @model_validator(mode='before')
    @classmethod
    def validate_data(cls, data):
        if next(VALIDATOR.iter_errors(data), None): raise ValueError('Invalid playback catalog schema')
        return deepcopy(data)


def validate_catalog(data, bundle):
    PlaybackCatalog.model_validate(data)
    if (data['bundle_id'], data['manifest_sha256']) != (bundle['bundle_id'], bundle['manifest_sha256']):
        raise ValueError('Playback catalog belongs to another evidence bundle')
    images = {i['image_id']: i for i in data['images']}
    if len(images) != len(data['images']): raise ValueError('Duplicate playback picture')
    for saved in bundle['runs']:
        rows = {i['image_id']: i['label'] for i in saved['report']['images']}
        if {k: i['label'] for k, i in images.items()} != rows:
            raise ValueError('Playback must cover exactly the complete evaluation references')
    for image in data['images']:
        ident = image['image_id']
        if image['display']['path'] != f'images/{ident}.png' or (image['mask'] is None) != (image['label'] == 'normal'):
            raise ValueError('Playback asset identity mismatch')
        if image['mask'] and (image['mask']['path'] != f'masks/{ident}.png' or image['mask']['dimensions'] != image['display']['dimensions']):
            raise ValueError('Playback mask alignment mismatch')
    if any(images[i['image_id']] != i for i in bundle['images']):
        raise ValueError('Existing challenge assets changed')
    return deepcopy(data)


def build_catalog(package: Path, public: Path):
    bundle = validate_bundle(json.loads((public / 'bundle.json').read_text(encoding='utf-8')))
    manifest_path = package / 'evaluator/image-manifest.v2.json'
    if sha256(manifest_path.read_bytes()).hexdigest() != bundle['manifest_sha256']:
        raise ValueError('Prepared manifest differs from saved evaluation')
    manifest = read_manifest(manifest_path).root
    images = [{k: i[k] for k in ('image_id', 'label', 'display', 'mask')}
              for i in manifest['images'] if i['split'] == 'evaluation']
    images.sort(key=lambda i: i['image_id'])
    data = validate_catalog({'schema_version': 1, 'bundle_id': bundle['bundle_id'],
                             'manifest_sha256': bundle['manifest_sha256'], 'images': images}, bundle)
    sources = []
    for image in images:
        for asset in (image['display'], image['mask']):
            if asset is None: continue
            source, target = package / 'evaluator' / asset['path'], public / asset['path']
            if source.is_symlink() or source.is_junction() or not source.resolve().is_relative_to((package / 'evaluator').resolve()):
                raise ValueError('Unsafe prepared asset')
            if sha256(source.read_bytes()).hexdigest() != asset['sha256']:
                raise ValueError('Prepared asset hash mismatch')
            with Image.open(source) as picture:
                picture.load()
                if picture.size != (asset['dimensions']['width_px'], asset['dimensions']['height_px']):
                    raise ValueError('Prepared asset dimensions mismatch')
            if target.is_symlink() or target.is_junction() or not target.resolve().is_relative_to(public.resolve()):
                raise ValueError('Unsafe public asset')
            if target.exists() and sha256(target.read_bytes()).hexdigest() != asset['sha256']:
                raise ValueError('Preserve changed public assets')
            sources.append((source, target))
    content = json.dumps(data, sort_keys=True, indent=2) + '\n'
    destination = public / 'playback.v1.json'
    if destination.exists() and destination.read_text(encoding='utf-8') != content:
        raise ValueError('Preserve existing playback catalog; package new evidence separately')
    for source, target in sources:
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    destination.write_text(content, encoding='utf-8')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--public', type=Path, required=True)
    args = parser.parse_args()
    catalog = build_catalog(args.package, args.public)
    print(f"PASS playback catalog: {len(catalog['images'])} pictures; saved bundle unchanged")


if __name__ == '__main__': main()
