# AI Method 3 - Heuristic Search Algorithms: Hill Climbing

We tried the Hill Climbing method to find action for the agent. As a local heuristic search method, Hill Climbing is a very intuitive and simple method, since we used it to imporve the baseline performance, as to compared with other advanced methods. Different from other method, it only considers of possible actions in the next one step, and ignored all other useless information on the layout. Therefore, it takes up very little memory and runs extremely fast. Nevertheless, its performance is very limited. Because of its short-sightedness, we can’t plan for the situation a few steps later.

# Table of Contents
- [Heuristic Search Algorithms: Hill Climbing](#Heuristic-Search-Algorithms-Hill-Climbing)
  * [Motivation](#motivation)
  * [Application](#application)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)

## Heuristic Search Algorithms: Hill Climbing  

### Motivation  
When we observe the default baseline method, we find that it works with a method similar to hill climbing. Its heuristic function is the Qvalue of each node. This Qvalue is obtained by features and weights. However, its selection of features is very limited. For example, Pacman only considered eating food and didn't consider avoiding ghost. Therefore, we intuitively think that when adding some map preprocessing steps and features, its performance can be improved.

[Back to top](#table-of-contents)

### Application  

$$h = -Q-value = - features*weightsT$$

We only modified the offensive agent. The added features are: avoid getting too close to the visible ghost, avoid entering a dead end, and choose to go home when the agnet is carrying too much food.

1. add feature of maze distance to visible ghost, assign weight of it with 5.
2. add feature of agent location in dead end or in stop status, assign weight of it with -10.
3. add feature of maze distance to home side, assign weight of -1. When going back, all other feature are 0.

Then, hill climbing will choose action which minimize heuristic h.

[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  
As a local heuristic search method, Hill Climbing is easy to implement and has a fast compuation speed. What's more, compare to A* and Qlearning and MCTS, it is the most memory saving method.


#### *Disadvantages*
Performance of Hill Climbing is limited. Thus, we just use it as a baseline improvement method.

[Back to top](#table-of-contents)

### Future improvements  

Pacman games are dynamic with many different status and situations. Therefore, different heuristic calculation methods can be used according to different situations. When choosing an action, first, set of features and their corresponding weights should be choosed by decision logic and game status, then calculate heuristics. This may improve the performance of this Hill Climbing method.

[Back to top](#table-of-contents)
