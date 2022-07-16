"""

ToDo:
* Search all tools
    * Tools
    * Search with short-name
    * Macros
    * Add to node viewer
* Search scripts
* Add weights to search
* Check if selected tool is 2D or 3D tool. If 3D, add extra weight to all 3D nodes, same to 2D tools. (REGS_Category)
* Add shotcut names to the nodes name in the list
* Add console-scripts
* Add args-posibility to nodes.
    * Check if there is any modules for picked node. If so, apply module.
* Add menu
    * Pick where to save weights
    * Add custom scripts folder
    * Select what modules you want to use
* Add images to the nodes like in the original search bar (fusion.GetToolIcon("Loader"))

40px high (SizeHint)

"""

# ========================== Globals ============================ #
from pprint import pprint
import os
import sys
import pkgutil

DEBUG = False

comp = fu.GetCurrentComp()
ui = fu.UIManager
disp = bmd.UIDispatcher(ui)
fuBarFolder = os.path.join(os.path.dirname(
    os.path.abspath(sys.argv[0])), "FuBar")
modules = []
searchList = []
maxItems = 20

globs = {
    "_thisapp": _thisapp,
    "app": app,
    "bmd": bmd,
    "comp": comp,
    "composition": composition,
    "fu": fu,
    "fusion": fusion
}


# ========================== Functions ============================ #

def AddModules():
    moduleFolder = os.path.normpath(os.path.join(fuBarFolder, "Modules"))
    for package in pkgutil.iter_modules([moduleFolder]):
        finder, name, ispkg = package
        spec = finder.find_spec(name)
        module = spec.loader.load_module(name)
        module.init(globs)
        modules.append(module)


def get_all_tree_items(tree):
    return tree.FindItems("*",
                          {
                              "MatchExactly": False,
                              "MatchFixedString": False,
                              "MatchContains": False,
                              "MatchStartsWith": False,
                              "MatchEndsWith": False,
                              "MatchCaseSensitive": False,
                              "MatchRegExp": False,
                              "MatchWildcard": True,
                              "MatchWrap": False,
                              "MatchRecursive": True,
                          }, 0)


def selectTree(tree, amount):
    treeItems = get_all_tree_items(tree)
    selectedIndex = 0
    for i, item in treeItems.items():
        if item.Selected:
            selectedIndex = i
            item.Selected = False
            break
    selectedIndex = selectedIndex + amount

    if selectedIndex <= 0:
        treeItems[len(treeItems)].Selected = True
    elif selectedIndex > len(treeItems):
        treeItems[1].Selected = True
    else:
        treeItems[selectedIndex].Selected = True


# ========================== UI ============================ #

def updateTree(tree, searchText):
    tree.UpdatesEnabled = False
    tree.SortingEnabled = False

    foundItems = 0
    tree.Clear()
    for tool in searchList:
        if searchText.lower() in tool["Name"].lower():
            itRow = tree.NewItem()
            itRow.Text[0] = tool["Name"]
            itRow.Text[1] = tool["ID"]
            tree.AddTopLevelItem(itRow)
            foundItems = foundItems + 1
            if foundItems >= maxItems:
                break
    if(foundItems > 0):
        tree.SortByColumn(0, "AscendingOrder")
        tree.ItemAt(0, 0).SetSelected(True)

    tree.UpdatesEnabled = True
    tree.SortingEnabled = True


def FuBarUI():
    dlg = disp.AddWindow({
        "WindowTitle": "FuBar",
        "ID": "FuBarWin",
        "TargetID": "FuBarWin",
        "Spacing": 0,
        "WindowFlags": {
            "Window": True,
            "WindowStaysOnTopHint": True
        }
    }, [
        ui.VGroup({"ID": "root", "Weight": 10.0, }, [
            ui.Tree({
                "ID": "Tree",
                "SortingEnabled": True,
                "Events": {
                    "CurrentItemChanged": True,
                    "ItemActivated": True,
                    "ItemClicked": True,
                    "ItemDoubleClicked": True,
                },
            }),
            ui.HGroup({"ID": "search", "Weight": 0.0, }, [
                ui.LineEdit({
                    "ID": 'SearchBar',
                    "Weight": 10.0,
                    "ClearButtonEnabled": True,
                    "Events": {
                        "ReturnPressed": True,
                        "TextChanged": True,
                    },
                }),
                ui.Button({
                    "ID": 'Settings',
                    "Weight": 1.0,
                    "Text": "Settings"
                }),
            ]),
        ]),
    ])

    itm = dlg.GetItems()
    # Resize UI to nice size
    itm["FuBarWin"].UpdatesEnabled = False
    itm["FuBarWin"].Resize([430, 430])
    itm["FuBarWin"].UpdatesEnabled = True

    # The window was closed
    def _func(ev):
        try:
            if ev["key"] == "up":
                selectTree(itm["Tree"], -1)
            elif ev["key"] == "down":
                selectTree(itm["Tree"], 1)
        except:
            disp.ExitLoop()
    dlg.On.FuBarWin.Close = _func

    # Add your GUI element based event functions here:

    # Add a header row
    hdr = itm["Tree"].NewItem()

    hdr.Text[0] = "Name"
    hdr.Text[1] = "ID"
    hdr.Text[2] = "Weight"
    hdr.Text[3] = "Data1"
    hdr.Text[4] = "Data2"
    itm["Tree"].SetHeaderItem(hdr)

    # Number of columns in the Tree list
    itm["Tree"].ColumnCount = 5

    # Resize the Columns
    itm["Tree"].ColumnWidth[0] = 100
    itm["Tree"].ColumnWidth[1] = 75
    itm["Tree"].ColumnWidth[2] = 75
    itm["Tree"].ColumnWidth[3] = 75
    itm["Tree"].ColumnWidth[4] = 75
    itm["Tree"].ColumnWidth[5] = 75

    # Add an new row entries to the list
    AddModules()
    for module in modules:
        searchList.extend(module.search())
    updateTree(itm["Tree"], itm["SearchBar"].Text)

    # Set focus to search bar
    itm["SearchBar"].SetFocus()

    # When searching
    def _func(ev):
        updateTree(itm["Tree"], itm["SearchBar"].Text)
    dlg.On.SearchBar.TextChanged = _func

    # A Tree view row was clicked on
    def _func(ev):
        # Grab the name of the selected item and place in the search bar
        itm["SearchBar"].Text = ev["item"].Text[0]
    dlg.On.Tree.ItemClicked = _func

    # A Tree view row was double clicked on
    def executeItem(ev):
        # Execute clicked item
        item = None
        treeItems = get_all_tree_items(itm["Tree"]).items()

        for _, treeItem in treeItems:
            if treeItem.GetSelected():
                item = treeItem
                break
        for module in modules:
            module.execute(item.Text[1])
    dlg.On.Tree.ItemDoubleClicked = executeItem

    def _func(ev):
        executeItem(None)
        disp.ExitLoop()
    dlg.On.SearchBar.ReturnPressed = _func

    # Map ESC to close UI
    comp.Execute("""
        app:AddConfig('FuBarWin', {
            Target {
                ID = 'FuBarWin',
            },
            Hotkeys {
                Target = 'FuBarWin',
                Defaults = true,

                CONTROL_W = 'Execute{cmd = [[app.UIManager:QueueEvent(obj, "Close", {})]]}',
                CONTROL_F4 = 'Execute{cmd = [[app.UIManager:QueueEvent(obj, "Close", {})]]}',
                ESCAPE = 'Execute{cmd = [[app.UIManager:QueueEvent(obj, "Close", {})]]}',
                UP = "Execute{cmd = [[app.UIManager:QueueEvent(obj, 'Close', {key = 'up'})]]}",
                DOWN = "Execute{cmd = [[app.UIManager:QueueEvent(obj, 'Close', {key = 'down'})]]}",
            },
        })
        """)

    dlg.Show()
    disp.RunLoop()
    dlg.Hide()


if __name__ == "__main__":
    FuBarUI()
