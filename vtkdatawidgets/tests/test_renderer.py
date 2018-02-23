#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Simula Research Laboratory.
# Distributed under the terms of the Modified BSD License.

import pytest

from .. import VtkRenderer, DataSet


def test_empty_renderer_creation_fails():
    with pytest.raises(TypeError):
        renderer = VtkRenderer()


def test_empty_dataset_renderer_creation():
    dataset = DataSet()
    renderer = VtkRenderer(dataset)
