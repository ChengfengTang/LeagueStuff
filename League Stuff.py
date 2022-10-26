from lcu_driver import Connector
from random import randint
import time

#full LCU documentation
#https://lcu.vivide.re/#operation--lol-matchmaking-v1-ready-check-get

connector = Connector()

# fired when LCU API is ready to be used
@connector.ready
async def connect(connection):
    #adopted from LCU_driver code example https://lcu-driver.readthedocs.io/en/latest/examples.html#
    # check if the user is already logged into his account
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    if summoner.status != 200:
        print('Please login into your account and restart the script')
    else:
        championId = 350
        while(True):
            #print(await summoner.json())
            print('Welcome,'+(await summoner.json()).get('displayName'))
            print('What would you like to do today?')
            print('Enter:')
            print('1: Set a random Chinese icon')
            print('2: Auto accept')
            print('3: Create Lobby')
            print('4: Preset Champs/Skins')
            print('5: Check Teammates Stats during Champ-Select')
            print('6: Exit')
            userInput = input() 

            print()
            if(userInput == "1"):
                print('Setting new icon...')
                await set_random_icon(connection)
            elif(userInput ==  "2"):
                print("Attempting to start the queue now")
                gamephase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
                currentphase = await gamephase.json()

                #print(currentphase)
                """
                gamephase: None, Lobby, Matchmaking, InProgress, ChampSelect, ReadyCheck
                """
                #start the queue
                if(currentphase == 'Lobby' or currentphase == 'Matchmaking' or currentphase == 'ChampSelect' ):
                    await connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
                    while(True):
                        #await connection.request('post', '/lol-game-client-chat/v1/party-messages', data ={'message':"xd"})
                        currentphase = await gamephase.json()
                        print(currentphase)
                        time.sleep(2)
                        gamephase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
                        currentphase = await gamephase.json() 
                        if currentphase == 'ReadyCheck':
                            await connection.request('post', '/lol-matchmaking/v1/ready-check/accept')
                        if currentphase == 'ChampSelect': # Draft: ban pick champs/skins, ARAM: rerolls, check teammates' rerolls, ranked: check winrate...etc
                            if championId != 0:
                                session = await connection.request('get', '/lol-champ-select/v1/session')
                                session = await session.json()
                                #print(session)
                                for action in session['actions'][0]:
                                    if action['championId'] == 0:
                                        # Pick champion
                                        await connection.request('patch', '/lol-champ-select/v1/session/actions/%d' % action['id'],data = {'championId': championId})
                                        await connection.request('post', '/lol-champ-select/v1/session/actions/%d' % action['id'] + '/complete',data = {'championId': championId})
                                        #await connection.request('post', '/lol-game-client-chat/v1/party-messages', data ={'message':"xd"})
                                        
                            break
                    await connector.stop()
                            
                else:
                    print("Please create a lobby manually or using the commands first")
                    print()
            elif(userInput == "3"):
                gamephase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
                currentphase = await gamephase.json()
                if(currentphase == 'Lobby' or currentphase == 'None'):
                    print("Please enter the code corresponding to the game mode that you would like to create a lobby for")
                    print("Summoners' Rift: Draft - 400, Blind - 430, Ranked solo/duo - 420, Ranked Flex - 440")
                    print("ARAM: 450")
                    print("TFT: Normal - 1090,  Ranked - 1100, Hyperroll - 1130, Doubleup - 1160")
                    
                    userInput = input()
                    response = await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':userInput})
                    if response != 200:
                        print("Lobby created successfully!")
                        print()
                else:
                    print("Please make sure you are not in queue or in game already")
                    
            elif(userInput == "4"):
                summonerId = (await summoner.json()).get('summonerId')
                print(summonerId)
                pickables = await connection.request('get', '/lol-champions/v1/inventories/'+ str(summonerId)+'/champions')
                res = await pickables.json()
                pickable_champs = []
                for champs in res: #for each champ
                    #print(champs.get('ownership'))
                    #{'freeToPlayReward': False, 'owned': True, 'rental': {'endDate': 0, 'purchaseDate': 1662308524000, 'rented': False, 'winCountRemaining': 0}}
                    for ownerships in champs.get('ownership').values(): #check the ownership of that champ
                        if(ownerships == True):
                            print(champs.get('id'), end = ":")  #print championId for selection
                            pickable_champs.append(champs.get('id'))
                            print(champs.get('name') + ":", end = "")
                            for skin in champs.get('skins'): #check ownership of each skin
                                for ownerships in skin.get('ownership').values():
                                     if(ownerships == True):
                                        print(skin.get('name'), end = ",")
                            print()

                print("Please enter the champion Id for the champion that you wish to instalock after acceting queue, or enter 0 to exit")
                championId = input()
  
                while(int(championId) not in pickable_champs):
                    print("You do not own that champion, please try again!")
                    championId = input()
                print()       
                    
            elif(userInput == "5"):
                gamephase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
                currentphase = await gamephase.json()
                if(currentphase == "ChampSelect"):
                    await champSelect(connection)
                else:
                    print("You are not in champ select")
                    print()
            elif(userInput == "6"):
                break
                
            else:
                print("Invalid input, please try again")
                print()
                
async def champSelect(connection):
    for i in range(5):
        try:
            summonerId = (await (await connection.request('get', '/lol-champ-select/v1/summoners/'+ str(i))).json()).get('summonerId')

            summonerInfo = await(await connection.request('get', '/lol-summoner/v1/summoners/'+ str(summonerId))).json()
            print(summonerInfo)
            name = summonerInfo.get('displayName')
            print(name)
            puuid = summonerInfo.get('puuid')
            print(reroll)
            print()

            rankedInfo = (await (await connection.request('get', '/lol-ranked/v1/ranked-stats/' + puuid)).json()).get('queues') #for some reason can only retrieve through puuid
            
            for x in rankedInfo: #ranked information
                print(x.get('queueType'), end = ': ')
                print(x.get('tier'), end = ' ')
                print(x.get('division'), end = ' ')
                print(x.get('leaguePoints'), end = ' LP')
                print()
            print()
        except:
            pass
       
    await connector.stop()
                    
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
