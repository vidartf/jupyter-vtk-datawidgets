
import pytest

import warnings

import vtk
from ..vtkio import read_vtk_xml

from ..widget import PolyData, MutableDataSet



@pytest.mark.filterwarnings('ignore:Cannot serialize (u)int64 data')
@pytest.mark.parametrize("mode", [vtk.vtkXMLWriter.Ascii, vtk.vtkXMLWriter.Binary, vtk.vtkXMLWriter.Appended])
@pytest.mark.parametrize("byte_order", [vtk.vtkXMLWriter.BigEndian, vtk.vtkXMLWriter.LittleEndian])
@pytest.mark.parametrize("header_type", [vtk.vtkXMLWriter.UInt32, vtk.vtkXMLWriter.UInt64])
@pytest.mark.parametrize("compressor", [vtk.vtkXMLWriter.NONE, vtk.vtkXMLWriter.ZLIB, vtk.vtkXMLWriter.LZ4])
def test_vtkio_poly(mode, byte_order, header_type, compressor, tmpdir):
    if compressor == vtk.vtkXMLWriter.LZ4:
        pytest.mark.xfail()
    source = vtk.vtkSphereSource()
    fname = str(tmpdir.join('test.vtp'))

    # Write the file
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(fname)
    writer.SetInputConnection(source.GetOutputPort())
    writer.SetDataMode(mode)
    writer.SetByteOrder(byte_order)
    writer.SetHeaderType(header_type)
    writer.SetCompressorType(compressor)
    writer.Write()

    try:
        dataset = read_vtk_xml(fname)
    except ValueError:
        if compressor == vtk.vtkXMLWriter.LZ4 and mode != vtk.vtkXMLWriter.Ascii:
            pytest.xfail('LZ4 compression not supported')
        raise
    assert isinstance(dataset, MutableDataSet)
    assert dataset.kind == 'vtkPolyData'


def test_vtkio_image(tmpdir):
    source = vtk.vtkImageMandelbrotSource()
    fname = str(tmpdir.join('test.vti'))

    # Write the file
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(fname)
    writer.SetInputConnection(source.GetOutputPort())
    writer.SetDataModeToBinary()
    writer.Write()

    dataset = read_vtk_xml(fname)
    assert isinstance(dataset, MutableDataSet)
    assert dataset.kind == 'vtkImageData'