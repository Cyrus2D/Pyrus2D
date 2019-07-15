from base.main_player import main
from threading import Thread

team_name = "Pyrus"


def make_agent_runner(team_name, goalie, agents):
    agent = Thread(target=main, args=(team_name, goalie))
    agents.append(agent)


def start_main():
    agents = []
    # Todo run Goalie
    # goalie
    make_agent_runner(team_name, True, agents)

    # Players
    for i in range(10):
        make_agent_runner(team_name, False, agents)

    for agent in agents:
        agent.start()

    for agent in agents:
        agent.join()

    print("Done :\\")


if __name__ == "__main__":
    start_main()
