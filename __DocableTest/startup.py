"""Example of IronPython script to be executed by pyRevit on extension load

The script filename must end in startup.py

To Test:
- rename file to startup.py
- reload pyRevit: pyRevit will run this script after successfully
  created the DLL for the extension.

pyRevit runs the startup script in a dedicated IronPython engine and output
window. Thus the startup script is isolated and can not hurt the load process.
All errors will be printed to the dedicated output window similar to the way
errors are printed from pyRevit commands.
"""
#pylint: disable=import-error,invalid-name,broad-except,superfluous-parens
#pylint: disable=unused-import,wrong-import-position,unused-argument
#pylint: disable=missing-docstring
import sys
import time
import os.path as op

from pyrevit import HOST_APP, framework
from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit import routes
from pyrevit.compat import get_elementid_value_func


# add your module paths to the sys.path here
# sys.path.append(r'path/to/your/module')

print('Startup script execution test.')
print('\n'.join(sys.path))

# test imports from same directory and exensions lib
import startuplibimport
print('lib/ import works in startup.py')


# test code for creating event handlers =======================================
# define event handler
def docopen_eventhandler(sender, args):
    forms.alert('Document Opened: {}'.format(args.PathName))

# add to DocumentOpening
# type is EventHandler[DocumentOpeningEventArgs] so create that correctly
HOST_APP.app.DocumentOpening += \
    framework.EventHandler[DB.Events.DocumentOpeningEventArgs](
        docopen_eventhandler
        )


# test code routes module =====================================================

api = routes.API("pyrevit-dev")


@api.route('/forms-block', methods=['POST'])
def forms_blocking(doc):
    """Test blocking GUI"""
    forms.alert("Routes works!")
    return 'Routes works!'


@api.route('/doc')
def get_doc(doc):
    """Test API access: get active document title"""
    return {
        "title": doc.Title if doc else ""
    }


@api.route('/doors/')
def get_doors(uiapp):
    """Test API access: find doors in active model"""
    time.sleep(3)
    doors = revit.query.get_elements_by_categories(
        [DB.BuiltInCategory.OST_Doors]
        )
    get_elementid_value = get_elementid_value_func()
    doors_data = [get_elementid_value(x.Id) for x in doors]
    return routes.make_response(
        data=doors_data,
        headers={"pyRevit": "v4.6.7"}
        )


@api.route('/except')
def raise_except():
    """Test handler exception"""
    m = 12 / 0 #pylint: disable=unused-variable


@api.route('/reflect', methods=['POST'])
def reflect_request(request):
    return {
        "path": request.path,
        "method": request.method,
        "data": request.data
    }


@api.route('/posts/<int:uiapp>')
def invalid_pattern():
    # this must throw an error in routes
    pass


@api.route('/posts/<int:pid>')
def post_id(request, pid):
    return {
        "path": request.path,
        "method": request.method,
        "data": {
            "post_id": pid,
            "post_id_type": type(pid).__name__
        }
    }


@api.route('/posts/<uuid:pid>')
def post_uuid(request, pid):
    return {
        "path": request.path,
        "method": request.method,
        "data": {
            "post_id": str(pid),
            "post_id_type": type(pid).__name__
        }
    }

@api.route('/archive/<int:year>/<int:month>/<int:day>/posts/<int:pid>')
def post_date_id(request, year, month, day, pid):
    return {
        "path": request.path,
        "method": request.method,
        "data": {
            "date": '{}/{}/{}'.format(year, month, day),
            "post_id": pid,
            "post_id_type": type(pid).__name__
        }
    }


# test dockable panel =========================================================

# class DockableExample(forms.WPFPanel):
#     panel_title = "pyRevit Dockable Panel Title"
#     panel_id = "3110e336-f81c-4927-87da-4e0d30d4d64a"
#     panel_source = op.join(op.dirname(__file__), "DockableExample.xaml")

#     def do_something(self, sender, args):
#         forms.alert("Voila!!!")


# if not forms.is_registered_dockable_panel(DockableExample):
#     forms.register_dockable_panel(DockableExample)
# else:
#     print("Skipped registering dockable pane. Already exists.")