# AI Method 4 - Approximate Q-Learning Approach

The goal of this approach was to make the Pacman agents learn policies through experience and win the game automatically by applying the learnt policies. To achieve the goal, we deployed a model-free reinforcement learning technique: approximate q-learning. A range of features were selected to describe the environment and a set of rewards were specified to encourage the right choices of actions. However, due to the inherent complexity of the problem, the features and reward used could not fully capture the states and the outcome of our initial attempt of using approximate q-learning alone was poor. Therefore, to improve the performance, we proposed a hybrid approach by combining approximate q-learning with classical planning.

# Table of Contents
- [Approximate Q-learning](#Approximate-Q-Learning)
  * [Motivation](#motivation)
  * [Application](#application)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)

## Approximate Q-learning  

### Motivation  
There are three important properties of the Pacman problem domain:
1. The Pacman game is an MDP problem where an action can lead to more than one possible outcomes. For example, The action "stop" can lead to either the Pacman staying at the same position or being eaten by the opponents. 
2. The probabilities of the outcomes of an action are unknown. This is because the Pacman problem is a two-player game and the outcome of an action depends on the action of the other player who we do not have control of.
3. Due to the layout of the maps and moves of opponents are  unpredictable, the Pacman problem domain is very dynamic and has a potentially infinite number of states. It is impossible and unnecessary for our agents to visit every possible state during training. 

Considering these properties, we decided to try approximate q-learning as it is known for being a model-free solution for MDPs. Additionally, the use of features for state representations allows us to estimate the Q values of unseen states and eliminates the need for keeping a large Q-table.

[Back to top](#table-of-contents)

### Application  
Our initial implementation of approximate Q-learning can be found in [commit b94fb39](https://github.com/COMP90054-classroom/contest-a-team/commit/b94fb391c167ea6df73f8bd0af930c1f29910c3d).

The intuition behind this implementation is to encourage the agents to play offense and to eat as many beans as possible when they are on the opponent’s side of the map and to play defense and eat opponent Pacman when they are on their home side. 
Six features were used to represent the states in the game:
*	Features "distanceToFood" and "foodToEat" describe the distance from the position of the agent Pacman to the closest food and if the agent ate food.
*	Feature “disNotGo” describes the minimum distance between the agent Pacman and some predefined dangerous places on the map such as areas around the ghosts or dead-end alley.
*	Feature “disPac” describes the distance between the agent Ghost and the closest observable opponent Pacman.
*	Feature “disCap” describes the distance between the agent Pacman and the closest capsules on the map.
*	Feature “toScore” describes how far the agent Pacman is from the home and how much food it carries.
Since there are five actions in the problem domain and six state features per action, we ended up with a feature vector with 25 features in total. 
Positive rewards were given when the agent Pacman ate food or capsule, or the agent Ghost ate the opponent Pacman. Negative rewards were given when the agent Pacman was at the predefined dangerous places or got eaten by the opponent Ghost.

[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  
As discussed in the motivation section, there are three main advantages of using Q-learning. First, Q-learning is model free. We do not need to know the probabilities of action outcomes. Second, it does not require the agent to visit every state and store the Q-value for each state and action pair during the training. This is particularly important for a large state space such as the Pacman problem we are trying to solve here. Lastly, it allows us to generalize our solution to unseen state and action pairs through approximation. 

#### *Disadvantages*
Like other reinforcement learning approaches, Q-learning suffers from poor interpretability, which makes debugging and quality assurance much harder. When we observed unexpected behaviors of the agents, it was difficult to reason the causes or come up with improvements, especially when there were many features. 
Moreover, due to the inherent complexity of the Pacman problem, we found it was hard to find effective features for some states. For example, one of the problems of this implementation was that the agent Pacman failed to learn when to deliver the eaten food home to score. We tried to use the feature “toScore”, but it was not successful.

[Back to top](#table-of-contents)

### Future Improvements  
Based on the problems we found during the implementation, we propose two improvements:
1.	Make one agent play offense, while the other agent plays defense. This way, we can simplify the state space for each agent, and hopefully it will give us better interpretability of the agent behaviors. 
2.	For policies that are hard to learn due to the lack of effective features, we can use classical planning approaches to tell the agent directly what to do. For example, for the scoring problem mentioned above, we can specify a threshold for food carried. Once the threshold is met, the agent will use a heuristic search to deliver the food home and score before switching back to using the learnt policies.

[Back to top](#table-of-contents)
