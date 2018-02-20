
import {
  DOMWidgetModel, DOMWidgetView, ManagerBase
} from '@jupyter-widgets/base';

import vtkActor from 'vtk.js/Sources/Rendering/Core/Actor';
import vtkColorMaps from 'vtk.js/Sources/Rendering/Core/ColorTransferFunction/ColorMaps';
import vtkColorTransferFunction from 'vtk.js/Sources/Rendering/Core/ColorTransferFunction';
import vtkOpenGLRenderWindow from 'vtk.js/Sources/Rendering/OpenGL/RenderWindow';
import vtkRenderWindow from 'vtk.js/Sources/Rendering/Core/RenderWindow';
import vtkRenderWindowInteractor from 'vtk.js/Sources/Rendering/Core/RenderWindowInteractor';
import vtkRenderer from 'vtk.js/Sources/Rendering/Core/Renderer';
import vtkMapper from 'vtk.js/Sources/Rendering/Core/Mapper';

// Data sets:
import vtkPolyData from 'vtk.js/Sources/Common/DataModel/PolyData';
import vtkImageData from 'vtk.js/Sources/Common/DataModel/ImageData';
// import vtkRectilinearGrid from 'vtk.js/Sources/Common/DataModel/vtkRectilinearGrid';
// import vtkStructuredGrid from 'vtk.js/Sources/Common/DataModel/StructuredGrid';
// import vtkUnstructuredGrid from 'vtk.js/Sources/Common/DataModel/UnstructuredGrid';


import {
  ColorMode,
  ScalarMode,
} from 'vtk.js/Sources/Rendering/Core/Mapper/Constants';


import {
  VtkRendererModel as VtkRendererModelBase
} from './gen';

import vtkJupyterBridge from './vtk_binding';



export
class VtkRendererModel extends VtkRendererModelBase {
  initialize() {
    super.initialize(...arguments);
    this.wrapper = vtkJupyterBridge.newInstance({widget: this});
  }
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
    this.updateCamera(this.renderer.getActiveCamera());
  }

  /**
   * 
   */
  update() {
    // TODO: Map model to renderer properties
    // - name, dataset -> recreate pipeline
    // - background -> set on renderer
    // - camera position -> update camera
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

    //const lookupTable = vtkColorTransferFunction.newInstance();
    const source = dataset.getOutputPort();
    const mapper = vtkMapper.newInstance(); /*{
      interpolateScalarsBeforeMapping: false,
      useLookupTableScalarRange: true,
      lookupTable,
      scalarVisibility: false,
    });*/
    mapper.setInputConnection(source);

    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);

    this.renderer.addActor(actor);

    // Manage update when lookupTable change
    /*lookupTable.onModified(() => {
      this.renderWindow.render();
    });*/

    // First render
    this.renderer.resetCamera();
    this.renderWindow.render();
  }

  // camera
  updateCamera(camera) {
    /*['zoom', 'pitch', 'elevation', 'yaw', 'azimuth', 'roll', 'dolly'].forEach(
      (key) => {
        this.renderWindow.render();
      }
    );*/
  }
}



