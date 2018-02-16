

import {
  DOMWidgetModel, DOMWidgetView, ManagerBase
} from '@jupyter-widgets/base';

import vtkActor from 'vtk.js/Sources/Rendering/Core/Actor';
import vtkColorMaps from 'vtk.js/Sources/Rendering/Core/ColorTransferFunction/ColorMaps';
import vtkColorTransferFunction from 'vtk.js/Sources/Rendering/Core/ColorTransferFunction';
import vtkGenericRenderWindow from 'vtk.js/Sources/Rendering/Misc/GenericRenderWindow';
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



class VTKRendererModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      name: '',
      dataset: null,
      background: [0, 0, 0],
    }
  }
}



class VTKRendererView extends DOMWidgetView {

  initialize(parameters) {
    super.initialize(parameters);
  }

  // ----------------------------------------------------------------------------

  /**
   * 
   */
  render() {
    createViewer();
    createPipeline(this.model.name, this.model.dataset);
    updateCamera(renderer.getActiveCamera());
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
    this.renderWindow = vtkGenericRenderWindow.newInstance({
      background: this.model.background,
      container: this.el,
    });
    this.renderWindow.getInteractor().setDesiredUpdateRate(15);
    this.renderer = this.renderWindow.getRenderer();

    fullScreenRenderer.setResizeCallback(fpsMonitor.update);
  }

  // camera
  updateCamera(camera) {
    ['zoom', 'pitch', 'elevation', 'yaw', 'azimuth', 'roll', 'dolly'].forEach(
      (key) => {
        if (userParams[key]) {
          camera[key](userParams[key]);
        }
        this.renderWindow.render();
      }
    );
  }

  createPipeline(name, dataset) {
    // VTK pipeline
    const vtuReader = vtkXMLUnstructuredGridReader.newInstance();
    vtpReade
    vtpReader.parseAsArrayBuffer(fileContents);

    const lookupTable = vtkColorTransferFunction.newInstance();
    const source = vtpReader.getOutputData(0);
    const mapper = vtkMapper.newInstance({
      interpolateScalarsBeforeMapping: false,
      useLookupTableScalarRange: true,
      lookupTable,
      scalarVisibility: false,
    });
    const actor = vtkActor.newInstance();
    const scalars = source.getPointData().getScalars();
    const dataRange = [].concat(scalars ? scalars.getRange() : [0, 1]);


    // --------------------------------------------------------------------
    // Pipeline handling
    // --------------------------------------------------------------------

    actor.setMapper(mapper);
    mapper.setInputData(source);
    renderer.addActor(actor);

    // Manage update when lookupTable change
    lookupTable.onModified(() => {
      renderWindow.render();
    });

    // First render
    renderer.resetCamera();
    renderWindow.render();

    global.pipeline[fileName] = {
      actor,
      mapper,
      source,
      lookupTable,
      renderer,
      renderWindow,
    };

    // Update stats
    fpsMonitor.update();
  }


}
