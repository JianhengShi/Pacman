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
The motivation for this hybrid approach is to increase the efficiency of the agents when they fail to derive optimal policy from learning. There are many reasons for such failures, such as unrepresentative state features, sparse reward, or lack of training. When such failure occurs, the effectiveness and efficiency of the agents suffer dramatically. For example, one of the major problems that the approximate q-learning agents had was that the agents failed to learn the eaten food needed to be carried back home for scoring, which directly impacted the performance of the agents. Therefore, in situations like this, the agents need an alternative method to choose actions and this is when classical planning comes into play.

[Back to top](#table-of-contents)

### Application  
The implementation of this hybrid approach can be found in [commit 623b202](https://github.com/COMP90054-classroom/contest-a-team/commit/623b2029ce2e02ecf1afbc671df5a9609a073c00). Comparing to the approximate Q-learning approach, two major changes were made. 

First, classical planning was used when the agents fail to learn optimal policies due to sparse reward. More specifically, in this implementation, the heuristic searching was used in two cases: guiding the agent Pacman to deliver food home to score and guiding the agent Ghost to where our food was eaten by the opponents. 

Second, instead of having the same agent play both defense and offense roles, we had one agent play offense only, while the other agent plays defense only in this implementation. The agent that played offense followed an offensive strategy that focused on scoring and avoiding been eaten by opponent Ghosts. To describe this problem domain,  we used three features that were used in the approximate Q-learning approach previously, namely “disNotGo”, “foodToEat”, and “distanceToFood”, and introduced a new feature “ghostInRange”, which describes the minimum distance between the agent Pacman and the observable opponent Ghosts. On the other hand, the agent that played defense followed a defensive strategy that focused on eating the opponent Pacman. Since the agent can only observe opponents within a certain range, we used the positions of the food that was eaten by the opponents to locate the area where the opponents might be. Features that were useful in representing this agent’s state space are: 
*	Feature “disPac” describes the distance between the agent Ghost and the closest observable opponent Pacman.
*	Feature “onDefend” describes whether the agent is on its home side.
*	Feature "disFoodToDefend" describes the maximum distance between the agent Ghost and the food on the home side which we need to defend.

[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  
This approach has effectively improved the performance of the agents. The classical planning techniques complemented the approximate Q-learning by providing a relatively efficient action plan in certain situations where agents failed to derive optimal policies from learning. 
Moreover, by having one agent play one role only, the problem domain for each agent was simplified and the interpretability of the agent behaviors was improved. 

#### *Disadvantages*


[Back to top](#table-of-contents)

### Future Improvements  


[Back to top](#table-of-contents)
