#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Simula Research Laboratory.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import Widget, DOMWidget, widget_serialization, Color
from traitlets import (
    Unicode, Undefined, Dict, List, Enum, Tuple, Float, Instance, Int, Union,
)
from ipydatawidgets import DataUnion, data_union_serialization

from .traittypes import VarTuple

from ._version import EXTENSION_SPEC_VERSION

module_name = "jupyter-vtk-datawidgets"


class VtkWidget(Widget):
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(EXTENSION_SPEC_VERSION).tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(EXTENSION_SPEC_VERSION).tag(sync=True)



class DataArray(VtkWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('DataArrayModel').tag(sync=True)

    name = Unicode(None, allow_none=True).tag(sync=True)
    data = DataUnion().tag(sync=True, **data_union_serialization)

    def __init__(self, data, name=None, **kwargs):
        super(DataArray, self).__init__(data=data, name=name, **kwargs)


class DataContainer(VtkWidget):
    """A structure that holds a sequence of DataArrays.

    Represents things like Cells, Points, Verts, Lines, Strips, Polys,
    CellData, and PointData.
    """
    _model_name = Unicode('DataContainerModel').tag(sync=True)

    kind = Unicode().tag(sync=True)
    attributes = Dict().tag(sync=True)
    data_arrays = VarTuple(Instance(DataArray)).tag(sync=True, **widget_serialization)

    def __init__(self, kind, data_arrays=(), attributes=Undefined, **kwargs):
        if attributes is Undefined:
            attributes = {}
        super(DataContainer, self).__init__(
            kind=kind, data_arrays=data_arrays, attributes=attributes,
            **kwargs
        )

class DataSet(VtkWidget):
    containers = VarTuple(Instance(DataContainer)).tag(sync=True, **widget_serialization)

    def __init__(self, containers=(), **kwargs):
        super(DataSet, self).__init__(
            containers=containers,
            **kwargs
        )


class MutableDataSet(DataSet):
    """A DataSet that can represent any kind, and that can switch between them"""
    kind = Unicode().tag(sync=True)
    metadata = Dict().tag(sync=True)
    _model_name = Unicode('MutableDataSetModel').tag(sync=True)

    def __init__(self, containers=(), metadata=Undefined, **kwargs):
        if metadata is Undefined:
            metadata = {}
        super(MutableDataSet, self).__init__(
            containers=containers,
            metadata=metadata,
            **kwargs
        )


def ensure_data_array(data):
    if isinstance(data, DataArray):
        return data
    return DataArray(data=data)


class ImageData(DataSet):
    """TODO: Add docstring here
    """
    _model_name = Unicode('ImageDataModel').tag(sync=True)

    origin = Tuple(*((Float(),) * 3)).tag(sync=True)
    spacing = Tuple(*((Float(),) * 3)).tag(sync=True)

    def __init__(self, point_data, cell_data, origin=(0,0,0), spacing=(1,1,1)):
        containers = (
            DataContainer('PointData', [ensure_data_array(point_data)]),
            DataContainer('CellData', [ensure_data_array(cell_data)]),
        )
        super(ImageData, self).__init__(
            containers=containers,
            origin=origin,
            spacing=spacing,
        )


class RectilinearGrid(DataSet):
    """TODO: Add docstring here
    """
    _model_name = Unicode('RectilinearGridModel').tag(sync=True)

    whole_extent = Tuple(*((Float(),) * 6)).tag(sync=True)


    def __init__(self, point_data, cell_data, coordinates, whole_extent):
        containers = (
            DataContainer('PointData', [ensure_data_array(point_data)]),
            DataContainer('CellData', [ensure_data_array(cell_data)]),
            DataContainer('Coordinates', [ensure_data_array(coordinates)]),
        )
        super(RectilinearGrid, self).__init__(
            containers=containers,
            whole_extent=whole_extent,
        )


class StructuredGrid(DataSet):
    """TODO: Add docstring here
    """
    _model_name = Unicode('StructuredGridModel').tag(sync=True)

    whole_extent = Tuple(*((Float(),) * 6)).tag(sync=True)

    def __init__(self, point_data, cell_data, points, whole_extent):
        containers = (
            DataContainer('PointData', [ensure_data_array(point_data)]),
            DataContainer('CellData', [ensure_data_array(cell_data)]),
            DataContainer('Points', [ensure_data_array(points)]),
        )
        super(StructuredGrid, self).__init__(
            containers=containers,
            whole_extent=whole_extent,
        )


class PolyData(DataSet):
    """TODO: Add docstring here
    """
    _model_name = Unicode('PolyDataModel').tag(sync=True)

    def __init__(self, point_data, cell_data, points, verts=None, lines=None, strips=None, polys=None):
        containers = (
            DataContainer('PointData', [ensure_data_array(point_data)]),
            DataContainer('CellData', [ensure_data_array(cell_data)]),
            DataContainer('Points', [ensure_data_array(points)]),
        )
        if verts:
            containers += (DataContainer('Verts', [ensure_data_array(verts)]),)
        if lines:
            containers += (DataContainer('Lines', [ensure_data_array(lines)]),)
        if strips:
            containers += (DataContainer('Strips', [ensure_data_array(strips)]),)
        if polys:
            containers += (DataContainer('Polys', [ensure_data_array(polys)]),)
        super(PolyData, self).__init__(
            containers=containers,
        )



class UnstructuredGrid(DataSet):
    """TODO: Add docstring here
    """
    _model_name = Unicode('UnstructuredGridModel').tag(sync=True)

    def __init__(self, point_data, cell_data, points, cells):
        containers = (
            DataContainer('PointData', [ensure_data_array(point_data)]),
            DataContainer('CellData', [ensure_data_array(cell_data)]),
            DataContainer('Points', [ensure_data_array(points)]),
            DataContainer('Cells', [ensure_data_array(cells)]),
        )
        super(UnstructuredGrid, self).__init__(
            containers=containers,
        )


class VtkRenderer(DOMWidget):
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(EXTENSION_SPEC_VERSION).tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(EXTENSION_SPEC_VERSION).tag(sync=True)
    _model_name = Unicode('VtkRendererModel').tag(sync=True)
    _view_name = Unicode('VtkRendererView').tag(sync=True)

    dataset = Instance(DataSet).tag(sync=True, **widget_serialization)
    size = Tuple(Int(), Int(), default_value=(600, 400)).tag(sync=True)
    background = Union(
        [ Tuple(Float(0), Float(0), Float(0)), Color() ],
        default_value=(0, 0, 0)
    ).tag(sync=True)

    def __init__(self, dataset, background=(0, 0, 0), **kwargs):
        super(VtkRenderer, self).__init__(dataset=dataset, background=background, **kwargs)

__all__ = [
    'VtkWidget', 'DataArray', 'DataContainer', 'DataSet', 'MutableDataSet',
    'ImageData', 'RectilinearGrid', 'StructuredGrid', 'PolyData', 'UnstructuredGrid',
    'VtkRenderer',
]
