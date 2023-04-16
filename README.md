# PYRUS2D

## Robocup Soccer Simmulation 2D Python Base Code


PYRUS2D is the first Python base code (sample team) for RoboCup Soccer 2D Simulator.
This project is implemented by members of CYRUS soccer simulation 2D team.
By using this project, a team includes 11 players and one coach can connect to RoboCup Soccer Server and play a game.
Also, researchers can use the trainer to control the server for training proposes.

---
## Dependencies



### RoboCup Soccer Simulation Server and Monitor

Install rcssserver and rcssmonitor (soccer window for debugging proposes)

- rcssserver: [https://github.com/rcsoccersim/rcssserver](https://github.com/rcsoccersim/rcssserver)
- rcssmonitor: [https://github.com/rcsoccersim/rcssmonitor](https://github.com/rcsoccersim/rcssmonitor)
- soccer window: [https://github.com/helios-base/soccerwindow2](https://github.com/helios-base/soccerwindow2)

### Python requirements

- Python v3.9
- coloredlogs==15.0.1
- pyrusgeom==0.1.2
- scipy==1.10.1

```bash
pip install -r requirements.txt
```

---

## Quick Start

### Run team (11 players and 1 coach)

To run the team there are some options,

- running agents(players and coach execute separately)

```bash
cd Pyrus2D
./start.sh
```

- running the agents by Python (or running them separately in PyCharm)

```bash
cd Pyrus2D
python team/main_player.py (11 times)
python team/main_coach.py
```

- running the agents by using one Python main process

```bash
cd Pyrus2D
python main.py
```


## Start team by arguments


To modify team configuration, you can pass the arguments or update ```team_config.py```.

Configurations are listed bellow:

```bash
# To change the teamname (default is PYRUS):
-t|--teamname TeamName 

# Determines if the connecting player is goalie or not. (take no parameters)
-g|--goalie 

# To change Output of loggers(Default is std):
#   - std: loggers print data on the terminal -> std output
#   - textfile: loggers write on the files based on players unum. (player-{unum}.txt, player-{unum}.err)
-o|--out [std|textfile] 

# change the host(serve) ip adderess. (defualt is localhost)
-H|--host new_ip_address

# change the player port connection. (default is 6000)
-p|--player-port new_port

# change the coach port connection. (default is 6002) 
-P|--coach-port new_port

# change the trainer port connection. (default is 6001)
--trainer-port new_port

```

---

## Useful links

- CYRUS team: [https://cyrus2d.com/](https://cyrus2d.com/)
- RoboCup: [https://www.robocup.org/](https://www.robocup.org/)
- Soccer Simulation 2D League: [https://rcsoccersim.github.io/](https://rcsoccersim.github.io/)
- Server documentation: [https://rcsoccersim.readthedocs.io/](https://rcsoccersim.readthedocs.io/)

## Related Papers

- Zare N, Amini O, Sayareh A, Sarvmaili M, Firouzkouhi A, Rad SR, Matwin S, Soares A. Cyrus2D Base: Source Code Base for RoboCup 2D Soccer Simulation League. InRoboCup 2022: Robot World Cup XXV 2023 Mar 24 (pp. 140-151). Cham: Springer International Publishing. [link](https://arxiv.org/abs/2211.08585)
- Zare N, Sarvmaili M, Sayareh A, Amini O, Matwin S, Soares A. Engineering Features to Improve Pass Prediction in Soccer Simulation 2D Games. InRobot World Cup 2022 (pp. 140-152). Springer, Cham. [link](https://www.researchgate.net/profile/Nader-Zare/publication/352414392_Engineering_Features_to_Improve_Pass_Prediction_in_Soccer_Simulation_2D_Games/links/60c9207fa6fdcc0c5c866520/Engineering-Features-to-Improve-Pass-Prediction-in-Soccer-Simulation-2D-Games.pdf)
- Zare N, Amini O, Sayareh A, Sarvmaili M, Firouzkouhi A, Matwin S, Soares A. Improving Dribbling, Passing, and Marking Actions in Soccer Simulation 2D Games Using Machine Learning. InRobot World Cup 2021 Jun 22 (pp. 340-351). Springer, Cham. [link](https://www.researchgate.net/profile/Nader-Zare/publication/355680673_Improving_Dribbling_Passing_and_Marking_Actions_in_Soccer_Simulation_2D_Games_Using_Machine_Learning/links/617971b0a767a03c14be3e42/Improving-Dribbling-Passing-and-Marking-Actions-in-Soccer-Simulation-2D-Games-Using-Machine-Learning.pdf)
- Akiyama, H., Nakashima, T.: Helios base: An open source package for the robocup soccer 2d simulation. In Robot Soccer World Cup 2013 Jun 24 (pp. 528-535). Springer, Berlin, Heidelberg.


## Cite and Support

Please don't forget to cite our papers and star our GitHub repo if you haven't already!
## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
