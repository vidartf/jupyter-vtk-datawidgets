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

});
