class MessageParamsParser:
    def __init__(self):
        self._dic = {}

    @staticmethod
    def _parse(dic, string: str):
        string = string.strip(" ()")
        if len(string) < 3:
            return
        key = string.split(" ")[0].strip("()")
        value = string[string.find(" "):]
        if not MessageParamsParser.need_dict(value):
            if value.find(")") == -1:
                dic[key] = value.strip()
            else:
                dic[key] = value[:value.find(")")].strip()
            MessageParamsParser._parse(dic, value[value.find(")"):])
        else:
            dic[key] = {}
            end_of_dic = MessageParamsParser.end_of_dic(value)
            if end_of_dic == -1:
                MessageParamsParser._parse(dic[key], value[:])
            else:
                MessageParamsParser._parse(dic[key], value[:end_of_dic])
            MessageParamsParser._parse(dic, value[end_of_dic:])

    @staticmethod
    def need_dict(string):
        if string.find("(") == -1:
            return False
        return string.find(")") > string.find("(")

    @staticmethod
    def end_of_dic(string):
        k = 1
        for i in range(len(string)):
            if string[i] == "(":
                k += 1
            elif string[i] == ")":
                k -= 1
            if k == 0:
                return i
        return -1

    def parse(self, string):
        MessageParamsParser._parse(self._dic, string)
        return self._dic

    def dic(self):
        return self._dic


