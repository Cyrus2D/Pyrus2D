"""
  \ file soccer_action.py
  \ brief abstract player actions class File
"""

# from lib.player.player_agent import *
# from lib.rcsc.server_param import *

"""
  \ class AbstractAction
  \ brief base class of actions
"""


class AbstractAction:
    S_action_object_counter = 0

    def __init__(self):
        AbstractAction.S_action_object_counter += 1
        self._action_object_id = AbstractAction.S_action_object_counter
        pass

    """
    \ brief pure virtual. set command to the action effector
    \ return_value True if action is performed
    \ return_value False if action is failed or not needed.
    """

    def execute(self, agent):
        pass

    """
    \ brief get ID of action object to identify action instances
    \ return ID of action object
    """

    def actionObjectID(self):
        return self._action_object_id


#  #################################
"""
 \ class BodyAction
 \ brief abstract body action
"""


class BodyAction(AbstractAction):

    def execute(self, agent):
        pass


#  #################################/

"""
  \ class NeckAction
  \ brief abstract turn neck action
"""


class NeckAction(AbstractAction):
    def __init__(self):
        super().__init__()

    def execute(self, agent):
        pass

    """
    \ brief create cloned action object
    \ return pointer to the cloned object instance.
    """

    def clone(self, agent):
        pass


#  #################################/

"""
\ class ViewAction
\ brief abstract change view action
"""


class ViewAction(AbstractAction):

    def __init__(self, ):
        super().__init__()

    def execute(self, agent):
        pass

    """
    \ brief create cloned action object
    \ return pointer to the cloned object instance.
    """

    def clone(self, agent):
        pass


#  #################################/

"""
\ class ArmAction
\ brief abstract point to action
"""


class ArmAction(AbstractAction):

    def __init__(self, ArmActions: list):
        super().__init__()
        self._ArmAction = ArmActions

    def execute(self, agent):
        pass

    """
    \ brief create cloned action object
    \ return pointer to the cloned object instance.
    """

    def clone(self, agent):
        pass

#  #################################/

"""
\ class ViewAction
\ brief abstract change view action
"""


class FocusPointAction(AbstractAction):

    def __init__(self, ):
        super().__init__()

    def execute(self, agent):
        pass

    """
    \ brief create cloned action object
    \ return pointer to the cloned object instance.
    """

    def clone(self, agent):
        pass

#  #################################/

"""
\ class SoccerBehavior
\ brief abstract player behavior.
"""


class SoccerBehavior(AbstractAction):

    def execute(self, agent):
        pass
