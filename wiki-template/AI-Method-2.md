# AI Method 2 - Reinforcement Learning Approach

The goal of this approach was to make the Pacman agents learn policy through experience and win the game automatically by applying the learnt policy. To achieve the goal, we deployed a model-free reinforcement learning technique: approximate q-learning. A range of features were selected to describe the environment and a set of rewards were specified to encourage the right choices of actions. However, due to the inherent complexity of the problem, the features and reward used could not fully capture the states and the outcome of our initial attempt of using approximate q-learning alone was poor. Therefore, to improve the performance, we adopted a hybrid approach by combining approximate q-learning with classical planning and achieved relatively better performance.

# Table of Contents
- [Approximate Q-learning](#Approximate-Q-Learning)
  * [Motivation](#motivation)
  * [Application](#application)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)
<!-- - [Hybrid Approach: Approximate Q-learning & Classical Planning](#Hybrid-Approach)
  * [Motivation](#motivation)
  * [Application](#application)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements) -->

## Approximate Q-learning  

### Motivation  
There are three important properties of the Pacman problem domain:
1. The Pacman game is an MDP problem where an action can lead to more than one possible outcomes. For example, The action "stop" can lead to either the Pacman staying at the same position or being eaten by the opponents. 
2. The probabilities of the outcomes of an action are unknown. This is because the Pacman problem is a two-player game and the outcome of an action depends on the action of the other player who we do not have control of.
3. Due to the layout of the maps and moves of opponents are  unpredictable, the Pacman problem domain is very dynamic and has a potentially infinite number of states. It is impossible and unnecessary for our agents to visit every possible state during training. 

Considering these properties, we decided to try approximate q-learning as it is known for being a model-free solution for MDPs. Additionally, the use of features for state representation allows us to estimate the Q values of unseen states and eliminates the need for keeping a large Q-table.


[Back to top](#table-of-contents)

### Application  

[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  


#### *Disadvantages*

[Back to top](#table-of-contents)

### Future improvements  

[Back to top](#table-of-contents)




## Hybrid Approach: Approximate Q-learning & Classical Planning

### Motivation  


[Back to top](#table-of-contents)

### Application  

[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  


#### *Disadvantages*

[Back to top](#table-of-contents)

### Future improvements  

[Back to top](#table-of-contents)
