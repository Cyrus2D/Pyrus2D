from lib.math.vector_2d import Vector2D
from lib.player.object_player import PlayerObject
from lib.player.world_model import WorldModel
from lib.player.messenger.player_pos_unum_messenger import PlayerPosUnumMessenger

def test_player_pos_unum_test():
    wm = WorldModel()
    player= PlayerObject()
    player._pos = Vector2D(10,20)
    player._unum = 5
    
    wm._our_players_array[5] = player
    
    
    msg = PlayerPosUnumMessenger(5).encode(wm)
    print(msg)
    
    PlayerPosUnumMessenger(message=msg).decode(wm, 4)
    
    print(wm.our_player(5))
    
if __name__ == "__main__":
    test_player_pos_unum_test()