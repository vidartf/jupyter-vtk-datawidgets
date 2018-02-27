var loaders = [
  { test: /\.ts$/, loader: 'ts-loader' },
  { test: /\.js$/, loader: "source-map-loader" },
];

var webpack = require('webpack');
var vtkRules = require('vtk.js/Utilities/config/dependency.js').webpack.v2.rules;

module.exports = [
  {
    entry: './src/index.ts',
    output: {
      filename: 'index.js',
      path: __dirname + '/vtkdatawidgets/nbextension/static',
      libraryTarget: 'amd'
    },
    module: {
      rules: loaders.concat(vtkRules),
    },
    devtool: 'source-map',
    externals: ['@jupyter-widgets/base'],
    resolve: {
      // Add '.ts' and '.tsx' as resolvable extensions.
      extensions: [".webpack.js", ".web.js", ".ts", ".js"]
    },
  },

  {
    // embeddable bundle (e.g. for docs)
    entry: './src/index.ts',
    output: {
      filename: 'embed-bundle.js',
      path: __dirname + '/docs/source/_static',
      library: "jupyter-vtk-datawidgets",
      libraryTarget: 'amd'
    },
    module: {
      rules: loaders.concat(vtkRules),
    },
    devtool: 'source-map',
    externals: ['@jupyter-widgets/base'],
    resolve: {
      // Add '.ts' and '.tsx' as resolvable extensions.
      extensions: [".webpack.js", ".web.js", ".ts", ".js"]
    },
  },

];
