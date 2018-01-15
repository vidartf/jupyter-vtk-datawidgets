define(function() {
    "use strict";

    window['requirejs'].config({
        map: {
            '*': {
                'jupyter-vtk-datawidgets': 'nbextensions/jupyter-vtk-datawidgets/index',
            },
        }
    });
    // Export the required load_ipython_extention
    return {
        load_ipython_extension : function() {}
    };
});
