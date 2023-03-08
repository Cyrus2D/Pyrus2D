class Color:
    def __init__(self, red: int = 0, green: int = 0, blue: int = 0, string: str = None):
        self._hex: str = ""
        if string is None:
            red = ('0' if red < 16 else "") + hex(red).split("x")[1]
            green = ('0' if green < 16 else "") + hex(green).split("x")[1]
            blue = ('0' if blue < 16 else "") + hex(blue).split("x")[1]
            self._hex = f"#{red}{green}{blue}"
        else:
            if string[0] == '#':
                self._hex = string
            else:
                string = string.lower()
                if string in ['white', 'w']:
                    self.__init__(255, 255, 255)
                elif string in ['black', 'b']:
                    self.__init__(0, 0, 0)
                elif string in ['red', 'r']:
                    self.__init__(255, 0, 0)
                elif string in ['green', 'g']:
                    self.__init__(0, 255, 0)
                elif string in ['blue', 'b']:
                    self.__init__(0, 0, 255)
                elif string in ['yellow', 'y']:
                    self.__init__(255, 248, 27)
                elif string in ['ping', 'p']:
                    self.__init__(241, 27, 255)
                elif string in ['gray']:
                    self.__init__(151, 151, 151)

    def hex(self):
        return self._hex

    def color(self):
        return self._hex

    def __repr__(self):
        return self._hex
