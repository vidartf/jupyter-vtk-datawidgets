// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import {
  Application, IPlugin
} from '@phosphor/application';

import {
  Widget
} from '@phosphor/widgets';

import {
  IJupyterWidgetRegistry, ExportMap
 } from '@jupyter-widgets/base';

import * as widgets from './widget';

import {
  JUPYTER_EXTENSION_VERSION
} from './version';


const EXTENSION_ID = 'jupyter.extensions.vtk-datawidgets';


/**
 * The example plugin.
 */
const examplePlugin: IPlugin<Application<Widget>, void> = {
  id: EXTENSION_ID,
  requires: [IJupyterWidgetRegistry],
  activate: activateWidgetExtension,
  autoStart: true
};

export default examplePlugin;


/**
 * Activate the widget extension.
 */
function activateWidgetExtension(app: Application<Widget>, registry: IJupyterWidgetRegistry): void {
  registry.registerWidget({
    name: 'jupyter-vtk-datawidgets',
    version: JUPYTER_EXTENSION_VERSION,
    exports: widgets as any as ExportMap
  });
}
