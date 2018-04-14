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
Students' Names: Ali Ahmed
Contest Number: 2
Description of Bot: I have two agents (offensive and defensive). The Defensive one is relatively straightforward, it copys lots of the baseline team code but uses inference to detect where the attacker/invader is if we have a noisy reading by seeing which dots disappeared on the map in the previous gameState. The bot can also go on offense when there is no threat, and when it does it uses all of the offensive tactics that the offensive bot has.
The offensive bot first pre-processes the map to figure out the 'exit positions', and remembers the amount of food it has eaten. It then uses that amount to determine when it should jump back to our side of the board. If it has eaten more than 3 pellets, the strategy changes dramatically, it will now place precedence on going back to the closest spot in the 'exitCol' on our side. I tried using BFS to determine the shortest path but it takes too long, instead we use distance to exitPath, as well as tracking previous moves so the bot doesn't get stuck moving back and forth.
"""
from captureAgents import CaptureAgent
import random, time, util
from game import Directions, Actions, Grid
import game
from util import nearestPoint, manhattanDistance
import distanceCalculator
#################
# Team creation #
#################
def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveAgent', second='DefensiveAgent'):
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
class OffensiveAgent(CaptureAgent):
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
    self.foodNum = 0
    # self.pathToExit = []
    self.myTeam = ''
    self.exitCol = []
    self.walls = gameState.getWalls()
    self.prevActions = [None, None, None, None]
    # get what team the bot is on
    if self.getTeam(gameState)[0] % 2 == 0:
      # exit direction left
      self.myTeam = 'red'
    else:
      # exit direction right
      self.myTeam = 'blue'
    # find available exit column spaces
    if self.myTeam == 'blue':
      exitCol = (gameState.data.layout.width) // 2
    else:
      exitCol = (gameState.data.layout.width - 1) // 2
    for i in range(1, gameState.data.layout.height - 1):
      # self.debugDraw([((gameState.data.layout.width - 1) // 2, i)], [0, 1, 0])
      if not self.walls[exitCol][i]:
        self.exitCol.append((exitCol, i))
    # for entry in self.exitCol:
    #   self.debugDraw([entry], [0, 1, 0])
  # Follows from getSuccessor function of ReflexCaptureAgent
  def getSuccessor(self,gameState,action):
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != util.nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor
  #Follows from chooseAction function of ReflexCaptureAgent
  def chooseAction(self,gameState):
    nextAction = None
    actions = gameState.getLegalActions(self.index)
    # # if we hold more than 3 pieces of food, run to the other side (while avoiding the ghost)
    if self.foodNum >= 3:
      # calculate fastest path to exit space using BFS.
      visited = []
      fringe = util.Queue()
      fringe.push( (gameState, [], 0) )
      finalConsiderations = []
      while not fringe.isEmpty():
          state = fringe.pop()
          node = state[0]
          directions = state[1]
          iteration = state[2]
          if node.getAgentPosition(self.index) in self.exitCol:
            nextDirection = directions[0]
            # finalDirections = directions + [node.getAgentPosition(self.index)]
            # self.pathToExit = finalDirections
            break
          if iteration == 3:
            finalDirections = directions + [node.getAgentPosition(self.index)]
            values = [self.specialEvaluate(node, a) for a in node.getLegalActions(self.index)]
            maxValue = max(values)
            finalConsiderations.append( (finalDirections[0], maxValue) )
          if node not in visited and iteration < 3:
              visited.append(node)
              for action in node.getLegalActions(self.index):
                child = self.getSuccessor(node, action)
                fringe.push((child, directions + [child.getAgentPosition(self.index)], iteration + 1))
      currMaxScore = -float(9999999999)
      nextDirection = None
      for entry in finalConsiderations:
        if entry[1] > currMaxScore:
          currMaxScore = entry[1]
          nextDirection = entry[0]
      for a in actions:
        if self.getSuccessor(gameState, a).getAgentPosition(self.index) == nextDirection:
          nextAction = a
          break
    if not nextAction:
      values = [self.evaluate(gameState, a) for a in actions]
      maxValue = max(values)
      bestActions = [a for a, v in zip(actions,values) if v == maxValue]
      nextAction = random.choice(bestActions)
    #DEBUG
    # for entry in self.pathToExit:
    #   self.debugDraw([entry], [0, 1, 0])
    # calculate food this pacman has eaten
    newGameState = self.getSuccessor(gameState, nextAction)
    if not newGameState.getAgentState(self.index).isPacman:
      self.foodNum = 0
    self.foodNum += len(self.getFood(gameState).asList()) - len(self.getFood(newGameState).asList())
    # Update previous actions, make sure the list doesn't get too big and cause error
    self.prevActions.append(nextAction)
    if len(self.prevActions) > 20:
      self.prevActions = self.prevActions[14:21]
    return nextAction
  #Follows from evaluate function of ReflexCaptureAgent
  def evaluate(self,gameState,action):
    features = self.getFeatures(gameState,action)
    weights = self.getWeights(gameState,action)
    return features * weights
  def specialEvaluate(self,gameState,action):
    features = self.specialGetFeatures(gameState,action)
    weights = self.specialGetWeights(gameState,action)
    return features * weights
  def specialGetWeights(self, gameState, action):
    return {'stuck': -10, 'eatFood': 1,'closeToExitPos': -15, 'repeatMovement': -1}
  def specialGetFeatures(self, gameState, action):
    # Start like getFeatures of OffensiveReflexAgent
    features = util.Counter()
    successor = self.getSuccessor(gameState,action)
    #Get other variables for later use
    food = self.getFood(gameState)
    capsules = gameState.getCapsules()
    foodList = food.asList()
    walls = gameState.getWalls()
    x, y = gameState.getAgentState(self.index).getPosition()
    vx, vy = Actions.directionToVector(action)
    newx = int(x + vx)
    newy = int(y + vy)
    # Get set of invaders and defenders
    enemies = [gameState.getAgentState(a) for a in self.getOpponents(gameState)]
    # ghosts
    invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    # attacking pacmen
    defenders =[a for a in enemies if a.isPacman and a.getPosition() != None]
    # Check if pacman has stopped
    if action == Directions.STOP:
      features["stuck"] = 1.0
    # If we've eaten enough food, try and go to an exit route
    if self.foodNum >= 3: #and (newx, newy) in self.pathToExit:
      # closestExit = self.pathToExit[-1]
      closestExit = self.exitCol[0]
      dist = self.getMazeDistance((newx, newy), closestExit)
      for entry in self.exitCol:
        if self.getMazeDistance((newx, newy), entry) < dist:
          closestExit = entry
          dist = self.getMazeDistance((newx, newy), entry)
      # features["pathOnExitRoute"] = 1
      normalized = manhattanDistance((0,0), closestExit)
      features["closeToExitPos"] = manhattanDistance(closestExit, (newx, newy)) / float(normalized)
    if self.prevActions[-4] != None and (self.prevActions[-3] == Directions.REVERSE[self.prevActions[-4]]) and (self.prevActions[-4] == self.prevActions[-2]) and (self.prevActions[-3] == self.prevActions[-1]) and action == self.prevActions[-4]:
      features['repeatMovement'] = 1
    # if action == "North":
    # if action == "West":
    return features
  # 1) Understand what's going on
  # 2) Add if the position in the successor is in the pathToExit, then go for it
  # 3) If you're going to hit a ghost, don't hit a ghost first and foremost
  def getFeatures(self, gameState, action):
    # Start like getFeatures of OffensiveReflexAgent
    features = util.Counter()
    successor = self.getSuccessor(gameState,action)
    #Get other variables for later use
    food = self.getFood(gameState)
    capsules = gameState.getCapsules()
    foodList = food.asList()
    walls = gameState.getWalls()
    x, y = gameState.getAgentState(self.index).getPosition()
    vx, vy = Actions.directionToVector(action)
    newx = int(x + vx)
    newy = int(y + vy)
    # Get set of invaders and defenders
    enemies = [gameState.getAgentState(a) for a in self.getOpponents(gameState)]
    # ghosts
    invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    # attacking pacmen
    defenders =[a for a in enemies if a.isPacman and a.getPosition() != None]
    # Check if pacman has stopped
    if action == Directions.STOP:
      features["stuck"] = 1.0
    # Get ghosts close by
    for ghost in invaders:
      ghostpos = ghost.getPosition()
      ghostNeighbors = Actions.getLegalNeighbors(ghostpos, walls)
      if (newx, newy) == ghostpos:
        # Encounter a Normal Ghost
        if ghost.scaredTimer == 0:
          features["scaredGhosts"] = 0
          features["normalGhosts"] = 1
        else:
          # Encounter a Scared Ghost (still prioritize food)
          features["eatFood"] += 2
          features["eatGhost"] += 1   
      elif ((newx, newy) in ghostNeighbors) and (ghost.scaredTimer > 0):
        features["scaredGhosts"] += 1
    # How to act if scared or not scared
    if gameState.getAgentState(self.index).scaredTimer == 0:    
      for ghost in defenders:
        ghostpos = ghost.getPosition()
        ghostNeighbors = Actions.getLegalNeighbors(ghostpos, walls)
        if (newx, newy) == ghostpos:
          features["eatInvader"] = 1
    else:
      for ghost in enemies:
        if ghost.getPosition()!= None:
          ghostpos = ghost.getPosition()
          ghostNeighbors = Actions.getLegalNeighbors(ghostpos, walls)
          if (newx, newy) in ghostNeighbors or (newx, newy) == ghostpos:
            features["eatInvader"] = -10
    # Get capsules when nearby
    for cx, cy in capsules:
      if newx == cx and newy == cy and successor.getAgentState(self.index).isPacman:
        features["eatCapsule"] = 1
    # If we've eaten enough food, try and go to an exit route
    if self.foodNum >= 3: #and (newx, newy) in self.pathToExit:
      # closestExit = self.pathToExit[-1]
      closestExit = self.exitCol[0]
      dist = self.getMazeDistance((newx, newy), closestExit)
      for entry in self.exitCol:
        if self.getMazeDistance((newx, newy), entry) < dist:
          closestExit = entry
          dist = self.getMazeDistance((newx, newy), entry)
      # features["pathOnExitRoute"] = 1
      normalized = manhattanDistance((0,0), closestExit)
      features["closeToExitPos"] = manhattanDistance(closestExit, (newx, newy)) / float(normalized)
      # mini BFS, extend 3 spaces away from each
    if self.prevActions[-4] != None and (self.prevActions[-3] == Directions.REVERSE[self.prevActions[-4]]) and (self.prevActions[-4] == self.prevActions[-2]) and (self.prevActions[-3] == self.prevActions[-1]) and action == self.prevActions[-4]:
      features['repeatMovement'] = 1
    # When to eat
    if not features["normalGhosts"]:
      if food[newx][newy]:
        features["eatFood"] = 1.0
      if len(foodList) > 0:
        tempFood =[]
        for food in foodList:
          food_x, food_y = food
          adjustedindex = self.index-self.index % 2
          check1 = food_y > (adjustedindex / 2) * walls.height / 3
          check2 = food_y < ((adjustedindex / 2) + 1) * walls.height / 3
          if (check1 and check2):
            tempFood.append(food)
        if len(tempFood) == 0:
          tempFood = foodList
        mazedist = [self.getMazeDistance((newx, newy), food) for food in tempFood]
      if min(mazedist) is not None:
        walldimensions = walls.width * walls.height
        features["nearbyFood"] = float(min(mazedist)) / walldimensions  
    # if action == "North":
    # if action == "West":
    return features
  def getWeights(self, gameState, action):
    return {'eatInvader': 5,'teammateDist': 1.5, 'nearbyFood': -5, 'eatCapsule': 10,
    'normalGhosts': -30, 'eatGhost': 1.0, 'scaredGhosts': 0.1, 'stuck': -10, 'eatFood': 1, 'pathOnExitRoute': 10, 'closeToExitPos': -15, 'repeatMovement': -1}
class DefensiveAgent(CaptureAgent):
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
    self.foodNum = 0
    # self.pathToExit = []
    self.myTeam = ''
    self.exitCol = []
    self.walls = gameState.getWalls()
    self.prevActions = [None, None, None, None]
    # get what team the bot is on
    if self.getTeam(gameState)[0] % 2 == 0:
      # exit direction left
      self.myTeam = 'red'
    else:
      # exit direction right
      self.myTeam = 'blue'
    # find available exit column spaces
    if self.myTeam == 'blue':
      exitCol = (gameState.data.layout.width) // 2
    else:
      exitCol = (gameState.data.layout.width - 1) // 2
    for i in range(1, gameState.data.layout.height - 1):
      # self.debugDraw([((gameState.data.layout.width - 1) // 2, i)], [0, 1, 0])
      if not self.walls[exitCol][i]:
        self.exitCol.append((exitCol, i))
    # for entry in self.exitCol:
    #   self.debugDraw([entry], [0, 1, 0])
  def getSuccessor(self,gameState,action):
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != util.nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor
  def evaluate(self,gameState,action):
    features = self.getFeatures(gameState,action)
    weights = self.getWeights(gameState,action)
    return features*weights
  def chooseAction(self,gameState):
    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState,a) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions,values) if v == maxValue]
    nextAction = random.choice(bestActions)
    #DEBUG
    # for entry in self.pathToExit:
    #   self.debugDraw([entry], [0, 1, 0])
    # calculate food this pacman has eaten
    newGameState = self.getSuccessor(gameState, nextAction)
    if not newGameState.getAgentState(self.index).isPacman:
      self.foodNum = 0
    self.foodNum += len(self.getFood(gameState).asList()) - len(self.getFood(newGameState).asList())
    # Update previous actions, make sure the list doesn't get too big and cause error
    self.prevActions.append(nextAction)
    if len(self.prevActions) > 20:
      self.prevActions = self.prevActions[14:21]
    return nextAction
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    # computes whether we're on offense (-1) or defense (1)
    if not myState.isPacman: 
      features['onDefense'] = 1
      # standard from baseline - more numInvaders, larger minimum distance, worse successor (-30000, -1500).
      # Note if the opponent is greater than or equal to 5 blocks away (manhattan distance) then we only get a noisy reading.
      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      features['numInvaders'] = len(invaders)
      if len(invaders) > 0:
        distsManhattan = [manhattanDistance(myPos, a.getPosition()) for a in invaders]
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        # get a more exact reading if food disappears between turns
        if min(distsManhattan) >= 5: 
          prevGamestate = self.getPreviousObservation()
          currGamestate = self.getCurrentObservation()
          prevFood = self.getFood(prevGamestate).asList()
          currFood = self.getFood(currGamestate).asList()
          missingFood = list(set(currFood) - set(prevFood))
          dists.extend([self.getMazeDistance(myPos, a) for a in missingFood])
          features['invaderDistance'] = min(dists)
        else:
          features['invaderDistance'] = min(dists)
      # standard from baseline - is the action was to stop (-400) or to go back / reverse (-250)
      if action == Directions.STOP: features['stop'] = 1
      rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
      if action == rev: features['reverse'] = 1
      # transform defense agent into offensive when scared OR when there are no invaders
      # ADJUST WHEN DONE WITH OFFENSIVE AGENT - ADD ALL CHARACTERISTICS HERE ALSO CONSIDER THE OFFENSE OR DEFENSE PLAY (ABOVE). 
      if(successor.getAgentState(self.index).scaredTimer > 0):
        features['numInvaders'] = 0 # change all of the defense ones to 0
        if(features['invaderDistance'] <= 2): features['invaderDistance'] = 2
      # use the minimum noisy distance between our agent and their agent
      teamNums = self.getTeam(gameState)
      features['stayApart'] = self.getMazeDistance(gameState.getAgentPosition(teamNums[0]), gameState.getAgentPosition(teamNums[1]))
      features['offenseFood'] = 0
      # IF THERE ARE NO INVADERS THEN GO FOR FOOD / REFLEX AGENT. I LIKE THIS. COPY THE OFFENSE CODE HERE AS WELL.
      if(len(invaders) == 0 and successor.getScore() != 0):
        features['onDefense'] = -1
        features['offenseFood'] = min([self.getMazeDistance(myPos,food) for food in self.getFood(successor).asList()])
        features['foodCount'] = len(self.getFood(successor).asList())
        features['stayAprts'] += 2
        features['stayApart'] *= features['stayApart']
    else: # Offensive Agent
      features['onDefense'] = -1 
      # Start like getFeatures of OffensiveReflexAgent
      features = util.Counter()
      successor = self.getSuccessor(gameState,action)
      #Get other variables for later use
      food = self.getFood(gameState)
      capsules = gameState.getCapsules()
      foodList = food.asList()
      walls = gameState.getWalls()
      x, y = gameState.getAgentState(self.index).getPosition()
      vx, vy = Actions.directionToVector(action)
      newx = int(x + vx)
      newy = int(y + vy)
      # Get set of invaders and defenders
      enemies = [gameState.getAgentState(a) for a in self.getOpponents(gameState)]
      # ghosts
      invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      # attacking pacmen
      defenders =[a for a in enemies if a.isPacman and a.getPosition() != None]
      # Check if pacman has stopped
      if action == Directions.STOP:
        features["stuck"] = 1.0
      # Get ghosts close by
      for ghost in invaders:
        ghostpos = ghost.getPosition()
        ghostNeighbors = Actions.getLegalNeighbors(ghostpos, walls)
        if (newx, newy) == ghostpos:
          # Encounter a Normal Ghost
          if ghost.scaredTimer == 0:
            features["scaredGhosts"] = 0
            features["normalGhosts"] = 1
          else:
            # Encounter a Scared Ghost (still prioritize food)
            features["eatFood"] += 2
            features["eatGhost"] += 1   
        elif ((newx, newy) in ghostNeighbors) and (ghost.scaredTimer > 0):
          features["scaredGhosts"] += 1
      # How to act if scared or not scared
      if gameState.getAgentState(self.index).scaredTimer == 0:    
        for ghost in defenders:
          ghostpos = ghost.getPosition()
          ghostNeighbors = Actions.getLegalNeighbors(ghostpos, walls)
          if (newx, newy) == ghostpos:
            features["eatInvader"] = 1
      else:
        for ghost in enemies:
          if ghost.getPosition()!= None:
            ghostpos = ghost.getPosition()
            ghostNeighbors = Actions.getLegalNeighbors(ghostpos, walls)
            if (newx, newy) in ghostNeighbors or (newx, newy) == ghostpos:
              features["eatInvader"] = -10
      # Get capsules when nearby
      for cx, cy in capsules:
        if newx == cx and newy == cy and successor.getAgentState(self.index).isPacman:
          features["eatCapsule"] = 1
      # If we've eaten enough food, try and go to an exit route
      if self.foodNum >= 3: #and (newx, newy) in self.pathToExit:
        # closestExit = self.pathToExit[-1]
        closestExit = self.exitCol[0]
        dist = self.getMazeDistance((newx, newy), closestExit)
        for entry in self.exitCol:
          if self.getMazeDistance((newx, newy), entry) < dist:
            closestExit = entry
            dist = self.getMazeDistance((newx, newy), entry)
        # features["pathOnExitRoute"] = 1
        normalized = manhattanDistance((0,0), closestExit)
        features["closeToExitPos"] = manhattanDistance(closestExit, (newx, newy)) / float(normalized)
        # mini BFS, extend 3 spaces away from each
      if self.prevActions[-4] != None and (self.prevActions[-3] == Directions.REVERSE[self.prevActions[-4]]) and (self.prevActions[-4] == self.prevActions[-2]) and (self.prevActions[-3] == self.prevActions[-1]) and action == self.prevActions[-4]:
        features['repeatMovement'] = 1
      # When to eat
      if not features["normalGhosts"]:
        if food[newx][newy]:
          features["eatFood"] = 1.0
        if len(foodList) > 0:
          tempFood =[]
          for food in foodList:
            food_x, food_y = food
            adjustedindex = self.index-self.index % 2
            check1 = food_y > (adjustedindex / 2) * walls.height / 3
            check2 = food_y < ((adjustedindex / 2) + 1) * walls.height / 3
            if (check1 and check2):
              tempFood.append(food)
          if len(tempFood) == 0:
            tempFood = foodList
          mazedist = [self.getMazeDistance((newx, newy), food) for food in tempFood]
        if min(mazedist) is not None:
          walldimensions = walls.width * walls.height
          features["nearbyFood"] = float(min(mazedist)) / walldimensions  
      # if action == "North":
      # if action == "West":
    return features
  def getWeights(self,gameState, action):
    return {'foodCount': -20,'offenseFood': -1, 'numInvaders': -30000, 'onDefense': 20, 'stayApart': 50, 'invaderDistance':-1500, 'stop':-400,'reverse':-250,
    'eatInvader': 5,'teammateDist': 1.5, 'nearbyFood': -5, 'eatCapsule': 10,
    'normalGhosts': -30, 'eatGhost': 1.0, 'scaredGhosts': 0.1, 'stuck': -10, 'eatFood': 1, 'pathOnExitRoute': 10, 'closeToExitPos': -15, 'repeatMovement': -1}
