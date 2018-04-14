"""
Students' Names: Benjamin Carlson, Diana Tu
Contest Number: 2
Description of OffensiveAgent: Tries to eat closest food, but runs from ghosts and avoids tunnels
Decription of DefensiveAgent: Moves randomly until it sees enemy, then chases it 
"""

## myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveAgent', second = 'DefensiveAgent'):
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

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

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


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    ''' 
    You should change this in your own agent.
    '''

    return random.choice(actions)

class OffensiveAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.calcHoles(gameState)
    self.foodStart = len(self.getFood(gameState).asList())
    pack = gameState.getWalls().packBits()
    self.length = pack[0]
    self.width = pack[1]
    self.hole = None
    if self.red:
      self.side = 0
    else:
      self.side = 1

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    value = -pow(2, 63)
    best_action = None
    for action in actions:
      action_value = self.getScore(gameState, action)
      if action != "Stop" and action_value > value:
        value = action_value
        best_action = action
    return best_action

  def getScore(self, gameState, action):
    foods = self.getFood(gameState).asList()
    successor = gameState.generateSuccessor(self.index, action)
    myPos = successor.getAgentPosition(self.index)
    dist = pow(2, 63)
    for food in foods:
      food_dist = self.getMazeDistance(myPos, food)
      if food_dist < dist:
        dist = food_dist
    if (self.foodStart - len(foods)) >= 2 and dist > 2:
      dist = self.retreat(gameState, action)
      if dist == 0:
        self.foodStart = len(foods)
    return -dist + self.getNegs(gameState, action)

  def retreat(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    nextPos = successor.getAgentPosition(self.index)
    dist = pow(2, 63)
    walls = gameState.getWalls()
    for i in range(self.width):
      mid_dist = pow(2, 63)
      if not walls[self.length // 2 - self.side][i]:
        mid_dist = self.getMazeDistance(nextPos, (self.length // 2 - self.side, i))
      if mid_dist < dist:
        dist = mid_dist
    return dist

  def getNegs(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    myPos = successor.getAgentPosition(self.index)
    enemies = [successor.getAgentState(i).getPosition() for i in self.getOpponents(successor)]
    dist = pow(2, 63)
    for em in enemies:
      em_dist = pow(2, 63)
      if em != None:
        em_dist = self.getMazeDistance(myPos, em)
      if em_dist < dist:
        dist = em_dist

    if myPos in self.holes.keys():
      self.hole = self.holes[myPos]
    if self.hole != None and myPos in self.hole[1]:
      if dist <= 1:
        return -10000
      if dist <= len(self.hole[1]):
        return -1000
    else:
      self.hole = None
    if dist <= 3:
      return -100
    return 0

  def calcHoles(self, gameState):
    walls = gameState.getWalls()
    pack = walls.packBits()
    length = pack[0]
    width = pack[1]
    holes = []
    for i in range(1, length - 1):
      for j in range(1, width - 1):
        if not walls[i][j]:
          hole = self.isHole(i, j, walls, gameState)
          if hole[0]:
            holes.append(hole[1])
    holes_dict = {}
    for hole in holes:
      holes_dict[hole[1][len(hole[1]) - 1]] = hole
    self.holes = holes_dict

  def isHole(self, i, j, walls, gameState):
    wall = 0
    foods = self.getFood(gameState)
    food = 0
    length = 1
    pos = [(i, j)]
    if walls[i - 1][j]:
      wall += 1
    else:
      ex = (i - 1, j)
    if walls[i][j - 1]:
      wall += 1
    else:
      ex = (i, j - 1)
    if walls[i + 1][j]:
      wall += 1
    else:
      ex = (i + 1, j)
    if walls[i][j + 1]:
      wall += 1
    else:
      ex = (i, j + 1)
    if foods[i][j]:
      food += 1
    if wall != 3:
      return (False, (food, pos))

    while wall >= 2:
      wall = 0
      length += 1
      pos.append(ex)
      old = (i, j)
      i, j = ex
      if walls[i - 1][j]:
        wall += 1
      else:
        if (i - 1, j) != old:
          ex = (i - 1, j)
      if walls[i][j - 1]:
        wall += 1
      else:
        if (i, j - 1) != old:
          ex = (i, j - 1)
      if walls[i + 1][j]:
        wall += 1
      else:
        if (i + 1, j) != old:
          ex = (i + 1, j)
      if walls[i][j + 1]:
        wall += 1
      else:
        if (i, j + 1) != old:
          ex = (i, j + 1) 
      if foods[i][j]:
        food += 1
    return (True, (food, pos))

class DefensiveAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.start = gameState.getAgentPosition(self.index)
    self.prev = None
    if self.red:
      self.side = 1
    else:
      self.side = 0
    pack = gameState.getWalls().packBits()
    self.length = pack[0]
    self.width = pack[1]

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    walls = gameState.getWalls()
    value = -pow(2, 63)
    best_action = None
    dist = pow(2, 63)
    rand_spot = (random.randint(0, self.length // 2 - 1) + self.side * self.length // 2 - 1, random.randint(0, self.width - 1))
    while walls[rand_spot[0]][rand_spot[1]]:
      rand_spot = (random.randint(0, self.length // 2 - 1) + self.side * self.length // 2 - 1, random.randint(0, self.width - 1))
    rand_action = None
    for action in actions:
      action_value = self.getScore(gameState, action)
      if action != "Stop" and action_value >= value:
        value = action_value
        best_action = action
      successor = gameState.generateSuccessor(self.index, action)
      next_pos = successor.getAgentPosition(self.index)
      rand_dist = self.getMazeDistance(next_pos, rand_spot)
      if rand_dist < dist:
        dist = rand_dist
        rand_action = action
    if action_value == -pow(2, 63):
      best_action = rand_action
    return best_action

  def getScore(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    enemies = [gameState.getAgentState(i).getPosition() for i in self.getOpponents(gameState)]
    myPos = successor.getAgentState(self.index).getPosition()
    dist = pow(2, 63)
    for em in enemies:
      em_dist = pow(2, 63)
      if em is None:
        continue
      if self.red:
        if em[0] >= self.length // 2:
          continue
      else:
        if em[0] < self.length // 2:
          continue
      em_dist = self.getMazeDistance(myPos, em)
      if em_dist < dist:
        dist = em_dist
    return -dist


