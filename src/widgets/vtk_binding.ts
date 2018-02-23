'use strict'

// Data sets:
// @ts-ignore
import vtkPolyData from 'vtk.js/Sources/Common/DataModel/PolyData';
// @ts-ignore
import vtkImageData from 'vtk.js/Sources/Common/DataModel/ImageData';
// @ts-ignore
import vtkDataArray from 'vtk.js/Sources/Common/Core/DataArray';

// @ts-ignore
import vtk from 'vtk.js/Sources/vtk';
// @ts-ignore
import macro from 'vtk.js/Sources/macro';

import {
  getArray
} from 'jupyter-dataserializers';


function convertDataArray(widget: any) {
  const data = getArray(widget.get('data'));

  return {
    name: widget.get('name'),
    numberOfComponents: data ? data.shape[data.shape.length - 1] : 0,
    values: data ? data.data : null,
    vtkClass: 'vtkDataArray',
  };
}


function convertFieldSetArray(widget: any) {
  return {data: convertDataArray(widget)}
}


const CELL_ARRAYS = ['Verts', 'Lines', 'Strips', 'Polys'];


function convertContainer(widget: any) {
  const dataArrays = widget.get('data_arrays');
  const attributes = widget.get('attributes');
  const kind = widget.get('kind');
  if (['PointData', 'CellData'].indexOf(kind) !== -1) {
    // vtkDataSetAttributes
    const res: any = {
      vtkClass: "vtkDataSetAttributes",
      arrays: dataArrays.map((da: any) => convertFieldSetArray(da)),
    };
    const names = dataArrays.map((da: any) => da.get('name'));
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


function convertMetadata(metadata: any): any {
  const ret: any = {};
  if (metadata) {
    for (let key of Object.keys(metadata)) {
      if (key === 'whole_extent') {
        ret['extent'] = metadata[key];
      } else {
        ret[key] = metadata[key];
      }
    }
  }
  return ret;
}


function deCapitalize(str: string) {
  return str.replace(/^./, c => c.toLowerCase());
}


function vtkJupyterBridge(publicAPI: any, model: any) {
  // Set our className
  model.classHierarchy.push('vtkJupyterBridge');

  function updateFromBridge(outData: any) {
    const dataset = model.widget.get('dataset');
    const containers = dataset.get('containers');
    const data = {
      vtkClass: dataset.get('kind'),
      ...convertMetadata(dataset.get('metadata')),
    };
    for (let container of containers) {
      data[deCapitalize(container.get('kind'))] = convertContainer(container);
    }
    outData.splice(0, outData.length, vtk(data));
  }

  function onWidgetChanged() {
    publicAPI.modified();
  }

  // Connect to widget events:
  model.widget.on('change', onWidgetChanged);
  model.widget.on('childchange', onWidgetChanged);

  publicAPI.requestData = (inData: any, outData: any) => {
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

export function extend(publicAPI: any, model: any, initialValues = {}) {
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
