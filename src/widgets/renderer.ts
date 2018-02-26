
import {
  DOMWidgetModel, DOMWidgetView, ManagerBase
} from '@jupyter-widgets/base';

// @ts-ignore
import vtkActor from 'vtk.js/Sources/Rendering/Core/Actor';
// @ts-ignore
import vtkOpenGLRenderWindow from 'vtk.js/Sources/Rendering/OpenGL/RenderWindow';
// @ts-ignore
import vtkRenderWindow from 'vtk.js/Sources/Rendering/Core/RenderWindow';
// @ts-ignore
import vtkRenderWindowInteractor from 'vtk.js/Sources/Rendering/Core/RenderWindowInteractor';
// @ts-ignore
import vtkRenderer from 'vtk.js/Sources/Rendering/Core/Renderer';
// @ts-ignore
import vtkMapper from 'vtk.js/Sources/Rendering/Core/Mapper';

// Data sets:
// @ts-ignore
import vtkPolyData from 'vtk.js/Sources/Common/DataModel/PolyData';
// @ts-ignore
import vtkImageData from 'vtk.js/Sources/Common/DataModel/ImageData';
// import vtkRectilinearGrid from 'vtk.js/Sources/Common/DataModel/vtkRectilinearGrid';
// import vtkStructuredGrid from 'vtk.js/Sources/Common/DataModel/StructuredGrid';
// import vtkUnstructuredGrid from 'vtk.js/Sources/Common/DataModel/UnstructuredGrid';


import {
  ColorMode,
  ScalarMode,
  // @ts-ignore
} from 'vtk.js/Sources/Rendering/Core/Mapper/Constants';


import {
  VtkRendererModel as VtkRendererModelBase
} from './gen';

import {
  VtkWidgetModel
} from './base';

import vtkJupyterBridge from './vtk_binding';


// Keep this here to prevent test from optimizing away imports
// (causes side effects!)
export
const __keepSymbols = [vtkPolyData, vtkImageData]


export
class VtkRendererModel extends VtkRendererModelBase {
  initialize(attributes: any, options: any) {
    super.initialize(attributes, options);
    this.wrapper = vtkJupyterBridge.newInstance({widget: this});

    VtkWidgetModel.prototype.setupNestedKeys.call(this);
    VtkWidgetModel.prototype.setupListeners.call(this);
  }

  onChange(model: VtkRendererModel, options: any) {
  }

  onChildChanged(model: VtkRendererModel, options: any) {
    console.debug('child changed: ' + model.model_id);
    // Propagate up hierarchy:
    this.trigger('childchange', this);
  }

  wrapper: any;
  nestedKeys = [];
  dataWidgetKeys = [];
}


export
class VtkRendererView extends DOMWidgetView {

  // ----------------------------------------------------------------------------

  /**
   * 
   */
  render() {
    this.createViewer();
    this.createPipeline();
    this.setupEventListeners();
  }

  /**
   * 
   */
  update() {
    const diff = this.model.changedAttributes();
    if (diff.background) {
      this.renderer.setBackground(diff.background);
    }
    if (diff.size !== undefined) {
      const size = this.model.get('size');
      this.openglRenderWindow.setSize(size[0], size[1]);
    }
    if (diff.dataset !== undefined) {
      // Recreate pipeline
      this.renderer.getActors().map((actor: any) => this.renderer.removeActor(actor));
      this.createPipeline();
    }
    // TODO: Map model to renderer properties
    // - camera position -> update camera
    this.renderWindow.render();
  }

  // ----------------------------------------------------------------------------

  createViewer() {
    this.renderWindow = vtkRenderWindow.newInstance();
    this.renderer = vtkRenderer.newInstance({
      background: this.model.get('background') || [0, 0, 0],
    });
    this.renderWindow.addRenderer(this.renderer);

    this.openglRenderWindow = vtkOpenGLRenderWindow.newInstance();
    this.renderWindow.addView(this.openglRenderWindow);

    this.container = document.createElement('div');
    this.el.appendChild(this.container);
    this.openglRenderWindow.setContainer(this.container);

    this.interactor = vtkRenderWindowInteractor.newInstance();
    this.interactor.setView(this.openglRenderWindow);
    this.interactor.initialize();
    this.interactor.bindEvents(this.container);

    //this.interactor.setDesiredUpdateRate(15);
    const size = this.model.get('size');
    this.openglRenderWindow.setSize(size[0], size[1]);
  }

  createPipeline() {
    // VTK pipeline
    const dataset = this.model.wrapper;

    const source = dataset.getOutputPort();
    const mapper = vtkMapper.newInstance();
    mapper.setInputConnection(source);

    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);

    this.renderer.addActor(actor);

    // First render
    this.renderer.resetCamera();
    this.renderWindow.render();
  }

  // ----------------------------------------------------------------------------
  // Ensure that re-renders are throttled to one per animation frame:

  setupEventListeners() {
    this.listenTo(this.model, 'childchange', this.tick.bind(this));
  }

  tick() {
    if (!this._ticking) {
      requestAnimationFrame(this.tock.bind(this));
      this._ticking = true;
    }
  }

  tock() {
    this._ticking = false;
    this.trigger('beforeRender');
    this.renderWindow.render();
    this.trigger('afterRender');
  }

  // ----------------------------------------------------------------------------

  model: VtkRendererModel;

  renderWindow: any;
  renderer: any;
  openglRenderWindow: any;
  interactor: any;
  container: HTMLElement;

  private _ticking = false;
}
