#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Vidar Tonaas Fauske.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import Widget, widget_serialization
from traitlets import Unicode, Undefined, Dict, List, Enum, Tuple, Float, Instance
from ipydatawidgets import DataUnion, data_union_serialization


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
    """TODO: Add docstring here
    """
    _model_name =  Unicode('DataContainer').tag(sync=True)

    kind = Unicode().tag(sync=True)
    attributes = Dict().tag(sync=True)
    data_arrays = List(Instance(DataArray)).tag(sync=True, **widget_serialization)


class Piece(VtkWidget):
    """TODO: Add docstring here
    """
    _model_name =  Unicode('Piece').tag(sync=True)

    attributes = Dict().tag(sync=True)
    data = List(Instance(DataContainer)).tag(sync=True, **widget_serialization)


class DataSet(VtkWidget):
    """TODO: Add docstring here
    """
    pieces = List(Instance(Piece)).tag(sync=True, **widget_serialization)


def load_data_set(filename):
    if not isinstance(filename, str):
        raise TypeError("Filename must be string.")
    from .vtkio import read_vtk_xml
    return read_vtk_xml(filename)



class ImageData(DataSet):
    """TODO: Add docstring here
    """
    _model_name =  Unicode('ImageData').tag(sync=True)

    whole_extent = Tuple((Float(),) * 6).tag(sync=True)
    origin = Tuple((Float(),) * 3).tag(sync=True)
    spacing = Tuple((Float(),) * 3).tag(sync=True)


    def __init__(self, pieces, whole_extent, origin, spacing):
        super(ImageData, self).__init__(
            pieces=pieces, whole_extent=whole_extent,
            origin=origin, spacing=spacing
        )


class UnstructuredGrid(DataSet):
    """TODO: Add docstring here
    """
    _model_name =  Unicode('UnstructuredGrid').tag(sync=True)


    def __init__(self, pieces):
        super(UnstructuredGrid, self).__init__(
            pieces=pieces
        )
