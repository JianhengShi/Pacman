# AI Method 5 - Hybrid Approach: Approximate Q-Learning & Classical Planning 

This method is an implementation of the future improvements proposed in the Approximate Q-Learning Approach section. By combining the reinforcement learning approach with classical planning techniques, we effectively improved the performance of our agents and successfully defeated the staff-medium agents.

# Table of Contents
- [Hybrid Approach: Approximate Q-Learning & Classical Planning ](#Hybrid-Approach)
  * [Motivation](#motivation)
  * [Application](#application)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)

## Hybrid Approach: Approximate Q-Learning & Classical Planning 

### Motivation  
The motivation for this hybrid approach is to increase the efficiency of the agents when the agents fail to learn the optimal policy or the training for learning such an optimal policy takes too much time. For example, one of the major problems that the approximate q-learning agents had was that the agents would not carry the eaten food back home to score even after eating all the food. This was because the rewards for successful scoring were very sparse, and it would take a lot of time to train the agents. On the other hand, in situations like this where we knew what the optimal actions agents should take, classical planning is very efficient and effective.

[Back to top](#table-of-contents)

### Application  
The implementation of this hybrid approach can be found in [commit 623b202](https://github.com/COMP90054-classroom/contest-a-team/commit/623b2029ce2e02ecf1afbc671df5a9609a073c00). Comparing to the approximate Q-learning approach, two major changes were made. 

First, instead of having the same agent play both defense and offense roles, we had one agent play offense only, while the other agent plays defense only in this implementation. The agent that played offense followed an offensive strategy that focused on scoring and avoiding been eaten by opponent Ghosts. To describe this problem domain,  we used three features that were used in the approximate Q-learning approach previously, namely “disNotGo”, “foodToEat”, and “distanceToFood”, and introduced a new feature “ghostInRange”, which describes the minimum distance between the agent Pacman and the observable opponent Ghosts. On the other hand, the agent that played defense followed a defensive strategy that focused on eating the opponent Pacman. Since the agent can only observe opponents within a certain range, we used the positions of the food that was eaten by the opponents to locate the area where the opponents might be. Features that were useful in representing this agent’s state space are: 
•	Feature “disPac” describes the distance between the agent Ghost and the closest observable opponent Pacman.
•	Feature “onDefend” describes whether the agent is on its home side.
•	Feature " disFoodToDefend" describes the maximum distance between the agent Ghost and the food on the home side which we need to defend.

Another major change made in this approach is the use of classical planning. Heuristic searching was used in two cases: guiding the agent Pacman to deliver food home to score and guiding the agent Ghost to where our food was eaten by the opponents. 

[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  


#### *Disadvantages*


[Back to top](#table-of-contents)

### Future Improvements  


[Back to top](#table-of-contents)
