
import {
  WidgetModel, DOMWidgetModel,
  WidgetView, DOMWidgetView,
  unpack_models, ManagerBase
} from '@jupyter-widgets/base';


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
class VtkWidgetModel extends WidgetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_module: "jupyter-vtk-datawidgets",
      _model_module_version: "0.1.0",
      _view_module: "jupyter-vtk-datawidgets",
      _view_module_version: "0.1.0",
    }}
  }

}


export
class DataArrayModel extends VtkWidgetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "DataArray",
      data: undefined,
      name: null,
    }}
  }

}


export
class DataContainerModel extends VtkWidgetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "DataContainer",
      attributes: undefined,
      data_arrays: undefined,
      kind: undefined,
    }}
  }

  static serializers: ISerializers = {
    ...VtkWidgetModel.serializers,
    data_arrays: { deserialize: unpack_models },
  }
}


export
class DataSetModel extends VtkWidgetModel {

  defaults() {
    return {...super.defaults(), ...{
      containers: undefined,
    }}
  }

  static serializers: ISerializers = {
    ...VtkWidgetModel.serializers,
    containers: { deserialize: unpack_models },
  }
}


export
class MutableDataSetModel extends VtkWidgetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "MutableDataSet",
      containers: undefined,
      kind: undefined,
      metadata: undefined,
    }}
  }

  static serializers: ISerializers = {
    ...VtkWidgetModel.serializers,
    containers: { deserialize: unpack_models },
  }
}


export
class ImageDataModel extends DataSetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "ImageData",
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
      _model_name: "RectilinearGrid",
      whole_extent: [],
    }}
  }

}


export
class StructuredGridModel extends DataSetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "StructuredGrid",
      whole_extent: [],
    }}
  }

}


export
class PolyDataModel extends DataSetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "PolyData",
    }}
  }

}


export
class UnstructuredGridModel extends DataSetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_name: "UnstructuredGrid",
    }}
  }

}
