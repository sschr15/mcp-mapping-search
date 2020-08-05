from urllib import request
from sys import argv
import typing, glob, json, os, zipfile, time

def getFileFromUrl(url: str, encoding="utf-8", lines=False) -> typing.Union[str, typing.List[str]]:
    file = request.urlopen(url)
    data = str(file.read(), encoding)
    return data.split("\n") if lines else data

def getBytesFromUrl(url: str) -> bytes:
    file = request.urlopen(url)
    return file.read()

if len(argv) > 1:
    mapping = argv[1]
else:
    mapping = "stable_39"

_example = ["12345", "ab", "mcpname"]

FIELDS = []
METHODS = []
PARAMS = []
CLASSES = []

os.makedirs("csv", exist_ok=True) # make csv directory if it doesn't exist

loc = f'csv/{mapping}/'

g = glob.glob("csv/*")
if mapping == "latest":
    os.makedirs("csv/latest", exist_ok=True)
    with open(loc + "fields.csv", "w") as file:
        file.write(getFileFromUrl("http://export.mcpbot.bspk.rs/fields.csv").replace("\r\n", "\n"))
    with open(loc + "methods.csv", "w") as file:
        file.write(getFileFromUrl("http://export.mcpbot.bspk.rs/methods.csv").replace("\r\n", "\n"))
    with open(loc + "params.csv", "w") as file:
        file.write(getFileFromUrl("http://export.mcpbot.bspk.rs/params.csv").replace("\r\n", "\n"))
elif "csv\\" + mapping not in g:
    # get correct location on mcpbot exports
    json_str = getFileFromUrl("http://export.mcpbot.bspk.rs/versions.json")
    open("versions.json", "w").write(f'{"{"}"update-time":{time.time()}' + json_str[1:])
    data = json.loads(json_str)

    mappingType = mapping.split("_") # "stable_39" -> ["stable", "39"]

    for i in data:
        if mappingType[1] in str(data[i][mappingType[0]]):
            break
    
    zipFile = getBytesFromUrl(f'http://export.mcpbot.bspk.rs/mcp_{mappingType[0]}/{mappingType[1]}-{i}/mcp_{mappingType[0]}-{mappingType[1]}-{i}.zip')
    open(f'mcp_{mappingType[0]}-{mappingType[1]}-{i}.zip', "wb").write(zipFile)

    with zipfile.ZipFile(f'mcp_{mappingType[0]}-{mappingType[1]}-{i}.zip') as zfile:
        zfile.extractall(f'csv/{mapping}')
    os.remove(f'mcp_{mappingType[0]}-{mappingType[1]}-{i}.zip')

try: # init: setting up the above three lists
    with open(loc + "fields.csv") as file:
        iteration = [0, 0]
        contents = file.read().split("\n")
        for i in contents[1:-1]:
            iteration[1] += 1
            line = i.split(",")
            _ = line[0].split("_")
            field = [_[1], _[2], line[1], ",".join(line[3:]).replace("\\n \\n", "\n")]
            FIELDS.append(field)

    with open(loc + "methods.csv") as file:
        iteration = [1, 0]
        contents = file.read().split("\n")
        for i in contents[1:-1]:
            iteration[1] += 1
            line = i.split(",")
            _ = line[0].split("_")
            method = [_[1], _[2], line[1], ",".join(line[3:]).replace("\\n \\n", "\n")]
            METHODS.append(method)

    with open(loc + "params.csv") as file:
        iteration = [2, 0]
        contents = file.read().split("\n")
        for i in contents[1:-1]:
            iteration[1] += 1
            line = i.split(",")
            a = line[0].split("_")
            param = [a[1], a[2], line[1]]
            PARAMS.append(param)
except BaseException as e:
    print(iteration, e)
    os._exit(1)
else:
    try:
        with open(loc + "classes.csv") as file:
            contents = file.read().split("\n")
        for i in contents[1:-1]:
            line = i.split(",")
            a = line[0].split("_")
            _class = [a[1], a[2], line[1], ",".join(line[2:])]
            CLASSES.append(_class)
    except OSError:
        CLASSES = []  # no classes accessible, making sure the list is empty

try:
    print("MCP Method Identifier    Mapping:", mapping)
    print("m   methods (functions) \nf   fields \np   parameters", "\nc   classes" if CLASSES else "", "\nh   show this \nPress CTRL+C to exit")
    while True:
        result = False
        txt = input("> ")
        if len(txt) < 2: txt = "invalid query"
        prompt = txt[2:].lower()
        if txt.lower().strip() == "h":
            result = True
            print("m   methods (functions) \nf   fields \np   parameters \nh   show this \nPress CTRL+C to exit")
        elif txt[1] != " ":
            result = True
            print("Invalid query!")
        elif txt[0] in "mf":
            for a in prompt.split(" "):
                if txt[0].lower() == "m":
                    for i in METHODS:
                        if a in [m.lower() for m in i]:
                            result = True
                            print(" ".join(i[:3]) + "\n" + i[3])
                elif txt[0].lower() == "f":
                    for i in FIELDS:
                        if a in [m.lower() for m in i]:
                            result = True
                            print(" ".join(i[:3]) + "\n" + i[3])
        elif txt[0].lower() == "p":
            desc = ""
            a = False
            if prompt.isdigit():
                for i in METHODS:
                    if prompt == i[0]:
                        result = True
                        print(i[2], end="(")
                        desc = i[3]
            for i in PARAMS:
                if prompt == i[0]:
                    result = True
                    a = True
                    print(i[2], end=", ")
            if result: print("\b\b)" if a else ")", "\n" + desc)
        elif txt[0].lower() == "c" and len(CLASSES) > 0:
            desc = ""
            for i in CLASSES:
                if prompt in i[:3]:
                    result = True
                    print(" ".join(i[:3]))
                    if i[3] != "":
                        print(i[3])
        else:
            result = True
            print("Invalid query!")
        
        if not result:
            print("No results found for", prompt)
except KeyboardInterrupt:
    print("Closing!")