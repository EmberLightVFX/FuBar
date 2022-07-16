global _thisapp, app, bmd, comp, composition, fu, fusion

name = "Nodes"
description = "Searches for all nodes in Fusion"


def init(globs):
    global _thisapp, app, bmd, comp, composition, fu, fusion

    _thisapp = globs["_thisapp"]
    app = globs["app"]
    bmd = globs["bmd"]
    comp = globs["comp"]
    composition = globs["composition"]
    fu = globs["fu"]
    fusion = globs["fusion"]


def search():
    print("Searching!")
    found = []
    tools = fusion.GetToolList()

    for _, category in tools.items():
        for _, tool in category.items():
            OpIconString = ""
            try:
                OpIconString = " (" + \
                    fusion.GetRegAttrs(tool["ID"])["REGS_OpIconString"] + ")"
            except:
                pass

            name = tool["Name"] + OpIconString
            found.append({
                'Name': name,
                'ID': tool["ID"],
            })
    return found


def execute(node):
    print("Placing node")
    comp.AddTool(node, 32768, -32768)
