from lcu_driver import Connector
from random import randint
import time

#full LCU documentation
#https://lcu.vivide.re/#operation--lol-matchmaking-v1-ready-check-get

connector = Connector()

# fired when LCU API is ready to be used
@connector.ready
async def connect(connection):

    # check if the user is already logged into his account
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    if summoner.status != 200:
        print('Please login into your account and restart the script')
    else:
        while(True):
            print('Welcome,'+(await summoner.json()).get('displayName'))
            print('What would you like to do today?')
            print('Enter:')
            print('1: Set a random Chinese icon')
            print('2: Auto accept queue')
            print('3: End')
            userInput = input() 

            print()
            if(userInput == "1"):
                print('Setting new icon...')
                await set_random_icon(connection)
            elif(userInput ==  "2"):
                print("Please start the queue now")
                gamephase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
                currentphase = await gamephase.json()
                """
                #SR: 430 B 400 D 420 S/D 440 F
                #ARAM:450
                #TFT: 1090 NM 1100 ranked 1130 HR 1150 DU
                """
                #await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':1090})
                
                #start queue
                if(currentphase == 'Lobby'):
                    await connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
                    while(True):
                        currentphase = await gamephase.json()
                        print(currentphase)
                        time.sleep(2)
                        gamephase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
                        currentphase = await gamephase.json() 
                        if currentphase == 'ReadyCheck':
                            await connection.request('post', '/lol-matchmaking/v1/ready-check/accept')
            elif(userInput == "3"):
                break
            else:
                print("Invalid input, please try again")
                print()
                    
                    
#adopted from LCU_driver code example https://lcu-driver.readthedocs.io/en/latest/examples.html#
async def set_random_icon(connection):
    icon_num = randint(50, 78)
    icon = await connection.request('put', '/lol-summoner/v1/current-summoner/icon',
                                    data={'profileIconId': icon_num})
    if icon.status == 201:
        print('Set to icon number' + str(icon_num))
        print()
    else:
        print('Unknown error')
        print()


@connector.close
async def disconnect(connection):
    #await connector.stop()
    print('End')

    
# starts the connector
connector.start()
