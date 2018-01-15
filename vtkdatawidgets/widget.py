#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Vidar Tonaas Fauske.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import Widget
from traitlets import Unicode, Undefined
import numpy as np
from ipydatawidgets import DataUnion, data_union_serialization
import pyvtk

module_name = "jupyter-vtk-datawidgets"
module_version = "0.1.0"


class VtkDataWidget(Widget):
    """TODO: Add docstring here
    """
    _model_name =  Unicode('VtkDataModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name =  Unicode('VtkDataView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    header = Unicode().tag(sync=True)
    point_data = DataUnion().tag(sync=True, **data_union_serialization)
    cell_data = DataUnion().tag(sync=True, **data_union_serialization)
    structure = DataUnion().tag(sync=True, **data_union_serialization)

    def __init__(self, filename=None, point_data=Undefined, cell_data=Undefined, structure=Undefined):
        if f is not None:
            if not isinstance(filename, str):
                raise TypeError("Filename must be string.")
            vtkData = pyvtk.VtkData(filename)
            if point_data is Undefined:
                point_data = vtkData.point_data
            if cell_data is Undefined:
                cell_data
        
        super(VtkDataWidget, self).__init__(
            point_data=point_data,
            cell_data=cell_data,
            structure=structure,
        )
        
