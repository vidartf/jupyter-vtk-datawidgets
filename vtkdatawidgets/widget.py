#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Vidar Tonaas Fauske.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from traitlets import Unicode, Undefined, Dict
from ipydatawidgets import DataWidget

from .vtkio import VtkXmlReader
from .serializers import vtk_data_serialization

module_name = "jupyter-vtk-datawidgets"
module_version = "0.1.0"


class VtkDataWidget(DataWidget):
    """TODO: Add docstring here
    """
    _model_name =  Unicode('VtkDataModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name =  Unicode('VtkDataView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    data = Dict().tag(sync=True, **vtk_data_serialization)

    def __init__(self, filename=None, data=None):
        if filename is not None:
            if not isinstance(filename, str):
                raise TypeError("Filename must be string.")
            data = VtkXmlReader(filename)
        
        super(VtkDataWidget, self).__init__(
            data=data,
        )
        
