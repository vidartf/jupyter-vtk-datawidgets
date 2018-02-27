#
#
# Parts of this code was taken from meshio under the following license:
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Nico Schlömer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import base64
import xml.etree.cElementTree as ET

try:
    from StringIO import cStringIO as BytesIO
except ImportError:
    from io import BytesIO

import re

import numpy

import vtkdatawidgets.widget as vtk_widgets

_RE_TYPE = re.compile(r'P?(((Image)|(Poly))Data|((Rectilinear)|(Structured)|(Unstructured))Grid)')

_types = (
    'ImageData', 'RectilinearGrid', 'StructuredGrid', 'PolyData',
    'UnstructuredGrid',
)

expected_piece_tags = {
    'ImageData': ['PointData', 'CellData'],
    'RectilinearGrid': ['PointData', 'CellData', 'Coordinates'],
    'StructuredGrid': ['PointData', 'CellData', 'Points'],
    'PolyData': ['PointData', 'CellData', 'Points', 'Verts', 'Lines', 'Strips', 'Polys'],
    'UnstructuredGrid': ['PointData', 'CellData', 'Points', 'Cells'],
}

_vtu_to_numpy_type = {
    'Float32': numpy.dtype(numpy.float32),
    'Float64': numpy.dtype(numpy.float64),
    'Int8': numpy.dtype(numpy.int8),
    'Int16': numpy.dtype(numpy.int16),
    'Int32': numpy.dtype(numpy.int32),
    'Int64': numpy.dtype(numpy.int64),
    'UInt8': numpy.dtype(numpy.uint8),
    'UInt16': numpy.dtype(numpy.uint16),
    'UInt32': numpy.dtype(numpy.uint32),
    'UInt64': numpy.dtype(numpy.uint64),
    }
numpy_to_vtu_type = {v: k for k, v in _vtu_to_numpy_type.items()}

_vtu_to_numpy_byte_order = {
    'LittleEndian': '<',
    'BigEndian': '>',
}

def vtu_to_numpy_type(key, byte_order='LittleEndian'):
    return _vtu_to_numpy_type[key].newbyteorder(_vtu_to_numpy_byte_order[byte_order])



def _validate_root(root):
    assert root.tag == 'VTKFile'
    if root.attrib['version'] not in ['0.1', '1.0']:
        raise ValueError('Unknown VTK XML file version \'{}\'.'.format(
            root.attrib['version']))

    byte_order = root.attrib.get('byte_order', None)
    assert byte_order in ['LittleEndian', 'BigEndian', None], \
        'Unknown byte order \'{}\'.'.format(byte_order)

    main_type = root.attrib['type']
    assert _RE_TYPE.match(main_type), 'Unknown type: %r' % main_type

def _proc_root(root, path, conf):
    main_type = root.attrib['type']
    appended_data = []
    conf['compressor'] = root.attrib.get('compressor', None)
    conf['byte_order'] = root.attrib['byte_order']
    conf['header_type'] = root.attrib['header_type']
    conf['version'] = root.attrib['version']
    dataset_node = None
    for c in root:
        if c.tag == main_type:
            if dataset_node is not None:
                raise ValueError('Multiple %r elements in file!' % main_type)
            dataset_node = c
        elif c.tag == 'AppendedData':
            assert c.attrib['encoding'] == 'base64'
            data = c.text.strip()
            # The appended data always begins with a (meaningless)
            # underscore.
            assert data[0] == '_'
            appended_data.append(data[1:])
    conf['appended_data'] = appended_data
    dataset = _proc(dataset_node, path + (dataset_node.tag,), conf)
    return dataset, appended_data

def _proc_main_tag(node, path, conf):
    main_type = node.tag
    is_parallel = main_type[0] == 'P'

    containers = []
    for sub in node:
        if sub.tag == 'Piece':
            containers.extend(_proc(sub, path + (sub.tag,), conf))

    kwargs = dict(
        kind='vtk' + main_type,
        metadata=dict({k: v for k, v in _proc_attributes(node.attrib)}),
        containers=containers,
    )

    #try:
    #    cls = getattr(vtk_widgets, main_type)
    #except AttributeError:
    #    raise ValueError('Unsupported dataset type: %r' % main_type)
    return vtk_widgets.MutableDataSet(**kwargs)

def _proc_piece(node, path, conf):
    containers = []
    for sub in node:
        if sub.tag in expected_piece_tags[path[-2]]:
            containers.append(_proc(sub, path + (sub.tag,), conf))
    return containers

def _proc_pc_data(node, path, conf):
    data_arrays = _proc_piece_dataarrays(node, path, conf)
    names = []
    for da in data_arrays:
        names.append(da.name)
    attributes = {}
    for key, value in node.attrib.items():
        if key in ('Scalars', 'Vectors', 'Normals', 'Tensors', 'TCoords'):
            assert value in names, 'Could not find array name %r in %r' % (
                value, names)
            attributes[key] = value
    return vtk_widgets.DataContainer(
        attributes=attributes,
        kind=node.tag,
        data_arrays=data_arrays,
    )

def _proc_points(node, path, conf):
    data_arrays = _proc_piece_dataarrays(node, path, conf)
    assert len(data_arrays) == 1
    da = data_arrays[0]
    assert da.data.shape[1] == 3
    return vtk_widgets.DataContainer(
        kind=node.tag,
        data_arrays=data_arrays,
    )

def _proc_coordinates(node, path, conf):
    data_arrays = _proc_piece_dataarrays(node, path, conf)
    assert len(data_arrays) == 3
    return vtk_widgets.DataContainer(
        kind=node.tag,
        data_arrays=data_arrays,
    )

def _proc_datacontainer_generic(node, path, conf):
    data_arrays = _proc_piece_dataarrays(node, path, conf)
    return vtk_widgets.DataContainer(
        kind=node.tag,
        data_arrays=data_arrays,
    )

def _proc_piece_dataarrays(node, path, conf):
    data_arrays = []
    for sub in node:
        if sub.tag != 'DataArray':
            continue
        da = _proc(sub, path + (sub.tag,), conf)
        data_arrays.append(da)
    return data_arrays

def _proc_data_array(node, path, conf):
    name = node.attrib.get('Name', None)
    data = _read_data(node, conf)
    return vtk_widgets.DataArray(
        data=data,
        name=name,
    )


def _proc_attributes(attrib):
    for k, v in attrib.items():
        if (k not in ('Origin', 'Spacing', 'WholeExtent')):
            continue
        s = v.split()
        yield k, [float(a) for a in s]


_processors = {
    '/': _proc_root,
    '/*': _proc_main_tag,
    '/*/Piece': _proc_piece,
    '/*/Piece/PointData': _proc_pc_data,
    '/*/Piece/CellData': _proc_pc_data,
    '/*/Piece/Points': _proc_points,
    '/*/Piece/Coordinates': _proc_coordinates,
    '/*/Piece/*': _proc_datacontainer_generic,
    '/*/Piece/*/DataArray': _proc_data_array,
}


def _proc(node, path, conf):
    for key, func in _processors.items():
        candidate = key[1:].split('/')
        if candidate == ['']:
            candidate = ()
        if len(candidate) != len(path):
            continue
        for a, b in zip(candidate, path):
            if a != '*' and a != b:
                break
        else:
            return func(node, path, conf)
    # TODO: warn unprocessed node?


def _num_bytes_to_num_base64_chars(num_bytes):
    # Rounding up in integer division works by double negation since Python
    # always rounds down.
    return -(-num_bytes // 3) * 4


def _hex_repr(data):
    return ' '.join('{:02x}'.format(x) for x in data)


def _read_binary_uncompressed(data, data_type, conf):
    byte_order = conf.get('byte_order', 'LittleEndian')
    # Data dtype:
    dtype = vtu_to_numpy_type(data_type, byte_order)
    # Header dtype:
    header_dtype = vtu_to_numpy_type(conf.get('header_type', 'UInt32'), byte_order)

    # Uncompressed format: [#bytes][DATA]
    # Read header: [#bytes]
    num_header_bytes = int(numpy.dtype(header_dtype).itemsize)
    num_header_chars = _num_bytes_to_num_base64_chars(num_header_bytes)
    byte_string = base64.b64decode(data[:num_header_chars])[:num_header_bytes]
    num_bytes = int(numpy.fromstring(byte_string, header_dtype)[0])

    if num_bytes <= 0:
        return numpy.empty([], dtype=dtype)
    num_chars = _num_bytes_to_num_base64_chars(num_header_bytes + num_bytes)
    byte_array = base64.b64decode(data[:num_chars])
    return numpy.fromstring(
            byte_array[num_header_bytes : num_header_bytes + num_bytes],
            dtype=dtype)


def _read_binary_compressed(data, data_type, conf):
    byte_order = conf.get('byte_order', 'LittleEndian')
    # Data dtype:
    dtype = vtu_to_numpy_type(data_type, byte_order)
    # Header dtype:
    header_dtype = vtu_to_numpy_type(conf.get('header_type', 'UInt32'), byte_order)

    byte_array = base64.b64decode(data)

    # Compressed format: [#blocks][#u-size][#p-size][#c-size-1][#c-size-2]...[#c-size-#blocks][DATA]
    #  [#blocks] = Number of blocks
    #  [#u-size] = Block size before compression
    #  [#p-size] = Size of last partial block (zero if it not needed)
    #  [#c-size-i] = Size in bytes of block i after compression

    num_headeritem_bytes = int(numpy.dtype(header_dtype).itemsize)
    num_header_chars = _num_bytes_to_num_base64_chars(num_headeritem_bytes)
    byte_string = base64.b64decode(data[:num_header_chars])[:num_headeritem_bytes]
    num_blocks = numpy.fromstring(byte_string, header_dtype)[0]

    if num_blocks <= 0:
        return numpy.empty([], dtype=dtype)

    # read the entire header
    num_headeritems = 3 + num_blocks
    num_header_bytes = int(num_headeritem_bytes * num_headeritems)
    num_header_chars = _num_bytes_to_num_base64_chars(num_header_bytes)
    byte_string = base64.b64decode(data[:num_header_chars])[:num_header_bytes]
    header = numpy.fromstring(byte_string, header_dtype)

    # num_blocks = header[0]
    # max_uncompressed_block_size = header[1]
    # last_compressed_block_size = header[2]
    block_sizes = header[3:]

    # Read the block data
    byte_offsets = numpy.concatenate(
            [[0], numpy.cumsum(block_sizes, dtype=numpy.uint64)]
            )
    # https://github.com/numpy/numpy/issues/10135
    byte_offsets = byte_offsets.astype(numpy.uint64)

    final_byte = int(byte_offsets[-1])

    # process the compressed data
    num_data_chars = _num_bytes_to_num_base64_chars(final_byte)
    byte_array = base64.b64decode(data[num_header_chars : num_header_chars + num_data_chars])[:final_byte]
    if conf['compressor'] == 'vtkZLibDataCompressor':
        import zlib
        block_data = numpy.concatenate([
            numpy.fromstring(zlib.decompress(
                byte_array[byte_offsets[k]:byte_offsets[k+1]]
                ), dtype=dtype)
            for k in range(num_blocks)
        ])
    else:
        raise ValueError('Unsupported compressor: %r' % conf['compressor'])

    return block_data


def _read_binary(data, data_type, conf):
    if conf['compressor'] is None:
        return _read_binary_uncompressed(data, data_type, conf)
    return _read_binary_compressed(data, data_type, conf)


def _read_data(node, conf):
    dtype = node.attrib['type']
    if node.attrib['format'] == 'ascii':
        # ascii
        data = numpy.array(
            node.text.split(),
            dtype=vtu_to_numpy_type(dtype, conf.get('byte_order', 'LittleEndian'))
            )
    elif node.attrib['format'] == 'binary':
        data = _read_binary(node.text.strip(), dtype, conf)
    else:
        # appended data
        assert node.attrib['format'] == 'appended', \
            'Unknown data format \'{}\'.'.format(node.attrib['format'])

        appdata = conf['appended_data']
        encoded = appdata[0] if appdata else ''

        offset = int(node.attrib['offset'])
        data = _read_binary(encoded[offset:], dtype, conf)

    if 'NumberOfComponents' in node.attrib:
        data = data.reshape(-1, int(node.attrib['NumberOfComponents']))
    return data



def read_vtk_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    _validate_root(root)

    return _proc(root, (), {})[0]

