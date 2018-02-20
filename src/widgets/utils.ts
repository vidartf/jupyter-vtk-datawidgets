
import {
  WidgetModel
} from '@jupyter-widgets/base';
import { Widget } from '@phosphor/widgets';


type NestedContainer = NestedObject | NestedArray;
type NestedValue = WidgetModel | NestedContainer;

interface NestedObject {
    [key: string]: NestedValue;
}

interface NestedArray extends Array<NestedValue> { }



/**
 * Helper function for listening to child models in lists/dicts
 *
 * @param {WidgetModel} model The parent model
 * @param {string[]} propNames The propetry names that are lists/dicts
 * @param {Function} callback The callback to call when child changes
 */
export
function listenNested(model: WidgetModel, propNames: string[], callback: (model: WidgetModel, options: any) => void) {
  for (let propName of propNames) {
    // listen to current values in array
    var curr = model.get(propName) || [];
    // ignore WidgetModels in order to support properties
    // that are either an instance, or a sequence of instances:
    if (curr instanceof WidgetModel) {
      return;
    }
    for (let childModel of childModelsNested(curr)) {
      model.listenTo(childModel, 'change', callback);
      model.listenTo(childModel, 'childchange', callback);
    }

    // make sure to (un)hook listeners when array changes
    model.on('change:' + propName, (model: WidgetModel, value: NestedContainer) => {
      var prev = model.previous(propName) || [];
      var curr = value || [];

      var diff = nestedDiff(curr, prev);
      if (!diff) {
        return
      }

      for (let childModel of diff.added) {
        model.listenTo(childModel, 'change', callback);
        model.listenTo(childModel, 'childchange', callback);
      }
      for (let childModel of diff.removed) {
        model.stopListening(childModel);
      }
    });
  }
}

/**
 * Gets the child models of an arbitrarily nested combination of
 * arrays an dicts (hash maps).
 *
 * @param {any} obj nested array/dict structure with WidgetModels as leaf nodes.
 * @returns The child models
 */
function childModelsNested(obj: NestedContainer): WidgetModel[] {
  var children;
  if (Array.isArray(obj)) {
    children = obj;
  } else {
    children = Object.keys(obj).map(function(childModelKey) {
      return obj[childModelKey];
    });
  }
  if (children.length === 0) {
    return [];
  }
  if (children[0] instanceof WidgetModel) {
    // Bottom level (children are leaf nodes)
    return children as WidgetModel[];
  }
  return [].concat.apply([], children.map(   // flatten
    (child) => childModelsNested(child as NestedContainer)
  ));
}


/**
 * Get the diff of two arbitrarily nested combinations of
 * arrays and dicts (hash maps).
 *
 * Note: This function assumes the structure of both are the same,
 * i.e. they both have the same type at the same nesting level.
 *
 * @param {ModelContainer} newObj
 * @param {ModelContainer} oldObj
 * @returns An object with three attributes 'added', 'removed' and 'kept',
 *          each an array of child models;
 */
function nestedDiff(newObj: NestedContainer, oldObj: NestedContainer) {
  var diff;
  if (Array.isArray(newObj)) {
    diff = arrayDiff(newObj, oldObj as NestedArray);
  } else {
    diff = dictDiff(newObj, oldObj as NestedObject);
  }
  var all = [...diff.added, ...diff.removed, ...diff.kept];
  if (all.length === 0) {
    return null;
  }
  if (all[0] instanceof WidgetModel) {
    // Bottom level
    return diff;
  }
  var ret = {
    added: childModelsNested(diff.added),
    removed: childModelsNested(diff.removed),
  };
  return ret;
}

/**
 * Get the diff of two array.
 *
 * @param {WidgetModel[]} newArray
 * @param {WidgetModel[]} oldArray
 * @returns An object with three attributes 'added', 'removed' and 'kept',
 *          each an array of child values;
 */
function arrayDiff<T>(newArray: T[], oldArray: T[]) {
  var added = newArray.filter(e => oldArray.indexOf(e) === -1);
  var removed = oldArray.filter(e => newArray.indexOf(e) === -1);
  var kept = oldArray.filter(e => newArray.indexOf(e) !== -1);
  return {added, removed, kept};
}

/**
 * Get the diff of two dicts (hash maps).
 *
 * @param {ModelDict} newDict
 * @param {ModelDict} oldDict
 * @returns An object with three attributes 'added', 'removed' and 'kept',
 *          each an array of child values;
 */
function dictDiff<T>(newDict: {[key: string]: T}, oldDict: {[key: string]: T}) {
  var newKeys = Object.keys(newDict);
  var oldKeys = Object.keys(oldDict);

  var added = newKeys.filter(e => oldKeys.indexOf(e) === -1).map(function(key) { return newDict[key]; });
  var removed = oldKeys.filter(e => newKeys.indexOf(e) === -1).map(function(key) { return oldDict[key]; });
  var kept = oldKeys.filter(e => newKeys.indexOf(e) !== -1).map(function(key) { return newDict[key]; });
  return {added, removed, kept};
}
