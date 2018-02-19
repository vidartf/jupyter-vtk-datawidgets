

// Data sets:
import vtkPolyData from 'vtk.js/Sources/Common/DataModel/PolyData';
import vtkImageData from 'vtk.js/Sources/Common/DataModel/ImageData';
import vtkDataArray from 'vtk.js/Sources/Common/Core/DataArray';

import vtk from 'vtk.js/Sources/vtk';
import macro from 'vtk.js/Sources/macro';

import {
  getArray
} from 'jupyter-dataserializers';


function convertDataArray(widget) {
  const data = getArray(widget.get('data'));

  return {
    name: widget.get('name'),
    numberOfComponents: data.shape[0],
    values: data.data,
  };
}


CELL_ARRAYS = ['Verts', 'Lines', 'Strips', 'Polys']


function convertContainer(widget) {
  const dataArrays = widget.get('data_arrays');
  const attributes = widget.get('attributes');
  const kind = widget.get('kind');
  if (['PointData', 'CellData'].indexOf(kind) !== -1) {
    // vtkDataSetAttributes
    const res = {
      vtkClass: "vtkDataSetAttributes",
      arrays: dataArrays.map(da => convertDataArray(da)),
    };
    const names = dataArrays.map(da => da.name);
    for (let key of Object.keys(attributes)) {
      res[`active${key}`] = names.indexOf(key);
    }
    return res;
  } else if (kind === 'Points') {
    // vtkPointSet
    return {
      ...convertDataArray(dataArrays[0]),
      vtkClass: 'vtkPoints',
      name: '_points',
    };
  } else if (CELL_ARRAYS.indexOf(kind) !== -1) {
    return {
      ...convertDataArray(dataArrays[0]),
      vtkClass: 'vtkCellArray',
      name: `_${kind.toLowerCase()}`,
    };
  }
}


function convertMetadata(metadata) {
  const ret = {};
  for (let key of Object.keys(metadata)) {
    if (key === 'whole_extent') {
      ret['extent'] = metadata[key];
    } else {
      ret[key] = metadata[key];
    }
  }
  return ret;
}


function deCapitalize(str) {
  return str.replace(/^./, c => c.toLowerCase());
}


function vtkJupyterBridge(publicAPI, model) {
  // Set our className
  model.classHierarchy.push('vtkJupyterBridge');

  function updateFromBridge(outData) {
    const widget = model.widget;
    const containers = widget.get('containers');
    const data = {
      vtkClass: widget.get('kind'),
      ...convertMetadata(widget.get('metadata')),
    }
    for (let container of containers) {
      data[deCapitalize(container.get('kind'))] = convertContainer(container);
    }
    outData.splice(0, outData.length, vtk(data));
  }

  function onWidgetChanged() {
    model.modified();
  }

  // Connect to widget events:
  model.widget.on('change', onWidgetChanged);

  publicAPI.requestData = (inData, outData) => {
    updateFromBridge(outData);
  };
}


// ----------------------------------------------------------------------------
// Object factory
// ----------------------------------------------------------------------------

const DEFAULT_VALUES = {
  // widget: null,
  // dataType: null,
};

// ----------------------------------------------------------------------------

export function extend(publicAPI, model, initialValues = {}) {
  // @ts-ignore
  Object.assign(model, DEFAULT_VALUES, initialValues);

  // Build VTK API
  macro.obj(publicAPI, model);
  macro.get(publicAPI, model, ['widget']);
  macro.algo(publicAPI, model, 0, 1);

  // vtkXMLReader methods
  vtkJupyterBridge(publicAPI, model);
}

// ----------------------------------------------------------------------------

export const newInstance = macro.newInstance(extend, 'vtkJupyterBridge');

// ----------------------------------------------------------------------------

export default { extend, newInstance };
