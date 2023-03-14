class MessageParamsParserSee:
    def __init__(self) -> None:
        pass

    def parse(self, string) -> list:
        res = []
        objects_start_index = string.find("((")

        if objects_start_index == -1:
            return []

        objects_string = string[objects_start_index: -1]
        objects_list_string = objects_string[1:-1].split(") (")
        
        for object_string in objects_list_string:
            key_end_index = object_string.find(")")
            key = object_string[1:key_end_index]
            res.append((key, object_string[key_end_index+1:].strip(" ")))
        return res