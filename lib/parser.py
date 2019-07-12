class MessageRecieveParser:
    def __init__(self):
        self._dic = {}

    @staticmethod
    def _parse(dic, string: str):
        string = string.strip(" ()")
        if (len(string) < 3):
            return
        key = string.split(" ")[0]
        value = string[string.find(" "):]
        if (key == "wind_random"):
            print("HI")
        if not MessageRecieveParser.need_dict(value):
            if value.find(")") == -1:
                dic[key] = value.strip()
            else:
                dic[key] = value[:value.find(")")].strip()
            MessageRecieveParser._parse(dic, value[value.find(")"):])
        else:
            dic[key] = {}
            MessageRecieveParser._parse(dic[key], value)

    @staticmethod
    def need_dict(string):
        if string.find("(") == -1:
            return False
        return string.find(")") > string.find("(")

    def parse(self, string):
        MessageRecieveParser._parse(self._dic, string)
        return self._dic

    def dic(self):
        return self._dic
