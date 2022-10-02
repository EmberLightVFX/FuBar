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
            attrs = fusion.GetRegAttrs(tool["ID"])
            OpIconString = ""
            Description = ""
            try:
                OpIconString = " (" + \
                    attrs["REGS_OpIconString"] + ")"
            except:
                pass
            try:
                Description = attrs['REGS_OpDescription']
            except:
                pass

            name = attrs["REGS_Name"] + OpIconString
            found.append({
                'ViewName': name,
                'Name': attrs['REGS_Name'],
                'ID': attrs['REGS_ID'],
                'OpString': OpIconString,
                'Category': attrs['REGS_Category'],
                'Description': Description,
            })
    return found


def execute(node):
    print("Placing node")
    comp.AddTool(node, 32768, -32768)
