# AI Method 1 - Heuristic Search Algorithms: A*

In Heuristic Search Algorithms, we use the A* method to find a path for the agent. Different from the classic method, since the Pacman game is dynamic, a list containing the dangerous area defined under different circumstances will be passed into this method to prevent Pacman from falling into danger. The specific code is as follows:
```python
    def aStarSearch(self, gameState, start, goal, dangerous_list):
        ...
        if not gameState.getWalls()[int(x + dx)][int(y + dy)] and (int(x + dx), int(y + dy)) not in dangerous_list:
        ...
```
When searching for successors, each candidate node will be judged whether it belongs to the dangerous area.

Additionally, our A* algorithm uses maze distance as the heuristic method.

# Table of Contents
- [Heuristic Search Algorithms: A*](#heuristic-search-algorithms-A*)
  * [Motivation](#motivation)
  * [Application](#application)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)

## Heuristic Search Algorithms: A*
### Motivation  
Heuristic Search Algorithms has become our first choice for this project due to its simplicity and short computation time. Moreover, compared with Q-learning and MCST methods, the output of Heuristic Search Algorithms is easy to interpret, which provides us with a reference when debugging and adjusting competition strategies. Besides, Heuristic Search Algorithms does not need to be combined with specific action functions (such as offense and defense), and are independent of each other in execution, which reflects a high degree of abstraction, thereby improving the efficiency of project completion.

[Back to top](#table-of-contents)

### Application  
Heuristic Search Algorithms has been widely used in our project. Since its function is only to output routes based on the location, dangerous area and target location, it can be applied to almost all places. Specifically, when attacking, the target location is the position of the opposite dot:
```python
    def eatDots(self, gameState)::
        ...
        dot_dic.update({dot: len(self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [dot], self.notGo(gameState)))})
        ...
```
when being chased, the target location is the capsule, or a point on the centerline of the map:
```python
    def capOrHome(self, gameState):
        ...
        path = self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [capsule], self.notGo(gameState))
        ...
        path = self.aStarSearch(gameState, p, [centerline_point], self.notGo(gameState))
        ...
```
when defending, the target location is the location of the opposite Pacman, or the position of our dot that was just eaten:
```python
    def catch(self, gameState):
        ...
        path = self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [oppo_pacman], self.notGo(gameState))
        ...
        path = self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [eatenFood[0]], self.notGo(gameState))
        ...
```
Besides, many functions in the project handling special cases also more or less use Heuristic Search Algorithms.

[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  
As mentioned before, the path output of Heuristic Search Algorithms are easy to interpret, which helps us to optimize the strategy, including the tuning of parameters and the change of behavior. When dealing with different situations, we don't need to consider the algorithm itself, but only need to compare specific behaviors to continuously improve the agent's performance in the game. At the same time, due to the predictability of the results of Heuristic Search Algorithms, we do not need to simulate and train the small cases one by one, which saves our time significantly.
#### *Disadvantages*
However, because Heuristic Search Algorithms is too simple and straightforward, our agent cannot learn in a large number of competitions. It executes only the commands we give, and does not adjust itself to deal with different situations, that is, our agent is not inherently intelligent. The cost of this is that we need to watch a large number of game replays to analyze different situations, and come up with corresponding countermeasures for the agent to execute. This has increased our workload to a certain extent. In addition, because some situations are too complicated, the addition of behaviors may bring unexpected conflicts, which has also become a major obstacle to our improvement of the project.

[Back to top](#table-of-contents)

### Future improvements  
We plan to summarize and classify all the currently known conditions to achieve a certain generalization and prevent the project from becoming more complicated during the improvement process. Furthermore, due to the limitations of Heuristic Search Algorithms that prevent the agent from learning by itself, we may use other AI methods (such as Reinforcement Learning) to deal with some specific situations.

[Back to top](#table-of-contents)
