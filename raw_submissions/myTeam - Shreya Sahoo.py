# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

"""
Students' Names: Shreya Sahoo
Contest Number: 2
Description of Bot: This bot contains a defensive and offensive agent. 
The defensive agent protects its team side of the board and eats ghosts. 
However, if there aren't any invaders, it will go to the otherside of the board and 
help the offensive bot eat the other pellets. The features I used were the successor score, how many invaders were present, and how 
far the agents were from food, as well as how far the offensive agent was from the capsule. 
"""


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefensiveAgent', second = 'OffensiveAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########
class MainAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    self.registerTeam(self.getTeam(gameState))

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)

    values = [self.evaluate(gameState, a) for a in actions]

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

class DefensiveAgent(MainAgent):
  """
  Guards against members from the opposing team who are trying to enter.
  """
  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state. The important features are:
    1. Successor Score 
    2. How far an agent is from a capsule that its defending based on how many food pellets are left 
    3. The distance to the nearest food
    4. The distance to the nearest ghost
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    foodList1 = self.getFoodYouAreDefending(successor).asList()
    foodList2 = self.getFoodYouAreDefending(successor).asList()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    # nearest ghost on the blue side
    total = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    ghosts = [a for a in total if not a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(ghosts)
    if len(ghosts) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
      features['closestGhost'] = min(dists)

    if len(foodList2) > 0 and len(ghosts) > 1 and len(invaders) < len(ghosts): 
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList2])
      features['nearestFood'] = - minDistance

    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
  def getWeights(self, gameState, action):
    return {'successorScore': 1.0, 'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -1000, 'stop': -100, 'reverse': -2, 'nearestFood': 10}


class OffensiveAgent(MainAgent):
  """
  Gets food from the opposing side.
  """
  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state. The important features are:
    1. Successor Score 
    2. How far an agent is from a capsule if the scared timer is on / off. 
    3. The distance to the nearest food.
    4. The distance to the nearest ghost if the scared timer is on / off.
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()
    features['successorScore'] = -len(foodList)
    myPos = successor.getAgentState(self.index).getPosition()

    # agent to capsule on the otherside 
    if len(self.getCapsules(gameState)) > 0:
      closestCapsule = min([self.distancer.getDistance(i, myPos) \
        for i in self.getCapsules(gameState)])
    else: 
      closestCapsule = 1
    features['closestCapsule'] = closestCapsule

    #nearest food
    if len(foodList) > 0: 
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['nearestFood'] = minDistance
    else:
      features['nearestFood'] = 0

    # nearest ghost on the blue side
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      if closestCapsule > 0:
        features['closestGhost'] = -min(dists)
      else:
        features['closestGhost'] = min(dists) 
    else: 
      features['closestGhost'] = min(dists) 

    
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary."""
    return {'successorScore': 100, 'closestCapsule': -5, 'nearestFood': -10, 'closestGhost': 10, 'numInvaders': 0}


