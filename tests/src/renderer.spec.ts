// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import expect = require('expect.js');

import * as ndarray from 'ndarray';

import {
  createTestModel, DummyManager
} from './utils.spec';

import {
  VtkRendererModel, DataArrayModel, DataContainerModel, MutableDataSetModel, VtkRendererView
} from '../../src'


describe('Renderer widget', () => {

  describe('VtkRendererModel', () => {

    it('should be createable', () => {
      let model = createTestModel(VtkRendererModel);
      expect(model).to.be.an(VtkRendererModel);
      expect(model.get('background')).to.eql([0, 0, 0]);
      expect(model.get('dataset')).to.be(undefined);
      expect(model.get('size')).to.eql([600, 400]);
    });

    it('should be createable with a state', () => {
      let da = createTestModel(DataArrayModel, {
        data: ndarray([1, 2, 3]),
        name: 'testName' });
      let dc = createTestModel(DataContainerModel, {
        kind: 'TestData',
        attributes: { foo: 'bar' },
        data_arrays: [da],
      })
      let ds = createTestModel(MutableDataSetModel, {
        kind: 'TestDataModel',
        metadata: { alice: 'bob' },
        containers: [dc],
      })
      let model = createTestModel(VtkRendererModel, {
        background: [1, 1, 1],
        size: [1024, 512],
        dataset: ds,
      });
      expect(model).to.be.an(VtkRendererModel);
      expect(model.get('background')).to.eql([1, 1, 1]);
      expect(model.get('size')).to.eql([1024, 512]);
      expect(model.get('dataset')).to.be(ds);
    });

  });

  describe('VtkRendererView', () => {

    it('should be createable with a state', () => {
      let manager = new DummyManager();
      manager.testClasses.VtkRendererView = VtkRendererView;
      let dpolys = createTestModel(DataArrayModel, {
        data: ndarray([1, 2, 3]),
        name: 'cells'
      }, manager);
      let dpoints = createTestModel(DataArrayModel, {
        data: ndarray([1, 2, 3]),
        name: 'cells'
      }, manager);
      let ds = createTestModel(MutableDataSetModel, {
        kind: 'vtkPolyData',
        metadata: {},
        containers: [
          createTestModel(DataContainerModel, {
            kind: 'Points',
            data_arrays: [dpoints],
          }, manager),
          createTestModel(DataContainerModel, {
            kind: 'Polys',
            data_arrays: [dpolys],
          }, manager)
        ],
      }, manager);
      let model = createTestModel(VtkRendererModel, {
        background: [1, 1, 1],
        size: [1024, 512],
        dataset: ds,
      }, manager);

      const viewPromise = model.widget_manager.create_view(model);
      return viewPromise.then((view) => {
        expect(view).to.be.a(VtkRendererView);
        return model.widget_manager.display_view(null as any, view, null);
      }).then((node: HTMLElement) => {
        const canvas = node.children[0].children[0];
        expect(canvas.tagName.toLowerCase()).to.be('canvas');
        expect(canvas.getAttribute('width')).to.eql(1024);
        expect(canvas.getAttribute('height')).to.eql(512);
      });
    });

  });

});
