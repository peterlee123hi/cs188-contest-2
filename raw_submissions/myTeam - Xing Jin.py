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
Students' Names: Xing Jin, Yanzhou Pan
Contest Number: 1
Description of Bot: We used four features in offensive evaluation:
1. successorScore. This one indicates the total number of remaining food. We set the weight to 1000
because it is very important.
2. distance to food. We use the Maze distance to the nearest food as the distance feature. We didn't choose
 the total distance because the food maybe distributed in a biased way, with the most density most dangerous,
  which is not helpful for us.
3. distanceToHome. This one is kind of tricky. It is not exactly the distance to home, but the vertical
distance to the start side. We use this to enable our agent can get back as soon as he gets 'enough' food
thus prevent being captured with a bunch of dots in his backpack. We use a kind of reflex strategy to
determine how much is the limit volume, which is set to min(len(foodList)/5,self.lastReturned-2) thereby.
4. distanceToGhost. Also, we decide to use the distance to the nearest ghost as the distoghost feature. The
weight is set to 500 and the distance is modified before final usage. Because when the pacman is still
relatively safe, it is not harm to eat another food beside him. Only when the ghost is extremely close the
pacman should go nowhere but home.

In addition, we used a banned set to prevent pacman from lingering in the same place for a second round. Therefore
 breaking some of the stuck situation.

 Moreover, we updated the agent by switching in offensive and defensive plays. When we have a relatively large
 advantage on the opponent, the offensive agent would switch to defense as well to ensure victory.

 Defensive part:We used several new features in offensive evaluation:
 1. invader distance which indicates the distance to a nearest invader. When the agent is unfortunately scared,
 keep an eye on the enemy without being caught. Accordingly, we can capture the enemy as soon as we recover.
 2. Another feature that is worth discussing is disToHome. Inspired by the offensive agent, we decide to keep
 out defensive agent not too far away from the mid line. We accomplish this function by using distohome:
 when we are too close from home, the agent will be inclined to move to the middle line, where is easier
 to catch a enemy on his way back home.

"""

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from baselineTeam import ReflexCaptureAgent
from util import nearestPoint

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

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def __init__( self, index, timeForComputing = .1 ):
      #init as a big value
      self.lastReturned=50
      CaptureAgent.__init__( self, index, timeForComputing = .1 )

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

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

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class OffensiveAgent(ReflexCaptureAgent):
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
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.registerTeam(self.getTeam(gameState))
    self.buddyIndex = [i for i in self.agentsOnTeam if i != self.index][0]


  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

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
    choice=random.choice(bestActions)
    # make a ban set when pacman get stuck
    if choice==Directions.STOP:
      self.banSet.append(gameState.getAgentState(self.index).getPosition())

    return choice

  def getFeatures(self, gameState, action):
    thisState=gameState.getAgentState(self.index)
    if thisState.numCarrying > 0 and not thisState.isPacman:
        # record the number of capsules pacman returned last time
        self.lastReturned = thisState.numCarrying
        thisState.numReturned += thisState.numCarrying
        thisState.numCarrying = 0
    #if doesn't have enough advantage, time to attack
    if gameState.getScore()<=len(self.getFood(self.getSuccessor(gameState, action)).asList())/2:
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        capsules=gameState.getCapsules()
        foodList = self.getFood(successor).asList()
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        features['successorScore'] = -len(foodList)#self.getScore(successor)
        # init postions and foodlist
        enemyInitPos=gameState.getInitialAgentPosition(self.getOpponents(successor)[0])
        initialpos=gameState.getInitialAgentPosition(self.index)
        midPosx=(enemyInitPos[0]+initialpos[0])/2
        for capsule in capsules:
          if capsule[0]>midPosx:
            foodList.append(capsule)
        # when get back to my side, reset ban set
        if not myState.isPacman:
          self.banSet=[]
        # if the position is banned, return a minimum score
        if successor.getAgentState(self.index).getPosition() in self.banSet:
          features['successorScore']=-9999
          return features

        # Compute distance to the nearest food
        if len(foodList) > 0: # This should always be True,  but better safe than sorry
          myPos = successor.getAgentState(self.index).getPosition()
          minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
          features['distanceToFood'] = minDistance


        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        oppoAllin = len([a for a in enemies if a.isPacman])==2
        limit=min(len(foodList)/5,self.lastReturned-2)
        if self.lastReturned<=2:
          limit=2
        if oppoAllin:
          limit=len(foodList)*3
        # get back to my side when the pacman carries enough food
        if myState.numCarrying>limit or (gameState.data.timeleft<=200 and myState.numCarrying>0):
          disToHome=abs(initialpos[0]-myPos[0])
        else:
          disToHome=0
        features['distanceToHome']=disToHome

        # Pan's code
        """ Keep Pacman away from opponent's defensive agent:
        When our agent goes to opponent's manor, it will become Pacman and starts to eat dots.
        However, if it is captured by the defensive agent, all works will end in vain. 
        
        We optimized our offensive agent and make it can stay away from the defensive agent and
        we assume that other defensive agents would do so as well. 
        
        Instinctively, we used maze distance between our Pacman and the defensive agent as a 
        feature to calculate the incentive with this new feature. 
        However, this is not enough, our Pacman still goes straight to a defensive agent 
        sometimes if there is a lot of food behind the defensive agent. 
        
        So we added a new restricted condition to the Pacman. That is when it's very near to 
        the defensive agent, the incentive will decrease sharply because under this 
        circumstance, run for life is more important than eating foods, by this means, our 
        Pacman can keep himself away from the defensive agent quite well.
        """
        # Compute distance to the opponent ghosts
        minGhostDis=40
        onOffence = 1
        if not myState.isPacman: onOffence = 0
        #features['distanceToGhost'] = 0
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        defendersPos = []
        if onOffence == 1:
            for i in defenders:
                defendersPos.append(i.getPosition())

            distanceToGhost = []

            for i in defendersPos:
                distanceToGhost.append(self.getMazeDistance(myPos, i))
            if len(distanceToGhost) != 0 and min(distanceToGhost)<=8:
                minGhostDis = min(distanceToGhost)
                # if minGhostDis<3:
                #   features['distanceToFood'] = 0
                #   features['successorScore'] = 0
                # if minGhostDis>3:
                #   minGhostDis+=10
                # else:
                minGhostDis*=5



        features['distanceToGhost'] = minGhostDis
        defenders_scaredTimer = [i.scaredTimer for i in defenders]
        # print defenders_scaredTimer
        if defenders_scaredTimer != []:
            if min(defenders_scaredTimer) > 6:
                minGhostDis = 40
        features['distanceToGhost'] = minGhostDis
    else:
        #defensive code, activated if has enough advantage(excess score)
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

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

        # Run when you are scared, but keep an eye on the opponent
        myScaredTimer = myState.scaredTimer
        if myScaredTimer > 0:
            if features['invaderDistance'] < 4  :
                features['invaderDistance'] = -features['invaderDistance']

        agentDis=gameState.getAgentDistances()
        enemyDis=[]
        for i in self.getOpponents(successor):
          enemyDis.append(agentDis[i])
        features['toEnemy']=min(enemyDis)

        enemyInitPos=gameState.getInitialAgentPosition(self.getOpponents(successor)[0])
        initialpos=gameState.getInitialAgentPosition(self.index)
        midPosx=(enemyInitPos[0]+initialpos[0])/2
        disToMid=abs(myPos[0]-midPosx)
        disToHome=abs(initialpos[0]-myPos[0])
        if disToMid<6:
          features['disToHome']=abs(initialpos[0]-midPosx)
        else:
          features['disToHome']=disToHome
        buddyPos = successor.getAgentState(self.buddyIndex).getPosition()
        budDistance = min(self.getMazeDistance(myPos, buddyPos),10)
        if disToMid>6:
            budDistance=0
        features['distanceToBuddy'] = budDistance
    return features

  def getWeights(self, gameState, action):
    offense={'successorScore': 1000, 'distanceToFood': -1, 'distanceToHome':-10, 'distanceToGhost': 500}
    defense={'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -100, 'stop': -100, 'reverse': -2, 'toEnemy':-10,  'distanceToBuddy': 2}
    if gameState.getScore()>len(self.getFood(self.getSuccessor(gameState, action)).asList())/2:
      return defense
    return offense

class DefensiveAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

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

    # Run when you are scared, but keep an eye on the opponent
    myScaredTimer = myState.scaredTimer
    if myScaredTimer > 0:
        if features['invaderDistance'] < 4  :
            features['invaderDistance'] = -features['invaderDistance']

    agentDis=gameState.getAgentDistances()
    enemyDis=[]
    for i in self.getOpponents(successor):
      enemyDis.append(agentDis[i])
    features['toEnemy']=min(enemyDis)

    enemyInitPos=gameState.getInitialAgentPosition(self.getOpponents(successor)[0])
    initialpos=gameState.getInitialAgentPosition(self.index)
    midPosx=(enemyInitPos[0]+initialpos[0])/2
    disToMid=abs(myPos[0]-midPosx)
    disToHome=abs(initialpos[0]-myPos[0])
    if disToMid<6:
      features['disToHome']=abs(initialpos[0]-midPosx)
    else:
      features['disToHome']=disToHome

    # use a random variable to prevent stuck
    # seed=random.random()
    # if seed<0.1:
    #   features['disToHome']=abs(initialpos[0]-midPosx)

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -100, 'stop': -100, 'reverse': -2, 'toEnemy':-10, 'disToHome':1}

