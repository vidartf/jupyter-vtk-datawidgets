
import vtk

from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import vtkConstants, numpy_support

import numpy

from .widget import MutableDataSet, DataContainer, DataArray


array_lut = {}

container_lut = {}

widget_lut = {}


_std_attribute_indices = {
    vtk.vtkDataSetAttributes.SCALARS: 'Scalars',
    vtk.vtkDataSetAttributes.VECTORS: 'Vectors',
    vtk.vtkDataSetAttributes.NORMALS: 'Normals',
    vtk.vtkDataSetAttributes.TCOORDS: 'TCoords',
    vtk.vtkDataSetAttributes.TENSORS: 'Tensors',
}

def _std_attributes(attrib):
    for type_id, name in _std_attribute_indices.items():
        array = attrib.GetAttribute(type_id)
        if array is None:
            yield name, None
            continue
        yield name, array.GetName()


def _get_field_arrays(field):
    output = []
    for i in range(field.GetNumberOfArrays()):
        array = field.GetAbstractArray(i)
        output.append(DataArray(name=array.GetName(), data=vtk2array(array)))
    return output


class VtkJupyterBridge(VTKPythonAlgorithmBase):
    def __init__(self):
        super(VtkJupyterBridge, self).__init__(
            nInputPorts=1, inputType='vtkDataSet',  # defaults, but explicit
            nOutputPorts=0)
        widget_lut[self] = MutableDataSet()


    @property
    def widget(self):
        return widget_lut[self]


    def RequestData(self, request, inInfo, outInfo):
        containers = []
        metadata = {}
        inp = vtk.vtkDataSet.GetData(inInfo[0])

        cell_data = inp.GetCellData()
        point_data = inp.GetPointData()

        containers.append(DataContainer(
            kind='CellData',
            data_arrays=_get_field_arrays(cell_data),
            attributes=dict(_std_attributes(cell_data)),
        ))

        containers.append(DataContainer(
            kind='PointData',
            data_arrays=_get_field_arrays(point_data),
            attributes=dict(_std_attributes(point_data)),
        ))


        if inp.IsA('vtkPointSet'):
            points = inp.GetPoints().GetData()
            containers.append(DataContainer(
                kind='Points',
                data_arrays=(DataArray(name=points.GetName(), data=vtk2array(points)),),
            ))
        if inp.IsA('vtkRectilinearGrid'):
            containers.append(DataContainer(
                kind='Coordinates',
                data_arrays=(
                    DataArray(name='XCoordinates', data=vtk2array(inp.GetXCoordinates())),
                    DataArray(name='YCoordinates', data=vtk2array(inp.GetYCoordinates())),
                    DataArray(name='ZCoordinates', data=vtk2array(inp.GetZCoordinates())),
                )
            ))

        if inp.IsA('vtkPolyData'):
            verts = inp.GetVerts()
            lines = inp.GetLines()
            strips = inp.GetStrips()
            polys = inp.GetPolys()
            containers.append(DataContainer(
                kind='Verts',
                data_arrays=(
                    DataArray(name='cells', data=vtk2array(verts.GetData())),
                )
            ))
            containers.append(DataContainer(
                kind='Lines',
                data_arrays=(
                    DataArray(name='cells', data=vtk2array(lines.GetData())),
                )
            ))
            containers.append(DataContainer(
                kind='Strips',
                data_arrays=(
                    DataArray(name='cells', data=vtk2array(strips.GetData())),
                )
            ))
            containers.append(DataContainer(
                kind='Polys',
                data_arrays=(
                    DataArray(name='cells', data=vtk2array(polys.GetData())),
                )
            ))
        if inp.IsA('vtkUnstructuredGrid'):
            connectivity = inp.GetCells().GetData()
            offsets = inp.GetCellLocationsArray()
            types = inp.GetCellTypesArray()
            containers.append(DataContainer(
                kind='Cells',
                data_arrays=(
                    DataArray(name='connectivity', data=vtk2array(connectivity)),
                    DataArray(name='offsets', data=vtk2array(offsets)),
                    DataArray(name='types', data=vtk2array(types)),
                ),
            ))
        if (
                inp.IsA('vtkImageData') or
                inp.IsA('vtkRectilinearGrid') or
                inp.IsA('vtkRectilinearGrid')
            ):
            metadata['whole_extent'] = inp.GetExtent()
        if inp.IsA('vtkImageData'):
            metadata['origin'] = inp.GetOrigin()
            metadata['spacing'] = inp.GetSpacing()

        # TODO: Move data to widget, using LUT's to check for
        # widgets already representing the data.
        with widget_lut[self].hold_sync():
            widget_lut[self].kind = inp.GetClassName()
            widget_lut[self].containers = containers
            widget_lut[self].metadata = metadata

        return 1


# ------------------------------------------------------------------------

# The code below this point is copied from the TVTK source under the
# following license:
"""
This software is OSI Certified Open Source Software.
OSI Certified is a certification mark of the Open Source Initiative.

Copyright (c) 2006, Enthought, Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 * Neither the name of Enthought, Inc. nor the names of its contributors may
   be used to endorse or promote products derived from this software without
   specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


# Useful constants for VTK arrays.
VTK_ID_TYPE_SIZE = vtk.vtkIdTypeArray().GetDataTypeSize()
if VTK_ID_TYPE_SIZE == 4:
    ID_TYPE_CODE = numpy.int32
elif VTK_ID_TYPE_SIZE == 8:
    ID_TYPE_CODE = numpy.int64

VTK_LONG_TYPE_SIZE = vtk.vtkLongArray().GetDataTypeSize()
if VTK_LONG_TYPE_SIZE == 4:
    LONG_TYPE_CODE = numpy.int32
    ULONG_TYPE_CODE = numpy.uint32
elif VTK_LONG_TYPE_SIZE == 8:
    LONG_TYPE_CODE = numpy.int64
    ULONG_TYPE_CODE = numpy.uint64


######################################################################
# The array cache.
######################################################################
class ArrayCache(object):

    """Caches references to numpy arrays that are not copied but views
    of which are converted to VTK arrays.  The caching prevents the user
    from deleting or resizing the numpy array after it has been sent
    down to VTK.  The cached arrays are automatically removed when the
    VTK array destructs."""

    ######################################################################
    # `object` interface.
    ######################################################################
    def __init__(self):
        # The cache.
        self._cache = {}

    def __len__(self):
        return len(self._cache)

    def __contains__(self, vtk_arr):
        key = vtk_arr.__this__
        return key in self._cache

    ######################################################################
    # `ArrayCache` interface.
    ######################################################################
    def add(self, vtk_arr, np_arr):
        """Add numpy array corresponding to the vtk array to the
        cache."""
        key = vtk_arr.__this__
        cache = self._cache

        # Setup a callback so this cached array reference is removed
        # when the VTK array is destroyed.  Passing the key to the
        # `lambda` function is necessary because the callback will not
        # receive the object (it will receive `None`) and thus there
        # is no way to know which array reference one has to remove.
        vtk_arr.AddObserver('DeleteEvent', lambda o, e, key=key: \
                            self._remove_array(key))

        # Cache the array
        cache[key] = np_arr

    def get(self, vtk_arr):
        """Return the cached numpy array given a VTK array."""
        key = vtk_arr.__this__
        return self._cache[key]

    ######################################################################
    # Non-public interface.
    ######################################################################
    def _remove_array(self, key):
        """Private function that removes the cached array.  Do not
        call this unless you know what you are doing."""
        try:
            del self._cache[key]
        except KeyError:
            pass


_array_cache = ArrayCache()


def get_vtk_to_numeric_typemap():
    """Returns the VTK array type to numpy array type mapping."""
    _vtk_arr = {vtkConstants.VTK_BIT:numpy.bool,
                vtkConstants.VTK_CHAR:numpy.int8,
                vtkConstants.VTK_UNSIGNED_CHAR:numpy.uint8,
                vtkConstants.VTK_SHORT:numpy.int16,
                vtkConstants.VTK_UNSIGNED_SHORT:numpy.uint16,
                vtkConstants.VTK_INT:numpy.int32,
                vtkConstants.VTK_UNSIGNED_INT:numpy.uint32,
                vtkConstants.VTK_LONG:LONG_TYPE_CODE,
                vtkConstants.VTK_UNSIGNED_LONG:ULONG_TYPE_CODE,
                vtkConstants.VTK_ID_TYPE:ID_TYPE_CODE,
                vtkConstants.VTK_FLOAT:numpy.float32,
                vtkConstants.VTK_DOUBLE:numpy.float64}
    return _vtk_arr


def get_numeric_array_type(vtk_array_type):
    """Returns a numpy array typecode given a VTK array type."""
    return get_vtk_to_numeric_typemap()[vtk_array_type]


def vtk2array(vtk_array):
    """Converts a VTK data array to a numpy array.
    Given a subclass of vtkDataArray, this function returns an
    appropriate numpy array containing the same data.  The function
    is very efficient since it uses the VTK imaging pipeline to
    convert the data.  If a sufficiently new version of VTK (5.2) is
    installed then it actually uses the buffer interface to return a
    view of the VTK array in the returned numpy array.
    Parameters
    ----------
    - vtk_array : `vtkDataArray`
      The VTK data array to be converted.
    """
    typ = vtk_array.GetDataType()
    assert typ in get_vtk_to_numeric_typemap().keys(), \
           "Unsupported array type %s"%typ

    shape = vtk_array.GetNumberOfTuples(), \
            vtk_array.GetNumberOfComponents()
    if shape[0] == 0:
        dtype = get_numeric_array_type(typ)
        return numpy.array([], dtype)

    # First check if this array already has a numpy array cached,
    # if it does and the array size has not been changed, reshape
    # that and return it.
    if vtk_array in _array_cache:
        arr = _array_cache.get(vtk_array)
        if shape[1] == 1:
            shape = (shape[0], )
        if arr.size == numpy.prod(shape):
            arr = numpy.reshape(arr, shape)
            return arr

    # If VTK's new numpy support is available, use the buffer interface.
    if numpy_support is not None and typ != vtkConstants.VTK_BIT:
        dtype = get_numeric_array_type(typ)
        result = numpy.frombuffer(vtk_array, dtype=dtype)
        if shape[1] == 1:
            shape = (shape[0], )
        result.shape = shape
        return result

    # Setup an imaging pipeline to export the array.
    img_data = vtk.vtkImageData()
    img_data.SetDimensions(shape[0], 1, 1)
    if typ == vtkConstants.VTK_BIT:
        iarr = vtk.vtkCharArray()
        iarr.DeepCopy(vtk_array)
        img_data.GetPointData().SetScalars(iarr)
    elif typ == vtkConstants.VTK_ID_TYPE:
        # Needed since VTK_ID_TYPE does not work with VTK 4.5.
        iarr = vtk.vtkLongArray()
        iarr.SetNumberOfTuples(vtk_array.GetNumberOfTuples())
        nc = vtk_array.GetNumberOfComponents()
        iarr.SetNumberOfComponents(nc)
        for i in range(nc):
            iarr.CopyComponent(i, vtk_array, i)
        img_data.GetPointData().SetScalars(iarr)
    else:
        img_data.GetPointData().SetScalars(vtk_array)

    if is_old_pipeline():
        img_data.SetNumberOfScalarComponents(shape[1])
        if typ == vtkConstants.VTK_ID_TYPE:
            # Hack necessary because vtkImageData can't handle VTK_ID_TYPE.
            img_data.SetScalarType(vtkConstants.VTK_LONG)
            r_dtype = get_numeric_array_type(vtkConstants.VTK_LONG)
        elif typ == vtkConstants.VTK_BIT:
            img_data.SetScalarType(vtkConstants.VTK_CHAR)
            r_dtype = get_numeric_array_type(vtkConstants.VTK_CHAR)
        else:
            img_data.SetScalarType(typ)
            r_dtype = get_numeric_array_type(typ)
        img_data.Update()
    else:
        if typ == vtkConstants.VTK_ID_TYPE:
            r_dtype = get_numeric_array_type(vtkConstants.VTK_LONG)
        elif typ == vtkConstants.VTK_BIT:
            r_dtype = get_numeric_array_type(vtkConstants.VTK_CHAR)
        else:
            r_dtype = get_numeric_array_type(typ)
        img_data.Modified()

    exp = vtk.vtkImageExport()
    if is_old_pipeline():
        exp.SetInput(img_data)
    else:
        exp.SetInputData(img_data)

    # Create an array of the right size and export the image into it.
    im_arr = numpy.empty((shape[0]*shape[1],), r_dtype)
    exp.Export(im_arr)

    # Now reshape it.
    if shape[1] == 1:
        shape = (shape[0], )
    im_arr = numpy.reshape(im_arr, shape)
    return im_arr
