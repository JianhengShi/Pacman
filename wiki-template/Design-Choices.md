# Design Choices

## General Comments

We compared several AI planning algorithms or hybrid algorithms with their performance in Pacman game. For seeing implemetation of these methods, please go to seperate wiki file of each method. 

![Comparison of Methods](images/Methods_comparison.png)

In the end, we chose the first method with the best performance.


## Comments per topic




## Offense

Through experiments, we find that aggressive strategy of eating dots is more effective, namely, both agents play the role of attackers at most of the time. Because when facing intelligent opponents, defense is very difficult and inefficient. As the saying goes: attack is the best defense. You can't win the Pacman game by defending.

This is comparison between our less-denfence version and more-defence version:
* Less-denfence version:
![Less-denfence version](images/10-19.png)
* More-denfence version:
![More-denfence version](images/10-13.png)

## Defense
For defense cases, the agent first find a path to enemy's Pacman. If there is no feasible path, then the agent will go to location of last dot eaten by enemy's Pacman.