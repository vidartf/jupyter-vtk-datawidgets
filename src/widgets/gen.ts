
import {
  WidgetModel, DOMWidgetModel,
  WidgetView, DOMWidgetView,
  unpack_models
} from '@jupyter-widgets/base';

import {
  data_union_serialization
} from 'jupyter-dataserializers';


import {
  ManagerBase
} from '@jupyter-widgets/base';

import {
  VtkWidgetModel
} from './base';

/**
 * Type declaration for general widget serializers.
 *
 * Declared in lieu of proper interface in jupyter-widgets.
 */
export interface ISerializers {
  [key: string]: {
      deserialize?: (value?: any, manager?: ManagerBase<any>) => any;
      serialize?: (value?: any, widget?: WidgetModel) => any;
  };
}


export
class DataArrayModel extends VtkWidgetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "DataArrayModel",
      data: undefined,
      name: null,
    }}
  }

  static serializers = {
    ...VtkWidgetModel.serializers,
    data: data_union_serialization,
  };
}


export
class DataContainerModel extends VtkWidgetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "DataContainerModel",
      attributes: undefined,
      data_arrays: undefined,
      kind: undefined,
    }}
  }

  static serializers = {
    ...VtkWidgetModel.serializers,
    data_arrays: { deserialize: unpack_models },
  };
}


export
class DataSetModel extends VtkWidgetModel {

  defaults() {
    return {...super.defaults(), ...{
      containers: undefined,
    }}
  }

  static serializers = {
    ...VtkWidgetModel.serializers,
    containers: { deserialize: unpack_models },
  };
}


export
class MutableDataSetModel extends DataSetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "MutableDataSetModel",
      kind: undefined,
      metadata: undefined,
    }}
  }

}


export
class ImageDataModel extends DataSetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "ImageDataModel",
      origin: [],
      spacing: [],
      whole_extent: [],
    }}
  }

}


export
class RectilinearGridModel extends DataSetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "RectilinearGridModel",
      whole_extent: [],
    }}
  }

}


export
class StructuredGridModel extends DataSetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "StructuredGridModel",
      whole_extent: [],
    }}
  }

}


export
class PolyDataModel extends DataSetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "PolyDataModel",
    }}
  }

}


export
class UnstructuredGridModel extends DataSetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "UnstructuredGridModel",
    }}
  }

}


export
class VtkRendererModel extends DOMWidgetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_module: "jupyter-vtk-datawidgets",
      _model_module_version: "0.1.0",
      _model_name: "VtkRendererModel",
      _view_module: "jupyter-vtk-datawidgets",
      _view_module_version: "0.1.0",
      _view_name: "VtkRendererView",
      background: [0,0,0],
      dataset: undefined,
      size: [512, 512],
    }}
  }

  static serializers = {
    ...DOMWidgetModel.serializers,
    dataset: { deserialize: unpack_models },
  };
}
