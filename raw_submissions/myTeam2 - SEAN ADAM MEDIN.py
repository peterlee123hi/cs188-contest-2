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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#import baselineTeam as baseline
from capture import randomLayout, GameState
from layout import Layout
import numpy

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DualReflex', second = 'DualReflex'):
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
  team = [eval(first)(firstIndex), eval(second)(secondIndex)]
  team[0].register_ally(team[1])
  team[1].register_ally(team[0])
  return team

##########
# Agents #
##########
SACK = 3

#functions for everything
argmax = lambda x: max( range(len(x)), key = lambda i: x[i] )
argmin = lambda x: min( range(len(x)), key = lambda i: x[i] + ( i * 0.001) )

# GENERAL TOOLS

def cycling(agent, gameState):
    if len(agent.observationHistory) < 13:
        return 0

    previous  = agent.observationHistory[-12:]
    locations = [x.getAgentPosition(agent.index) for x in previous]

    for i in range(1, 5):
        x, y, count = i, None, 0
        current, compare = locations[-x:y], locations[-x:y]

        equivalent = lambda a, b: all( [ x == y for (x, y) in zip(a, b) ] )
        while equivalent(current, compare) and x < 13:
            count = count + 1
            x, y = (count + 1) * i, -x

            compare = locations[-x:y]

        if count > 1:
            return count - 1
    return 0

# If red is true/false, gets shortest distance to red/blue side
def get_best_dist(dister, red, gameState, pos):

  x = gameState.data.layout.width / 2
  x = (x - 1) if red else (x + 1)
  y_ops = [i for i in range(gameState.data.layout.height)]

  best = 1000000
  for y in y_ops:
    if not gameState.hasWall(x,y):
      test = dister.getMazeDistance((x,y), pos)
      if test < best:
        best = test
  return best

# Returns 1 if on home side, else 0
def on_home_side(agent, gameState):
    my_pos = gameState.getAgentPosition(agent.index)
    return gameState.isRed(my_pos) == agent.red

# Wrappers for get_best_dist, for clarity / ease of use
home_distance = lambda x, g: distance_to_home(x, g) if currently_held(x, g) > SACK else 0
def distance_to_home(agent, gameState):
    if not on_home_side(agent, gameState):
        c, p = gameState.isOnRedTeam(agent.index), gameState.getAgentPosition(agent.index)
        return get_best_dist(agent, c, gameState, p)
    return 0

def distance_to_opposite(agent, gameState):
    if on_home_side(agent, gameState):
        c, p = gameState.isOnRedTeam(agent.index), gameState.getAgentPosition(agent.index)
        return get_best_dist(agent, not c, gameState, p)
    return 0

def get_ally_distance(agent,gameState):
    my_pos = gameState.getAgentPosition(agent.index)
    ally_pos = gameState.getAgentPosition((agent.index + 2) % 4)
    return agent.getMazeDistance(my_pos,ally_pos)

# OFFENSIVE METRICS

def food_eaten(agent,gameState):
    prevState = agent.getCurrentObservation()
    if prevState == None:
        return 0
    my_pos = gameState.getAgentPosition(agent.index)
    if prevState.hasFood(my_pos[0],my_pos[1]) and agent.red != prevState.isRed(my_pos):
        return distance_to_home(agent,gameState) + 1 
    else:
        return 0

# Return the distance to the nearest food, or 0 if enough is held
food_distance = lambda x, g: nearest_food(x, g) if currently_held(x, g) < SACK else 0
def nearest_food(agent, gameState):
    foods, position = agent.getFood(gameState).asList(), gameState.getAgentPosition(agent.index)
    distance = [agent.getMazeDistance(food, position) for food in foods]
    return min(distance + [2**64])

# The number of currently consumed food by a Pacman, that isn't returned
currently_held = lambda x, g: held_food(x.index, g)
def held_food(agent_index, gameState):
    return gameState.getAgentState(agent_index).numCarrying

# Returns the relative score of the current gameState
def get_score(agent, gameState):
    red_score = gameState.getScore()
    return red_score if gameState.isOnRedTeam(agent.index) else - red_score

# Returns nearest_ghost iff Pacman is in range to be eaten by that ghost, else 0.
def can_eat_me(agent, gameState):
    my_pos = gameState.getAgentPosition(agent.index)
    if not on_home_side(agent, gameState):
        pos_opps = get_opponent_positions(agent,gameState, my_pos)
        opp_idxes = agent.getOpponents(gameState)
        opp1_dist_back = get_best_dist(agent,agent.red,gameState,pos_opps[0])
        opp2_dist_back = get_best_dist(agent,agent.red,gameState,pos_opps[1])

        opp1_to_me = agent.getMazeDistance(pos_opps[0],my_pos)
        opp2_to_me = agent.getMazeDistance(pos_opps[1],my_pos)

        my_dist_back = distance_to_home(agent, gameState)

        if (opp1_dist_back <= my_dist_back and opp1_to_me <= my_dist_back
            and (gameState.getAgentState(opp_idxes[0]) == None or
                not gameState.getAgentState(opp_idxes[0]).scaredTimer > 1)):
            return nearest_ghost(agent,gameState)
        elif (opp2_dist_back <= my_dist_back and opp2_to_me <= my_dist_back
            and (gameState.getAgentState(opp_idxes[1]) == None or
                not gameState.getAgentState(opp_idxes[1]).scaredTimer > 1)):
            return nearest_ghost(agent,gameState)
        else:
            return 0
    else:
        return 0

# Returns distance of nearest ghost to pacman if not on his side
def nearest_ghost(agent, gameState):
    my_pos = gameState.getAgentPosition(agent.index)
    if gameState.isRed(my_pos) != agent.red:
        pos_opps = get_opponent_positions(agent,gameState,my_pos)
        return max(1.0 / (agent.getMazeDistance(pos_opps[0],my_pos) + .01),
            1.0 / (agent.getMazeDistance(pos_opps[1],my_pos) + .01))
    return 0

# Returns if I have been eaten
def me_eaten(agent, gameState):
    prevState = agent.getCurrentObservation()
    if prevState != None:
        if was_eaten(agent.index,gameState,prevState):
            print('eaten')
            return 1
        else:
            return 0
    else:
        return 0

# Returns if the agent at a given index was eaten
def was_eaten(agent_index, s, s_prime):
    old_pos = s.getAgentPosition(agent_index)
    new_pos = s_prime.getAgentPosition(agent_index)
    return (abs(old_pos[0] - new_pos[0]) + abs(old_pos[1] - new_pos[1]) > 1)

# Returns nearest distance to capsule
def my_nearest_capsule(agent,gameState):
    #first checks if a capsule was eaten
    my_pos = gameState.getAgentPosition(agent.index)
    prevState = agent.getCurrentObservation()
    if prevState == None:
        return 0
    caps = agent.getCapsules(gameState)
    if (agent.red and len(prevState.getBlueCapsules()) != len(caps)
        ) or (not agent.red and len(prevState.getRedCapsules()) != len(caps)):
        return 0

    nearest = 10000

    for cap in caps:
        test = agent.getMazeDistance(cap,my_pos)
        if test < nearest:
            nearest = test
    return nearest

# DEFENSIVE METRICS

# Returns distance to ghost if in range and we are the best for the job
def attack_ghost(agent, gameState):
    my_pos = gameState.getAgentPosition(agent.index)
    ally_pos = gameState.getAgentPosition((agent.index + 2) % 4)
    opps = get_opponent_positions(agent,gameState,my_pos)
    to_kill = []
    for opp in opps:
        if gameState.isRed(opp) == agent.red:
            to_kill.append(opp)

    my_scores = []
    al_scores = []
    for kill in to_kill:
        dist_to_me = agent.getMazeDistance(my_pos,kill)
        my_dist_back = get_best_dist(agent,agent.red,gameState,my_pos)
        their_dist_back = get_best_dist(agent,agent.red,gameState, kill)
        my_scores.append(dist_to_me + .01 * (my_dist_back - their_dist_back))

        dist_to_al = agent.getMazeDistance(ally_pos,kill)
        al_dist_back = get_best_dist(agent,agent.red,gameState,ally_pos)
        al_scores.append(dist_to_al + .01 * (al_dist_back - their_dist_back))

    if len(to_kill) == 0:
        return 0
    elif len(to_kill) == 1:
        if al_scores[0] < my_scores[0]:
            return 0
        else:
            return my_scores[0]
    else:
        if my_scores[0] + al_scores[1] < my_scores[1] + al_scores[0]:
            return my_scores[0]
        else:
            return my_scores[1]

# Returns if we can eat ghost here
def eat_ghost(agent, gameState):
    my_pos = gameState.getAgentPosition(agent.index)
    prevState = agent.getCurrentObservation()
    if prevState == None:
        return 0
    opps = agent.getOpponents(gameState)
    for opp in opps:
        if prevState.getAgentPosition(opp) != None and gameState.isRed(my_pos) == agent.red:
            if gameState.getAgentPosition(opp) != prevState.getAgentPosition(opp):
                return 1
    return 0

# Returns if opponent is nearer to any of their capsules then us
def opp_nearest_capsule(agent,gameState):
    caps = agent.getCapsulesYouAreDefending(gameState)
    my_pos = gameState.getAgentPosition(agent.index)
    pos_opps = get_opponent_positions(agent,gameState,my_pos)
    other_pos = gameState.getAgentPosition((agent.index + 2) % 4)
    for cap in caps:
        if min(agent.getMazeDistance(my_pos,cap),
            agent.getMazeDistance(other_pos,cap)) >= min(
            agent.getMazeDistance(pos_opps[0],cap),
            agent.getMazeDistance(pos_opps[1],cap)):
            return 1
    return 0


# INFERENCE

# Updates opponent location distribution
def update_loc(gameState, distrib, idx, my_pos):
  if gameState.getAgentPosition(idx) != None:
    return set([gameState.getAgentPosition(idx)])

  noisyDist = gameState.getAgentDistances()[idx]
  new_distrib = set()
  for pos in distrib:
    if util.manhattanDistance(pos,my_pos) < noisyDist:
      new_distrib.add(pos)
    new_tests = [(pos[0] + 1, pos[1]),(pos[0] - 1, pos[1]),
                  (pos[0], pos[1] + 1),(pos[0], pos[1] - 1)]
    for new_pos in new_tests:
      if util.manhattanDistance(new_pos,my_pos) < noisyDist and not gameState.isWall(new_pos):
        new_distrib.add(new_pos)
  return new_distrib

def get_opponent_positions(agent, gameState, my_pos):
    opps = []
    for idx in agent.opp_dic:
        agent.opp_dic[idx] = update_loc(gameState, agent.opp_dic[idx], idx, my_pos)
        opps.append(random.choice(list(agent.opp_dic[idx])))
    return opps

# was supposed to tell us the best weights to use. it didn't work well
class MDP:

    Overall =   [ cycling, get_ally_distance, get_score]

    Offensive = [ food_distance, food_eaten, home_distance,
                  can_eat_me, me_eaten, my_nearest_capsule ]

    Defensive = [attack_ghost, eat_ghost, opp_nearest_capsule ]

    functions = Overall + Offensive + Defensive
    normative_sign = [-1.0, 1.0, 1.0] + [-1.0, 1.0, -1.0, -1.0, -1.0, -1.0] + [-1.0, 1.0, -1.0]

    def __init__(self, agent):
        self.agent = agent
        self.policy  = {}
        self.weights = MDP.normative_sign

        self.agents = self.agent.getTeam(self.agent.startState)
        self.opponents = self.agent.getOpponents(self.agent.startState)

    def transition(self, gameState, action):
        possible_states = set()
        ally = self.agent.ally

        first_step = gameState.generateSuccessor(self.agent.index, action)
        g_1_moves = first_step.getLegalActions(self.opponents[0])
        for a in g_1_moves:

            second_step = first_step.generateSuccessor(self.opponents[0], a)
            ally_moves = second_step.getLegalActions(ally.index)
            for x in ally_moves:

                third_step = second_step.generateSuccessor(ally.index, x)
                g_2_moves = third_step.getLegalActions(self.opponents[1])
                for b in g_2_moves:

                    end_state = third_step.generateSuccessor(self.opponents[1], b)
                    possible_states.add(end_state)

        return list(possible_states)

    def q_template(self, successors):
        q_vectors  = [ numpy.array([ f(self.agent, s_prime) for f in MDP.functions ]) for s_prime in successors ]
        q_vector   = sum( q_vectors ) / len( q_vectors )

        return list(q_vector)

    def q_value(self, gameState, action):
        q_vector  = self.q_template( self.transition(gameState, action) )
        q_vector  = [ self.weights[i] * q_vector[i] for i in range(len(q_vector))]

        return sum( q_vector )

    def value(self, gameState):
        actions = gameState.getLegalActions(self.agent.index)
        return max( [self.q_value(gameState, action) for action in actions] )

    def reward(self, s, successors):
        rewards = 0

        for s_prime in successors:
            pellet_reward = held_food(self.agent.index, s_prime) - held_food(self.agent.index, s)

            eaten_reward  = - ( held_food(self.agent.index, s) + self.agent.penalty ) if was_eaten(self.agent.index, s, s_prime) else 0
            eating_reward = sum([ held_food(opponent, s) for opponent in self.opponents if was_eaten(opponent, s, s_prime)])

            scores_reward = get_score(self.agent, s_prime)
            rewards += pellet_reward + eaten_reward + scores_reward

        return - (rewards / len(successors))

    def policy_extraction(self, gameState):
        actions = [x for x in gameState.getLegalActions(self.agent.index) if x != "Stop"]
        actions.sort(key = lambda x: random.random())
        index = argmax( [self.q_value(gameState, action) for action in actions] )

        return actions[index]

    def policy_evaluation(self):
        states  = self.policy.keys()

        alpha, beta, gamma = [], [], []
        for s in states:
            s_prime = self.transition( s, self.policy[s] )

            alpha_row = [ f(self.agent, s) for f in MDP.functions ]
            beta_row  = [ self.reward(s, s_prime) ]
            gamma_row = [ 0.9 * x for x in self.q_template(s_prime) ]

            alpha.append(alpha_row)
            beta.append(beta_row)
            gamma.append(gamma_row)

        A = numpy.array(gamma) - numpy.array(alpha)
        self.weights = numpy.linalg.lstsq(A, beta, rcond=-1)
        self.weights =  list(self.weights[0].T[0])

    def policy_improvement(self):
        states = self.policy.keys()
        policy = {}

        for state in states:
            policy[state] = self.policy_extraction(state)

        return policy

    def policy_iteration(self, attempt=0):
        self.policy_evaluation()
        policy = self.policy_improvement()

        if policy != self.policy and attempt < 25:
            self.policy = policy
            self.policy_iteration(attempt + 1)

    def generate_sample(self, gameState, myTeam, trainingTeam):
        alpha, beta = {}, {}

        merge = [None] * (len(myTeam) + len(trainingTeam))
        merge[::2]  = myTeam
        merge[1::2] = trainingTeam

        threshold = 0.5
        while (not gameState.isOver()) and gameState.data.timeleft > 0:
            for agent in merge:
                action = agent.chooseAction(gameState, threshold) if agent in myTeam else agent.chooseAction(gameState)

                if agent == myTeam[0]: alpha[gameState] = action;
                if agent == myTeam[1]: beta[gameState]  = action;

                gameState = gameState.generateSuccessor(agent.index, action)
            threshold = threshold + ( gameState.data.timeleft * 0.0005 )

        myTeam[0].mdp.policy = alpha
        myTeam[1].mdp.policy = beta

    def filter_by_sign(self):
        signs, n = [ int( x / float(abs(x)) ) if x != 0 else 0 for x in self.weights ], range( len(self.normative_sign) )
        weights  = [ self.weights[i] if signs[i] == self.normative_sign[i] else 0 for i in n ]

        return weights

    def maximal_satisfying_weights(self, other):
        T_a = self.filter_by_sign()
        T_b = other.filter_by_sign()

        self.weights  = [ (T_a[i] + T_b[i]) / 2 for i in range( len(T_a) ) ]
        other.weights = self.weights
        return self.weights

'''
We have a bunch of features and a bunch of weights and we make the move that results
in the largest value of features dot product with weights.

The features in order of priority are:
1. Not getting eaten
2. Eating a pacman
2.5. Maximizing score
3. Not getting stuck in a cycle. Look to see if we would continue a cycle
and do something different if we are stuck
4. Not letting the opponent get a capsule
5. Heading towards a ghost on my side
6. Preventing a ghost from being in range to eat me
7. Heading back if a pacman has eaten 3 or more food
8. Eating food
9. Getting close to food
10. Staying away from my ally
'''
class DualReflex(CaptureAgent):
  """
  """

  def __init__( self, index, timeForComputing = .2 ):
    CaptureAgent.__init__(self,index,timeForComputing = .1)

    self.to_red_dists = {}
    self.to_blue_dists = {}
    self.opp_dic = {}

  def register_ally(self, ally):
      self.ally = ally

  def register_mdp(self):
      self.mdp = MDP(self)

      team_weights = [-10000000,.01,100000] + [-.1,25,-20,-1000,-10000000,0] + [-1000,1000000,-10000]
      self.mdp.weights = team_weights

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

    self.startState = gameState
    self.penalty = distance_to_opposite(self, self.startState)

    self.register_mdp()
    #registers opponent locations
    oppInds = self.getOpponents(self.startState)
    for idx in oppInds:
      self.opp_dic[idx] = {gameState.getInitialAgentPosition(idx):1}

    #creates dictionary of distances from each to square to other side
    for r in range(gameState.data.layout.width):
      for c in range(gameState.data.layout.height):
        if not gameState.hasWall(r,c):
          self.to_red_dists[(r,c)] = get_best_dist(self,True, gameState, (r,c))
          self.to_blue_dists[(r,c)] = get_best_dist(self,False, gameState, (r,c))

  def chooseAction(self, gameState, threshold=1.0):

    if random.random() < threshold:
        return self.mdp.policy_extraction(gameState)
    return random.choice( gameState.getLegalActions(self.index) )

'''
# Learning and Pseudo-Planning
def learning_protocol():
  agents = createTeam(0, 2, False)
  opponents = baseline.createTeam(1, 3, True)

  startState = GameState()
  startState.initialize( Layout(randomLayout().split('\n')), 4 )
  startState.data.timeleft = 300 * len(agents + opponents)

  for agent in agents + opponents:
      agent.registerInitialState(startState)

  for i in range(50):
      agents[0].mdp.generate_sample(startState, agents, opponents)
      for agent in agents:
          agent.mdp.policy_iteration()
      print agents[0].mdp.maximal_satisfying_weights(agents[1].mdp)
'''
