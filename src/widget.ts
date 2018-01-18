// Copyright (c) Vidar Tonaas Fauske.
// Distributed under the terms of the Modified BSD License.

import {
  WidgetModel, ManagerBase
} from '@jupyter-widgets/base';

import {
  JUPYTER_EXTENSION_VERSION
} from './version';


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
class VtkWidget extends WidgetModel {
  defaults() {
    return {...super.defaults(),
      _model_module: VtkWidget.model_module,
      _model_module_version: VtkWidget.model_module_version,
      _view_module: VtkWidget.view_module,
      _view_module_version: VtkWidget.view_module_version,
    };
  }

  static serializers: ISerializers = {
    ...WidgetModel.serializers,
    // Add any extra serializers here
  }

  static model_module = 'jupyter-vtk-datawidgets';
  static model_module_version = JUPYTER_EXTENSION_VERSION;
  static view_module = 'jupyter-vtk-datawidgets';   // Set to null if no view
  static view_module_version = JUPYTER_EXTENSION_VERSION;
}


export
class DataArray extends VtkWidget {
  defaults() {
    return {...super.defaults(),
      _model_name: DataArray.model_name,
      name: null,
      data: null,
    };
  }

  static serializers = {
    ...VtkWidget.serializers,
    // Add any extra serializers here
  }

  static model_name = 'DataArray';
}


export
class DataContainer extends VtkWidget {
  defaults() {
    return {...super.defaults(),
      _model_name: DataContainer.model_name,
      kind: '',
      attributes: {},
      data_arrays: [],
    };
  }

  static serializers = {
    ...VtkWidget.serializers,
    // Add any extra serializers here
  }

  static model_name = 'DataContainer';
}


export
class Piece extends VtkWidget {
  defaults() {
    return {...super.defaults(),
      _model_name: Piece.model_name,
      attributes: {},
      data: [],
    };
  }

  static serializers = {
    ...VtkWidget.serializers,
    // Add any extra serializers here
  }

  static model_name = 'Piece';
}


export
class DataSet extends VtkWidget {
  defaults() {
    return {...super.defaults(),
      _model_name: Piece.model_name,
      pieces: [],
    };
  }

  static serializers = {
    ...VtkWidget.serializers,
    // Add any extra serializers here
  }

  static model_name = 'Piece';
}


export
class ImageData extends DataSet {
  defaults() {
    return {...super.defaults(),
      _model_name: ImageData.model_name,
      whole_extent: [],
      origin: [],
      spacing: [],
    };
  }

  static serializers = {
    ...VtkWidget.serializers,
    // Add any extra serializers here
  }

  static model_name = 'Piece';
}


export
class UnstructuredGrid extends DataSet {
  defaults() {
    return {...super.defaults(),
      _model_name: UnstructuredGrid.model_name,
    };
  }

  static serializers = {
    ...VtkWidget.serializers,
    // Add any extra serializers here
  }

  static model_name = 'UnstructuredGrid';
}
