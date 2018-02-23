#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Simula Research Laboratory.
# Distributed under the terms of the Modified BSD License.

import pytest
import numpy as np

from ..widget import (
    DataContainer, DataArray, MutableDataSet,
    ImageData, RectilinearGrid, StructuredGrid, PolyData, UnstructuredGrid
)


def test_empty_dataarray_creation_fails():
    with pytest.raises(TypeError):
        w = DataArray()


def test_dataarray_creation():
    d = np.ones((5, 4))
    w = DataArray(data=d)
    assert w.name == None
    assert w.data is d


def test_empty_datacontainer_creation_fails():
    with pytest.raises(TypeError):
        w = DataContainer()

def test_minimal_datacontainer_creation():
    w = DataContainer('testKind')
    assert w.kind == 'testKind'
    assert w.data_arrays == ()

def test_full_datacontainer_creation():
    d = np.ones((5, 4))
    da = DataArray(data=d)
    dc = DataContainer('testKind', data_arrays=[da], attributes={
        'foo': 'bar'
    })
    assert dc.kind == 'testKind'
    assert dc.data_arrays == (da,)
    assert dc.attributes == {'foo': 'bar'}


def test_empty_mutable_creation():
    w = MutableDataSet()

def test_mutable_creation():
    d = np.ones((5, 4))
    da = DataArray(data=d)
    dc = DataContainer('testKind', data_arrays=[da], attributes={
        'foo': 'bar'
    })
    ds = MutableDataSet(containers=[dc], metadata={'meaning': 42})
    assert ds.containers == (dc,)
    assert ds.metadata == {'meaning': 42}


def test_empty_image_creation_fails():
    with pytest.raises(TypeError):
        w = ImageData()

def test_minimal_image_creation():
    point_data = np.ones((4, 2, 2))
    cell_data = np.ones((3, 1, 1))
    ds = ImageData(point_data, cell_data)
    assert [dc.kind for dc in ds.containers] == ['PointData', 'CellData']
    assert ds.origin == (0, 0, 0)
    assert ds.spacing == (1, 1, 1)


def test_empty_rectilinear_creation_fails():
    with pytest.raises(TypeError):
        w = RectilinearGrid()

def test_minimal_rectilinear_creation():
    point_data = np.ones((4, 2, 2))
    cell_data = np.ones((3, 1, 1))
    coordinates = np.ones((3, 3))
    ds = RectilinearGrid(point_data, cell_data, coordinates, (0, 0, 0, 100, 100, 100))
    assert [dc.kind for dc in ds.containers] == ['PointData', 'CellData', 'Coordinates']
    assert ds.whole_extent == (0, 0, 0, 100, 100, 100)


def test_empty_structured_creation_fails():
    with pytest.raises(TypeError):
        w = StructuredGrid()

def test_minimal_structured__creation():
    point_data = np.ones((4, 2, 2))
    cell_data = np.ones((3, 1, 1))
    points = np.ones((3, 3))
    ds = StructuredGrid(point_data, cell_data, points, (0, 0, 0, 100, 100, 100))
    assert [dc.kind for dc in ds.containers] == ['PointData', 'CellData', 'Points']
    assert ds.whole_extent == (0, 0, 0, 100, 100, 100)



def test_empty_poly_creation_fails():
    with pytest.raises(TypeError):
        w = PolyData()

def test_minimal_poly_creation():
    point_data = np.ones((4, 2, 2))
    cell_data = np.ones((3, 1, 1))
    points = np.ones((3, 3))
    ds = PolyData(point_data, cell_data, points)
    assert [dc.kind for dc in ds.containers] == ['PointData', 'CellData', 'Points']



def test_empty_unstructured_creation_fails():
    with pytest.raises(TypeError):
        w = UnstructuredGrid()

def test_minimal_unstructured_creation():
    point_data = np.ones((4, 2, 2))
    cell_data = np.ones((3, 1, 1))
    points = np.ones((3, 3))
    cells = np.ones((3, 3))
    ds = UnstructuredGrid(point_data, cell_data, points, cells)
    assert [dc.kind for dc in ds.containers] == ['PointData', 'CellData', 'Points', 'Cells']
