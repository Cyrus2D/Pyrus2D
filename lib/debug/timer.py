import time

class ProfileTimer:
    main_dict: dict = {}

    @staticmethod
    def start(name):
        if name not in ProfileTimer.main_dict:
            ProfileTimer.main_dict[name] = [0, 0, -1]
        ProfileTimer.main_dict[name][2] = time.time()

    @staticmethod
    def end(name):
        if name not in ProfileTimer.main_dict:
            return
        ProfileTimer.main_dict[name][0] += time.time() - ProfileTimer.main_dict[name][2]
        ProfileTimer.main_dict[name][1] += 1

    @staticmethod
    def get():
        res = ''
        for name, value in ProfileTimer.main_dict.items():
            avg = value[0] / value[1] if value[1] > 0 else -1
            res += f'## {name}: {round(avg, 6)}, {value[1]} \n'
        return res

# parse_message: 0.3392317295074463, 410, 0.0008273944622132837 ## flush: 0.4707632064819336, 1096, 0.00042952847306745764 ## synchaction: 5.524951934814453, 79, 0.06993610044068928 ##
#parse_message: 0.09196591377258301, 370, 0.0002485565237096838 ## flush: 0.5167291164398193, 1111, 0.00046510271506734416 ## synchaction: 2.8537697792053223, 92, 0.031019236730492634 ##