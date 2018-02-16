#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Vidar Tonaas Fauske.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import Widget, widget_serialization
from traitlets import Unicode, Undefined, Dict, List, Enum, Tuple, Float, Instance, Int
from ipydatawidgets import DataUnion, data_union_serialization

from .traittypes import VarTuple

module_name = "jupyter-vtk-datawidgets"
module_version = "0.1.0"


class VtkWidget(Widget):
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)



class DataArray(VtkWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('DataArray').tag(sync=True)

    name = Unicode(None, allow_none=True).tag(sync=True)
    data = DataUnion().tag(sync=True, **data_union_serialization)


class DataContainer(VtkWidget):
    """A structure that holds a sequence of DataArrays.

    Represents things like Cells, Points, Verts, Lines, Strips, Polys,
    CellData, and PointData.
    """
    _model_name =  Unicode('DataContainer').tag(sync=True)

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


class MutableDataSet(VtkWidget):
    """A DataSet that can represent any kind, and that can switch between them"""
    containers = VarTuple(Instance(DataContainer)).tag(sync=True, **widget_serialization)
    metadata = Dict().tag(sync=True)
    _model_name =  Unicode('MutableDataSet').tag(sync=True)

    def __init__(self, containers=(), metadata=Undefined, **kwargs):
        if metadata is Undefined:
            metadata = {}
        super(MutableDataSet, self).__init__(
            containers=containers,
            metadata=metadata,
            **kwargs
        )


class ImageData(DataSet):
    """TODO: Add docstring here
    """
    _model_name =  Unicode('ImageData').tag(sync=True)

    whole_extent = Tuple((Float(),) * 6)
    origin = Tuple((Float(),) * 3)
    spacing = Tuple((Float(),) * 3)

    def __init__(self, point_data, cell_data, whole_extent, origin=(0,0,0), spacing=(1,1,1)):
        containers = (
            DataContainer('PointData', point_data),
            DataContainer('CellData', cell_data),
        )
        super(ImageData, self).__init__(
            containers=containers,
            whole_extent=whole_extent,
            origin=origin,
            spacing=spacing,
        )


class RectilinearGrid(DataSet):
    """TODO: Add docstring here
    """
    _model_name =  Unicode('RectilinearGrid').tag(sync=True)

    whole_extent = Tuple((Float(),) * 6).tag(sync=True)


    def __init__(self, point_data, cell_data, coordinates, whole_extent):
        containers = (
            DataContainer('PointData', point_data),
            DataContainer('CellData', cell_data),
            DataContainer('Coordinates', coordinates),
        )
        super(RectilinearGrid, self).__init__(
            containers=containers,
            whole_extent=whole_extent,
        )


class StructuredGrid(DataSet):
    """TODO: Add docstring here
    """
    _model_name =  Unicode('StructuredGrid').tag(sync=True)

    whole_extent = Tuple((Float(),) * 6).tag(sync=True)

    def __init__(self, point_data, cell_data, points, whole_extent):
        containers = (
            DataContainer('PointData', point_data),
            DataContainer('CellData', cell_data),
            DataContainer('Points', points),
        )
        super(StructuredGrid, self).__init__(
            containers=containers,
            whole_extent=whole_extent,
        )


class PolyData(DataSet):
    """TODO: Add docstring here
    """
    _model_name =  Unicode('PolyData').tag(sync=True)

    def __init__(self, point_data, cell_data, points, verts=None, lines=None, strips=None, polys=None):
        containers = (
            DataContainer('PointData', point_data),
            DataContainer('CellData', cell_data),
            DataContainer('Points', points),
        )
        if verts:
            containers += (DataContainer('Verts', verts),)
        if lines:
            containers += (DataContainer('Lines', lines),)
        if strips:
            containers += (DataContainer('Strips', strips),)
        if polys:
            containers += (DataContainer('Polys', polys),)
        super(PolyData, self).__init__(
            containers=containers,
        )



class UnstructuredGrid(DataSet):
    """TODO: Add docstring here
    """
    _model_name =  Unicode('UnstructuredGrid').tag(sync=True)

    def __init__(self, point_data, cell_data, points, cells):
        containers = (
            DataContainer('PointData', point_data),
            DataContainer('CellData', cell_data),
            DataContainer('Points', points),
            DataContainer('Celles', cells),
        )
        super(UnstructuredGrid, self).__init__(
            containers=containers,
        )
