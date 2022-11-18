from lib.math.vector_2d import Vector2D
from lib.player.object_player import PlayerObject
from lib.player.world_model import WorldModel
from lib.player.messenger.player_pos_unum_messenger import PlayerPosUnumMessenger
from lib.rcsc.types import SideID

def test_player_pos_unum_test():
    wm_sender = WorldModel()
    wm_reciever = WorldModel()
    
    wm_sender._our_side = 'l'
    wm_reciever._our_side = 'l'
    
    player= PlayerObject()
    player._pos = Vector2D(10,20)
    player._unum = 5
    player._side = SideID.LEFT
    
    player2= PlayerObject()
    player2._pos = Vector2D(1,2)
    player2._unum = 5
    player2._side = SideID.LEFT
    player2._pos_count = 20
    player2._seen_pos_count = 20

    wm_sender._our_players_array[5] = player
    wm_sender._teammates.append(player)
    wm_reciever._teammates.append(player2)
    
    
    print(wm_sender._teammates)
    print(wm_reciever._teammates)
    
    
    
    msg = PlayerPosUnumMessenger(5).encode(wm_sender)
    print(msg)
    
    PlayerPosUnumMessenger(message=msg).decode(wm_reciever, 4)
    
    print(wm_sender._teammates)
    print(wm_reciever._teammates)
    
if __name__ == "__main__":
    test_player_pos_unum_test()