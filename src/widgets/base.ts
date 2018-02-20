
import {
  WidgetModel, DOMWidgetModel,
  WidgetView, DOMWidgetView,
  unpack_models
} from '@jupyter-widgets/base';

import {
  listenToUnion, data_union_serialization, array_serialization
} from 'jupyter-dataserializers';

import {
  JUPYTER_EXTENSION_VERSION
} from '../version';

import {
  listenNested
} from './utils';



export
class VtkWidgetModel extends WidgetModel {

  defaults() {
    return {...super.defaults(), ...{
      _model_module: "jupyter-vtk-datawidgets",
      _model_module_version: JUPYTER_EXTENSION_VERSION,
      _view_module: "jupyter-vtk-datawidgets",
      _view_module_version: JUPYTER_EXTENSION_VERSION,
    }}
  }

  initialize(attributes: any, options: {model_id: string; comm?: any; widget_manager: any;}) {
    super.initialize(attributes, options);
    this.setupNestedKeys();
    this.setupListeners();
  }

  onChange(model: VtkWidgetModel, options: any) {
  }

  onChildChanged(model: VtkWidgetModel, options: any) {
      console.debug('child changed: ' + model.model_id);
      // Propagate up hierarchy:
      this.trigger('childchange', this);
  }

  setupListeners() {
    // Handle changes in directly nested widgets:
    for (let [key, value] of this.pairs()) {
      if (!(value instanceof VtkWidgetModel)) {
        continue;
      }
      // register listener for current child value
      var curValue = this.get(key);
      if (curValue) {
          this.listenTo(curValue, 'change', this.onChildChanged.bind(this));
          this.listenTo(curValue, 'childchange', this.onChildChanged.bind(this));
      }

      // make sure to (un)hook listeners when child points to new object
      this.on('change:' + key, function(model: VtkWidgetModel, value: VtkWidgetModel) {
          var prevModel = this.previous(key);
          var currModel = value;
          if (prevModel) {
              this.stopListening(prevModel);
          }
          if (currModel) {
              this.listenTo(currModel, 'change', this.onChildChanged.bind(this));
              this.listenTo(currModel, 'childchange', this.onChildChanged.bind(this));
          }
      }, this);
    }

    // Handle changes in three instance nested props (arrays/dicts, possibly nested)
    listenNested(this, this.nestedKeys, this.onChildChanged.bind(this));

    // Handle changes in data widgets/union properties
    for (let propName of this.dataWidgetKeys) {
        listenToUnion(this, propName, this.onChildChanged.bind(this), false);
    }

    this.on('change', this.onChange, this);

  }

  setupNestedKeys() {
    this.nestedKeys = [];
    this.dataWidgetKeys = [];
    for (let [key, value] of this.pairs()) {
      if (value instanceof VtkWidgetModel) {
        continue;
      }
      const serializers = (this.constructor as typeof VtkWidgetModel).serializers || {};
      const serializer = serializers[key];
      if (!serializer) {
        continue;
      }
      if (serializer === {deserialize: unpack_models}) {
        // There's a widget serializer, but it is not a direct ref
        // Should be nested widget then
        this.nestedKeys.push(key);
      } else if (serializer === data_union_serialization || serializer === array_serialization) {
        this.dataWidgetKeys.push(key);
      }
    }
  }

  nestedKeys: string[];
  dataWidgetKeys: string[];

}