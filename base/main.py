# from lib.Player.player_agent import *
#
#
# def main():
#     player_agent = PlayerAgent()
#     player_agent.run()
#
#
# if __name__ == "__main__":
#     main()

from lib.parser.parser_message_fullstate_world import FullStateWorldMessageParser

message = '(fullstate 0 (pmode before_kick_off) (vmode high normal) (count 0 25 0 0 0 0 0 0) (arm (movable 0) (expires 0) (target 0 0) (count 0)) (score 0 0) ((b) 0 0 0 0) ((p l 1 0) -3 -37 0 0 0 0 (stamina 6625 1 1 129475)) ((p r 1 0) 3 -37 0 0 0 0 (stamina 6790 1 1 129610)))'

dic = FullStateWorldMessageParser().parse(message
                                          )
