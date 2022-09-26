class MessageParamsParserSee:
    def __init__(self) -> None:
        pass

    def parse(self, string):
        dic = {}
        dic["cycle"] = int(string.strip(" ()").split(" ")[1])
        objects_start_index = string.find("((")

        if objects_start_index == -1:
            print("No Objects have been seen")
            return

        objects_string = string[objects_start_index: -1]
        objects_list_string = objects_string[1:-1].split(") (")
        
        dic = {}
        for object_string in objects_list_string:
            key_end_index = object_string.find(")")
            key = object_string[1:key_end_index]
            dic[key] = object_string[key_end_index+1:]
        
        return dic