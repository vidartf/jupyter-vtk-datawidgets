
import base64
import xml.etree.cElementTree as ET

try:
    from StringIO import cStringIO as BytesIO
except ImportError:
    from io import BytesIO

import re

import numpy

_RE_TYPE = re.compile(r'P?(((Image)|(Poly))Data|((Rectilinear)|(Structured)|(Unstructured))Grid)')

_types = (
    'ImageData', 'RectilinearGrid', 'StructuredGrid', 'PolyData',
    'UnstructuredGrid',
)

_expected_piece_tags = {
    'ImageData': ['PointData', 'CellData'],
    'RectilinearGrid': ['PointData', 'CellData', 'Coordinates'],
    'StructuredGrid': ['PointData', 'CellData', 'Points'],
    'PolyData': ['PointData', 'CellData', 'Points', 'Verts', 'Lines', 'Strips', 'Polys'],
    'UnstructuredGrid': ['PointData', 'CellData', 'Points', 'Cells'],
}

vtu_to_numpy_type = {
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
numpy_to_vtu_type = {v: k for k, v in vtu_to_numpy_type.items()}



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
    out = {}
    out['byte_order'] = root.attrib.get('byte_order', None)
    out['version'] = root.attrib.get('version', None)
    out['compressor'] = root.attrib.get('compressor', None)
    out['type'] = root.attrib['type']
    out['appended_data'] = []
    conf['compressor'] = out['compressor']
    for c in root:
        if c.tag == out['type']:
            out['dataset'] = _proc(c, path + (c.tag,), conf)
        elif c.tag == 'AppendendData':
            assert c.attrib['encoding'] == 'base64'
            data = c.text.strip()
            # The appended data always begins with a (meaningless)
            # underscore.
            assert data[0] == '_'
            out['appended_data'].append(data[1:])
    return out

def _proc_main_tag(node, path, conf):
    is_parallel = node.tag[0] == 'P'

    out = {}
    out.update({kv for kv in _proc_attributes(node.attrib)})
    pieces = []
    for sub in node:
        if sub.tag == 'Piece':
            pieces.append(_proc(sub, path + (sub.tag,), conf))
    out['pieces'] = pieces
    return out
        
def _proc_piece(node, path, conf):
    out = {}
    out.update({kv for kv in _proc_attributes(node.attrib)})
    for sub in node:
        if sub.tag in _expected_piece_tags[path[-2]]:
            out[sub.tag] = _proc(sub, path + (sub.tag,), conf)
    return out

def _proc_pc_data(node, path, conf):
    out = _proc_sub_piece_data(node, path, conf)
    names = []
    for da in out['data_arrays']:
        names.append(da['Name'])
    for key, value in node.attrib.items():
        if key in ('Scalars', 'Vectors', 'Normals', 'Tensors', 'TCoords'):
            assert value in names, 'Could not find array name %r in %r' % (
                value, names)
            out[key] = value
    return out

def _proc_points(node, path, conf):
    out = _proc_sub_piece_data(node, path, conf)
    assert len(out['data_arrays']) == 1
    da = out['data_arrays'][0]
    assert da.get('NumberOfComponents', 0) == 3
    return out

def _proc_coordinates(node, path, conf):
    out = _proc_sub_piece_data(node, path, conf)
    assert len(out['data_arrays']) == 3
    return out

def _proc_sub_piece_data(node, path, conf):
    out = {}
    out['data_arrays'] = []
    for sub in node:
        if sub.tag != 'DataArray':
            continue
        da = _proc(sub, path + (sub.tag,), conf)
        out['data_arrays'].append(da)
    return out

def _proc_data_array(node, path, conf):
    out = {}
    for k in ('type', 'format', 'Name'):
        out[k] = node.attrib.get(k, None)
    for k in ('NumberOfComponents', 'offset'):
        try:
            out[k] = int(node.attrib[k])
        except KeyError:
            pass
    data = read_data(node, conf)
    if data is not None:
        out['data'] = data
    return out


def _proc_attributes(attrib):
    for k, v in attrib.items():
        if (k not in ('Extent', 'Origin', 'Spacing', 'WholeExtent') or
                not k.startswith('NumberOf')):
            continue
        s = v.split()
        if len(s) == 1:
            yield k, float(s[0])
        yield k, [float(a) for a in s]


_processors = {
    '/': _proc_root,
    '/*': _proc_main_tag,
    '/*/Piece': _proc_piece,
    '/*/Piece/PointData': _proc_pc_data,
    '/*/Piece/CellData': _proc_pc_data,
    '/*/Piece/Points': _proc_points,
    '/*/Piece/Coordinates': _proc_coordinates,
    '/*/Piece/*': _proc_sub_piece_data,
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

def _read_binary(data, data_type, conf):
    # first read the the block size; it determines the size of the header
    dtype = vtu_to_numpy_type[conf.get('header_type', 'UInt32')]
    num_bytes_per_item = numpy.dtype(dtype).itemsize
    num_chars = _num_bytes_to_num_base64_chars(num_bytes_per_item)
    byte_string = base64.b64decode(data[:num_chars])[:num_bytes_per_item]
    num_blocks = numpy.fromstring(byte_string, dtype)[0]

    # read the entire header
    num_header_items = 3 + num_blocks
    num_header_bytes = num_bytes_per_item * num_header_items
    num_header_chars = _num_bytes_to_num_base64_chars(num_header_bytes)
    byte_string = base64.b64decode(data[:num_header_chars])
    header = numpy.fromstring(byte_string, dtype)

    # num_blocks = header[0]
    # max_uncompressed_block_size = header[1]
    # last_compressed_block_size = header[2]
    block_sizes = header[3:]

    # Read the block data
    byte_array = base64.b64decode(data[num_header_chars:])
    dtype = vtu_to_numpy_type[data_type]
    num_bytes_per_item = numpy.dtype(dtype).itemsize

    byte_offsets = numpy.concatenate(
            [[0], numpy.cumsum(block_sizes, dtype=block_sizes.dtype)]
            )
    # https://github.com/numpy/numpy/issues/10135
    byte_offsets = byte_offsets.astype(numpy.int64)

    # process the compressed data
    if conf.get('compressor', None) == 'vtkZLibDataCompressor':
        import zlib
        block_data = numpy.concatenate([
            numpy.fromstring(zlib.decompress(
                byte_array[byte_offsets[k]:byte_offsets[k+1]]
                ), dtype=dtype)
            for k in range(num_blocks)
        ])
    else:
        block_data = numpy.concatenate([
            numpy.fromstring(
                byte_array[byte_offsets[k]:byte_offsets[k+1]],
                dtype=dtype)
            for k in range(num_blocks)
        ])

    return block_data

def read_data(node, conf):
    if node.attrib['format'] == 'ascii':
        # ascii
        data = numpy.array(
            node.text.split(),
            dtype=vtu_to_numpy_type[node.attrib['type']]
            )
    elif node.attrib['format'] == 'binary':
        data = _read_binary(node.text.strip(), node.attrib['type'], conf)
    else:
        # appended data
        assert node.attrib['format'] == 'appended', \
            'Unknown data format \'{}\'.'.format(node.attrib['format'])

        return None

    if 'NumberOfComponents' in node.attrib:
        data = data.reshape(-1, int(node.attrib['NumberOfComponents']))
    return data


def _inline_appended_data(data, conf):
    appdata = data.pop('appended_data')
    encoded = appdata[0] if appdata else ''
    
    for sub in data['dataset']['pieces']:
        for da in sub.get('data_arrays', []):
            if da['format'] != 'appended':
                continue
            da['format'] = 'binary'
            offset = da.pop('offset')
            data = _read_binary(encoded[offset:], da['type'], conf)
            if 'NumberOfComponents' in da:
                data = data.reshape(-1, da['NumberOfComponents'])
            da['data'] = data


class VtkXmlReader(object):
    def __init__(self, filename):
        self.load(filename)
    
    def load(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        _validate_root(root)

        conf = {}
        partial = _proc(root, (), conf)
        _inline_appended_data(partial, conf)
        self.data = partial

