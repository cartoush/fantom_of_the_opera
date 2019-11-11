import logging
import sys
from . import AlphaBetaDetective
from . import AlphaBetaFantom
from . import roles

class GameAgent():

    def __init__(self, world, role):
        self.world = world
        self.role = role

    def bluePower(self, node, data):
        if (data.find("bloquer") != - 1):
            return (str(node.power[0]))
        return (str(node.power[1]))

    def violetPower(self, node):
        return node.power

    def greyPower(self, node):
        return(node.power)

    def getRole(self):
        return self.role

    ## Return the best Tile selection
    def selectTile(self, root):
        logging.info("[IA] Trying to find best Tile")
        if self.role is "fantom":
            alphaB = AlphaBetaFantom.AlphaBetaFantom(root)
        else:
            alphaB = AlphaBetaDetective.AlphaBetaDetective(root)
        node = alphaB.alpha_beta_search(root);
        nbAnswer = node.parent.color.index(node.sColor)
        return str(nbAnswer), node 

    ## Return the best next pos
    def nextPos(self, root):
        if (self.role != roles.PLAYER_TYPE.DETECTIVE):
            alphaB = AlphaBetaFantom.AlphaBetaFantom(root)
        else:
            alphaB = AlphaBetaDetective.AlphaBetaDetective(root)
        node = alphaB.alpha_beta_search(root)
        if (node.move == ''):
            node = alphaB.alpha_beta_search(root)
        logging.info("[IA] selected POSITION %s"%(node.move))
        return str(node.move), node

    ## Return the best power choice
    def powerChoice(self, root):
        if (self.role != roles.PLAYER_TYPE.DETECTIVE):
            alphaB = AlphaBetaFantom.AlphaBetaFantom(root)
        else:
            alphaB = AlphaBetaDetective.AlphaBetaDetective(root)
        node = alphaB.alpha_beta_search(root)
        if (node.used == True and node.parent.used == False):
            return str(1), node
        return str(0), node