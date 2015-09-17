# DungeonGenerator
Procedural Dungeon Generation with Python and Pygame

![Screenshot](https://raw.githubusercontent.com/JnyJny/DungeonGenerator/master/screenshots/Screen%20Shot%202015-09-15%20at%2015%20Sep%204.21.26%20PM.png)

I wrote this after reading an article on ["Procedural Dungeon Generation Algorithm"](http://gamasutra.com/blogs/AAdonaac/20150903/252889/Procedural_Dungeon_Generation_Algorithm.php).

To be honest, I'm a sucker for graph paper dungeons and the word 'algorithm' so it was impossible for me
to avoid implementing the dungeon generator described in the article.

This code is very dependent on the excellent [pygame](http://pygame.org) framework.

The Generate module will put up a window and draw each phase of the algorithm as described in the
article with it's animated gifs.  The StateMachine module was something I reused from my [pacman](https://github.com/JnyJny/pacman) implementation
to help keep everything from happening at once. Dungeon is the interesting part, describing a Dungeon class that
manages Room objects. 

The biggest diversion between the article and my implementation is my failure to implement a Delauny triangulation
to build a guarunteed connected graph.  My graph uses a closest neighbor function that mostly generates connected
graphs but sometimes results in two islands.

A lesser diversion is the hallway construction where I admit I got lazy.  My only defense is it looks like a more
"Dwarven" dungeon to my eye, so I kept it.

I hope this provides someone some amusement, I enjoyed writing it. 
