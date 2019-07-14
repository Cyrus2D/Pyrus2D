def main():
    file = open("variables", "r")
    lines = file.read().split("\n")

    # make list of variables
    variables = []
    for line in lines:
        if line.find("self") == -1:
            continue
        if line.find(":") != -1:
            if line.find(":") < line.find("="):
                variables.append(line.split(":")[0].strip())
                continue
        if line.find("=") != -1:
            variables.append(line.split("=")[0].strip())
            continue
        variables.append(line.strip())

    # make accessors
    accessors = []
    for var in variables:
        acc = f"def {var[6:]}(self):\n" \
              f"\treturn {var}"
        accessors.append(acc)

    # write in file
    file = open("accessors", "w")
    for acc in accessors:
        file.write(acc + "\n")


if __name__ == "__main__":
    main()
