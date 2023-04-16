# PYRUS2D

Robocup Soccer Simmulation 2D Python Base Code 

---

PYRUS2D is the first Python base code (sample team) for RoboCup Soccer 2D Simulator. 
This project is implemented by members of CYRUS soccer simulation 2D team.
By using this project, a team includes 11 players and one coach 
can connect to RoboCup Soccer Server and play a game. 
Also, researchers can use the trainer to control the server for training proposes.


### Dependencies
#### RoboCup Soccer Simulation Server and Monitor
Install rcssserver and rcssmonitor (soccer window for debugging proposes)
- rcssserver: [https://github.com/rcsoccersim/rcssserver](https://github.com/rcsoccersim/rcssserver)
- rcssmonitor: [https://github.com/rcsoccersim/rcssmonitor](https://github.com/rcsoccersim/rcssmonitor)
- soccer window: [https://github.com/helios-base/soccerwindow2](https://github.com/helios-base/soccerwindow2)
#### Python requirements
- Python v3.9
- coloredlogs==15.0.1
- pyrusgeom==0.1.2
- scipy==1.10.1

```bash
pip install -r requirements.txt
```

### How to start quickly?
#### Run team (11 players and 1 coach)
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

### Start team by arguments
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


### Useful links:
- CYRUS team: [https://cyrus2d.com/](https://cyrus2d.com/)
- RoboCup: [https://www.robocup.org/](https://www.robocup.org/)
- Soccer Simulation 2D League: [https://rcsoccersim.github.io/](https://rcsoccersim.github.io/)
- Server documentation: [https://rcsoccersim.readthedocs.io/](https://rcsoccersim.readthedocs.io/)

### Cite and Support 
