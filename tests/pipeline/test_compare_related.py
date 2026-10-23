"""Known synthetic controls, never physical-object identity labels."""

import random

from PIL import Image, ImageChops, ImageEnhance
import pytest

from pipeline.compare_related import compare, correlation, overlap


def texture(seed):
    rng = random.Random(seed)
    return Image.frombytes("L", (128,128), bytes(rng.randrange(256) for _ in range(128*128))).convert("RGB")


def test_registration_finds_known_shift_and_same_photo_detail():
    a = texture(42)
    result = compare(a, ImageChops.offset(a, 2,-1))
    assert result["translation_source_px"] == [-2,1]
    assert result["rotation_deg"] == 0
    assert result["native_edge_correlation"] == pytest.approx(1)
    assert not result["search_boundary_hit"]


def test_unrelated_control_is_far_below_identical_and_relighting_is_not_identity():
    a = texture(42)
    same = compare(a,a)
    different = compare(a,texture(99))
    relit = compare(a,ImageEnhance.Brightness(a).enhance(0.8))
    assert same["native_edge_correlation"] > 0.999
    assert different["native_edge_correlation"] < 0.3
    assert relit["native_gray_correlation"] > 0.99


def test_overlap_does_not_wrap_and_constant_pixels_have_undefined_correlation():
    a,b = overlap(Image.new("L", (10,8), 10),Image.new("L",(10,8),20),2,-1)
    assert a.size == b.size == (8,7)
    assert correlation(a,b) is None
