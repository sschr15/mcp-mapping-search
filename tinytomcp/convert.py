import sys
import os
from typing import List

verbose = "verbose" in sys.argv

input_file = sys.argv[1]
output_folder = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1] + "-mcp"

with open(input_file) as file:
    contents = file.read().splitlines()

# Cut off first and last line
contents = contents[1:-1]

defline = "searge,name,side,desc"

output = {
    "classes": ["searge,name,desc"],
    "methods": [defline],
    "fields":  [defline],
    "params":  ["param,name,side,desc"]
}

in_method = False
classnum = ""
methodnum = ""
current_constructor = 0

last_line = None

print("Converting yarn to mcp-style")
for i in contents:
    official = ""
    intermediary = ""
    named = ""
    line = i.strip("\t").split("\t")
    if line[0] == "c" and len(line) > 2:
        # this is a class definition, we don't really care but we do
        official = line[1]
        classnum = line[2].split("/")[-1][6:]
        intermediary = f'class_{classnum}_{official}'
        named = line[3].split("/")[-1]

        current_constructor = 0

        last_line = "classes"

        output["classes"].append(",".join([intermediary, named, ""]))
    elif line[0] == "m" and "method" in line[3]:
        # method definition
        official = line[2]
        methodnum = line[3][7:]
        intermediary = f'func_{methodnum}_{official}'
        named = line[4]

        last_line = "methods"

        output["methods"].append(",".join([intermediary, named, "", ""]))
        in_method = True
    elif line[0] == "m" and line[2] == "<init>":
        last_line = "params"
        in_method = False
    elif line[0] == "m":
        if verbose:
            print("Ignoring line", "\t".join(line), "because it probably is deobf'd")
        last_line = None
    elif line[0] == "p":
        official = line[1]
        if in_method:
            intermediary = f'p_{methodnum}_{official}_'
        else:
            intermediary = f'p_i{classnum}_{official}_{current_constructor}'
            current_constructor += 1
        named = line[-1]
        
        last_line = "params"

        output["params"].append(",".join([intermediary, named, ""]))
    elif line[0] == "f":
        official = line[2]
        intermediary = f'field_{line[3][6:]}_{official}'
        named = line[4]
        
        last_line = "fields"

        output["fields"].append(",".join([intermediary, named, "", ""]))
    elif line[0] == "c" and i.startswith("\t"):
        # comment, not a class
        if last_line != None:
            output[last_line][-1] += line[1] if "," not in line[1] else f'"{line[1]}"'
    else:
        print("\x1b[31mInvalid line:", "\t".join(line) + "\x1b[0m")
        last_line = None

print("Saving to", output_folder)

os.makedirs(output_folder, exist_ok=True)

for key, value in output.items():
    with open(output_folder + f'/{key}.csv', "w") as file:
        file.write("\n".join([value[0]] + sorted(value[1:])) + "\n")

print("Done!")