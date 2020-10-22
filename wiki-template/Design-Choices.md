# Design Choices

## General Comments

We compared several AI planning algorithms or hybrid algorithms with their performance in Pacman game. For seeing implemetation of these methods, please go to seperate wiki file of each method. 

![Comparison of Methods](images/Methods_comparison.png)

In the end, we chose the first method with the best performance.


## Comments per topic

* A* Search with Complete Decision Logic:

This is the method we focus on with whole cycle of evolution. For details, see [AI-Method-1](https://github.com/COMP90054-classroom/contest-a-team/blob/master/wiki-template/AI-Method-1.md) and [Evolution](https://github.com/COMP90054-classroom/contest-a-team/blob/master/wiki-template/Evolution.md). It has a really high performance in the contest. Besides, its high interpretability helps us to optimize the strategy, including the tuning of parameters and the change of behavior. However, because Heuristic Search Algorithms is too simple and straightforward, our agent cannot learn in a large number of competitions, namely, it is not inherently intelligent. Thus, it took us a lot of time and energy to debug and improve this method.

Performance in the contest: Around staff team super
![Method 1](images/10-19.png)

* Hill Climbing:

This is simple idea we first came out with intuitive think of improving the default baseline method. For details, see [AI-Method-3](https://github.com/COMP90054-classroom/contest-a-team/blob/master/wiki-template/AI-Method-3.md). Its implementation is simple and straightforward, but its performance is fairly limited. Maybe we can improve its performance by implementing more presice decision logic for different cases. However, We did not focus on this method because it was easily defeated by our other methods.

Performance in the contest: Around staff team basic

* Monte Carlo Tree Search:

We came out with this method because we knew from the lectures that Monte Carlo Tree Search is very suitable for real-time AI planning for dynamic games like Pacman. For details, see [AI-Method-4](https://github.com/COMP90054-classroom/contest-a-team/blob/master/wiki-template/AI-Method-4.md). We added MCTS to the main method as an attempt. It turns out that it can help simplify the complicated logic of using only A* searching. However, it is not significantly improved in performace compared with the main method, so we did not choose it finally.

Performance in the contest: Above staff team top
![Method 4](images/MCTS.png)

* Approximate Q Learning:

This is our tentative verification of Q Learning methods. It is a model-free reinforcement learning technique to make the Pacman agents learn policies through experience and win the game automatically by applying the learnt policies. For details, see [AI-Method-5](https://github.com/COMP90054-classroom/contest-a-team/blob/master/wiki-template/AI-Method-5.md). However, due to the inherent complexity of the problem, the features and reward used could not fully capture the states and the outcome of our initial attempt of using approximate q-learning alone was poor. Therefore, to improve the performance, we proposed a hybrid approach by combining approximate q-learning with classical planning which is the following method.

Performance in the contest: Above staff team basic





## Offense

Through experiments, we find that aggressive strategy of eating dots is more effective, namely, both agents play the role of attackers at most of the time. Because when facing intelligent opponents, defense is very difficult and inefficient. As the saying goes: attack is the best defense. You can't win the Pacman game by defending.

This is comparison between our less-denfence version and more-defence version:
* Less-denfence version:
![Less-denfence version](images/10-19.png)
* More-denfence version:
![More-denfence version](images/10-13.png)

## Defense
For defense cases, the agent first find a path to enemy's Pacman. If there is no feasible path, then the agent will go to location of last dot eaten by enemy's Pacman.