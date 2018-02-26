// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import expect = require('expect.js');

import * as ndarray from 'ndarray';

import {
  createTestModel
} from './utils.spec';

import {
  DataArrayModel, DataContainerModel, MutableDataSetModel
} from '../../src'


describe('Data widgets', () => {

  describe('DataArrayModel', () => {

    it('should be createable', () => {
      let model = createTestModel(DataArrayModel);
      expect(model).to.be.an(DataArrayModel);
      expect(model.get('data')).to.be(undefined);
      expect(model.get('name')).to.be(null);
    });

    it('should be createable with a state', () => {
      let state = { data: ndarray([1, 2, 3]), name: 'testName' }
      let model = createTestModel(DataArrayModel, state);
      expect(model).to.be.an(DataArrayModel);
      expect(model.get('data')).to.not.be(undefined);
      expect(model.get('name')).to.be('testName');
    });

  });

  describe('DataContainerModel', () => {

    it('should be createable', () => {
      let model = createTestModel(DataContainerModel);
      expect(model).to.be.an(DataContainerModel);
      expect(model.get('kind')).to.be(undefined);
      expect(model.get('attributes')).to.be(undefined);
      expect(model.get('data_arrays')).to.be(undefined);
    });

    it('should be createable with a state', () => {
      let da = createTestModel(DataArrayModel, {
        data: ndarray([1, 2, 3]),
        name: 'testName' });
      let model = createTestModel(DataContainerModel, {
        kind: 'TestData',
        attributes: { foo: 'bar' },
        data_arrays: [da],
      });
      expect(model).to.be.an(DataContainerModel);
      expect(model.get('kind')).to.be('TestData');
      expect(model.get('attributes')).to.eql({foo: 'bar'});
      expect(model.get('data_arrays')).to.eql([da]);
    });

  });

  describe('MutableDataSetModel', () => {

    it('should be createable', () => {
      let model = createTestModel(MutableDataSetModel);
      expect(model).to.be.an(MutableDataSetModel);
      expect(model.get('kind')).to.be(undefined);
      expect(model.get('metadata')).to.be(undefined);
      expect(model.get('containers')).to.be(undefined);
    });

    it('should be createable with a state', () => {
      let da = createTestModel(DataArrayModel, {
        data: ndarray([1, 2, 3]),
        name: 'testName' });
      let dc = createTestModel(DataContainerModel, {
        kind: 'TestData',
        attributes: { foo: 'bar' },
        data_arrays: [da],
      });
      let model = createTestModel(MutableDataSetModel, {
        kind: 'TestDataModel',
        metadata: { alice: 'bob' },
        containers: [dc],
      });
      expect(model).to.be.an(MutableDataSetModel);
      expect(model.get('kind')).to.be('TestDataModel');
      expect(model.get('metadata')).to.eql({alice: 'bob'});
      expect(model.get('containers')).to.eql([dc]);
    });

    it('should fire a change event if attribute changes', () => {
      let model = createTestModel(MutableDataSetModel, {
        kind: 'TestDataModel',
        metadata: { alice: 'bob' },
        containers: [],
      });

      let triggered = false;
      model.on('change', () => { triggered = true; });
      expect(triggered).to.be(false);
      model.set({kind: 'OtherDataModel'});
      expect(triggered).to.be(true);
    });

    it('should fire a change event if data container is reassigned', () => {
      let da = createTestModel(DataArrayModel, {
        data: ndarray([1, 2, 3]),
        name: 'testName' });
      let dc = createTestModel(DataContainerModel, {
        kind: 'TestData',
        attributes: { foo: 'bar' },
        data_arrays: [da],
      });
      let model = createTestModel(MutableDataSetModel, {
        kind: 'TestDataModel',
        metadata: { alice: 'bob' },
        containers: [dc],
      });
      let dc2 = createTestModel(DataContainerModel, {
        kind: 'TestData',
        metadata: { dog: 'food' },
        data_arrays: [],
      });

      let triggered = false;
      model.on('change', () => { triggered = true; });
      expect(triggered).to.be(false);
      model.set({containers: [dc2]});
      expect(triggered).to.be(true);
    });

    it('should fire a childchange event of reassigned data container', () => {
      let da = createTestModel(DataArrayModel, {
        data: ndarray([1, 2, 3]),
        name: 'testName' });
      let dc = createTestModel(DataContainerModel, {
        kind: 'TestData',
        attributes: { foo: 'bar' },
        data_arrays: [da],
      });
      let model = createTestModel(MutableDataSetModel, {
        kind: 'TestDataModel',
        metadata: { alice: 'bob' },
        containers: [dc],
      });
      let dc2 = createTestModel(DataContainerModel, {
        kind: 'TestData',
        metadata: { dog: 'food' },
        data_arrays: [],
      });

      let triggered = false;
      model.on('childchange', () => { triggered = true; });
      model.set({containers: [dc2]});

      expect(triggered).to.be(false);
      dc2.set({kind: 'OtherData'});
      expect(triggered).to.be(true);
    });

    it('should fire a childchange event if data container changes', () => {
      let da = createTestModel(DataArrayModel, {
        data: ndarray([1, 2, 3]),
        name: 'testName' });
      let dc = createTestModel(DataContainerModel, {
        kind: 'TestData',
        attributes: { foo: 'bar' },
        data_arrays: [da],
      });
      let model = createTestModel(MutableDataSetModel, {
        kind: 'TestDataModel',
        metadata: { alice: 'bob' },
        containers: [dc],
      });

      let triggered = false;
      model.on('childchange', () => { triggered = true; });
      expect(triggered).to.be(false);
      dc.set({kind: 'OtherData'});
      expect(triggered).to.be(true);
    });

    it('should fire a childchange event if data array changes', () => {
      let da = createTestModel(DataArrayModel, {
        data: ndarray([1, 2, 3]),
        name: 'testName' });
      let dc = createTestModel(DataContainerModel, {
        kind: 'TestData',
        attributes: { foo: 'bar' },
        data_arrays: [da],
      });
      let model = createTestModel(MutableDataSetModel, {
        kind: 'TestDataModel',
        metadata: { alice: 'bob' },
        containers: [dc],
      });

      let triggered = false;
      model.on('childchange', () => { triggered = true; });
      expect(triggered).to.be(false);
      da.set({name: 'changedName'});
      expect(triggered).to.be(true);
    });

  });

});
