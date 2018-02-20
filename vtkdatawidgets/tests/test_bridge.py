#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Simula Research Laboratory.
# Distributed under the terms of the Modified BSD License.

import pytest

import vtk

from ..vtk_binding import VtkJupyterBridge


def test_empty_bridge_creation():
    bridge = VtkJupyterBridge()
    widget = bridge.widget
    assert widget.kind == ''
    assert widget.metadata == {}
    assert widget.containers == ()


@pytest.mark.filterwarnings('ignore:Cannot serialize (u)int64 data')
def test_simple_source_bridge():
    source = vtk.vtkSphereSource()
    bridge = VtkJupyterBridge()
    widget = bridge.widget
    bridge.SetInputConnection(source.GetOutputPort())
    # Check that nothing happens before Update()
    assert widget.kind == ''
    assert widget.metadata == {}
    assert widget.containers == ()

    bridge.Update()
    # Check that data populated after Update()
    assert widget.kind == 'vtkPolyData'
    assert widget.metadata == {}
    assert len(widget.containers) == 7
    assert list(sorted(c.kind for c in widget.containers)) == [
        'CellData', 'Lines', 'PointData', 'Points', 'Polys', 'Strips', 'Verts'
    ]
