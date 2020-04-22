# -- coding: utf-8 --
import re
from datetime import datetime
import time

quantityMarker = ("Quantité", "00000001-0000-0001-0001-000000000003")

######################
####### EVENTS #######
######################

def OnCounterChanged(args):
	if IamAlien():
		me.volonté = 0
	else:
		if args.counter.value < 0 :
			args.counter.value = 0
		if args.counter.name == "Volonté":
			if args.counter.value == 0 :
				notify("{} est mort (0 PV)".format(me))
				surrender()
			if args.counter.value > 3 :
				args.counter.value = 3
		mute()
		shared.counters["Volonté perdue"].value = (len(getPlayers())-1)*3 - countTotalPlayersPV()

def OnCardsMoved(args):
	index = -1
	if args.player == me:
		for card in args.cards:
			index += 1
			#whisper(str(card.position))
			# déplacements sur la table
			if args.fromGroups[0] == table and args.toGroups[0] == table:
				if "Blocked" in card.type:
					card.moveToTable(args.xs[index], args.ys[index], True)
			# déplacements vers la main
			if args.fromGroups[0] == table and args.toGroups[0] == me.hand:
				notFound = True
				for tableCard in table:
					if tableCard.model == card.model and "Blocked" in tableCard.type:
						tableCard.markers[quantityMarker] -= 1
						card.type = ""
						card.proprio = str(me._id)
						notFound = False
				if notFound and "Blocked" in card.type: # c'était la dernière carte, on la remet sur le plateau car c'était interdit
					card.moveToTable(args.xs[index], args.ys[index], True)
					card.isFaceUp = True

def OnPhasePassed(args):
	if me.getGlobalVariable("isSoundMuted") == "False":
		playSound("phase{}".format(str(args.id+1)))

def OnCardDoubleClicked(args):
	if canLoadBeacon([args.card]):
		loadBeacon()
	elif canActivateBeacon([args.card]):
		activateBeacon()
	elif canIncreaseAssimilationToken([args.card]):
		increaseAssimilationToken()

######################
####### SETUP  #######
######################	

def setup():
	if(askChoice("Quel rôle veux-tu jouer ?", ["La Créature", "Un Naufragé"], ['#512e5f', '#154360']) == 1):
		notify("{} veut être la créature".format(me))
		me.setGlobalVariable("preferAlien", str(True))
		me.setGlobalVariable("ready", str(True))
	else:
		notify("{} veut être un naufragé".format(me))
		me.setGlobalVariable("ready", str(True))
	if(allPlayersAreReady()):
		createSurviesDeck()
		designateAnAlien()
		remoteCall(me,"chooseCardSet", [])

def createSurviesDeck():
	mute()
	createRangeCards(shared.survies, 80, 106)
	shared.survies.shuffle()
	notify("La pile de cartes survies est prête")

def designateAnAlien():
	candidates = filter(lambda x : x.getGlobalVariable("preferAlien") == "True",getPlayers())
	if len(candidates) == 0:
		candidates = getPlayers()
	
	notify("Choix de la créature parmi {} candidats ".format(len(candidates)))
	random = rnd(0,len(candidates)-1)
	
	notify("{} incarnera la créature".format(candidates[random]))
	notifyBarAll("Prenez garde ... Des cornes, des griffes et des ailes ont poussées sur ... {}".format(candidates[random]), "#512e5f")
	
	remoteCall(candidates[random], "alienSetup", [])

def alienSetup():
	me.setGlobalVariable("isAlien", str(True))
	whisper("Je suis la créature")
	me.volonté = 0
	
	setGlobalVariable("dateTimeDebut", time.mktime(datetime.now().timetuple()))
	
	alienChooseBoard()
	mute()
	
	me.défausse.collapsed = False
	me.pioche.collapsed = False
	
	createRangeCards(me.pioche, 4, 35)
	me.pioche.shuffle()
	for i in range(0,3):
		me.pioche.top().moveTo(me.hand)
	#les jetons
	me.hand.create("00000001-0000-0001-0001-000000000036")
	me.hand.create("00000001-0000-0001-0001-000000000037")
	me.hand.create("00000001-0000-0001-0001-000000000038")

def survivorSetup():
	if IamNotAlien():
		whisper("Je suis un naufragé")
		mute()
		me.hand.create("00000001-0000-0001-0001-000000000041").proprio = str(me._id)
		me.hand.create("00000001-0000-0001-0001-000000000043").proprio = str(me._id)
		me.hand.create("00000001-0000-0001-0001-000000000045").proprio = str(me._id)
		me.hand.create("00000001-0000-0001-0001-000000000047").proprio = str(me._id)
		me.hand.create("00000001-0000-0001-0001-000000000049").proprio = str(me._id)

def alienChooseBoard():
	if IamAlien():
		planet = askChoice("Sur quelle planete sommes-nous ?", 
		["Planète A (Bonus 1 tour sur 2)", "Planète B (Bonus à la fin)", "La planète c'est moi"], 
		['#154360','#0b5345','#f39c12'])
		
		if (planet == 3):
			planet = rnd(1,2)
		
		if (planet == 2):
			table.board = 'PisteB'
			notify("La créature a choisi la planète B")
		else:
			notify("La créature a choisit la planète A")

def alienPlaceCardsOnTheBoard():
	if IamAlien():
		mute()
		drawBackgroundCard("00000001-0000-0001-0001-000000000041",1,1)
		drawBackgroundCard("00000001-0000-0001-0001-000000000043",1,2)
		drawBackgroundCard("00000001-0000-0001-0001-000000000045",1,3)
		drawBackgroundCard("00000001-0000-0001-0001-000000000047",1,4)
		drawBackgroundCard("00000001-0000-0001-0001-000000000049",1,5)
		
		quantity = howManyCardsInStack()
		drawBackgroundCard("00000001-0000-0001-0001-000000000051",2,1,quantity)
		drawBackgroundCard("00000001-0000-0001-0001-000000000053",2,2,quantity)
		drawBackgroundCard("00000001-0000-0001-0001-000000000055",2,3,quantity)
		drawBackgroundCard("00000001-0000-0001-0001-000000000057",2,4,quantity)
		drawBackgroundCard("00000001-0000-0001-0001-000000000039",2,5,quantity)
		
		#les pions
		table.create("00000001-0000-0001-0001-000000000110", 105, -255, persist = True).type = "Balise|Blocked"
		
		table.create("00000001-0000-0001-0001-000000000111", 0, 0, persist = True).type = "Assimilation|Blocked"
		addToAssimilationRank(0-len(getPlayers()))
		
		table.create("00000001-0000-0001-0001-000000000112", -10, -10, persist = True).type = "Secours|Blocked"
		addToSecoursRank(0-len(getPlayers()))
		
		#si j'ai une survie, je la rend
		for card in me.hand:
			if card.size == "Survie":
				card.moveTo(shared.survies)
		
		notifyBarAll("Mise en place terminée. Que le jeu commence !", "#008FFF")
		notify("Regles du jeu : http://wells83.free.fr/OCTGN/NotAlone/")
		nextTurn(force=True)
		setPhase(1)

def chooseCardSet():
	#extensionCards = askChoice("Quels lieux pourrons-nous visiter ?", 
	#["Lieux de base", "Lieux nouveaux", "Tous les lieux mélangés", "Le Labyrinthe"], 
	#['#154360','#0b5345','#283747', '#e74c3c'])
	#notify("extensions {}".format(extensionCards))
	
	remoteCallAll("survivorSetup", [])
	
	for p in getPlayers():
		if not isAlien(p):
			takeOneSurvie(player = p)
	
	remoteCallAll("alienPlaceCardsOnTheBoard", [])

def cleanupPhase4():
	if IamAlien():
		for card in table:
			if card.size == "Jeton":
				card.moveTo(me.hand) # on remonte les jetons
			if card.size == "Alien" and not card.anchor:
				card.moveTo(me.défausse) # on défausse la carte Alien
		alienCardInHand = filter(lambda card : card.size == "Alien", me.hand)
		for i in range(0, 3-len(alienCardInHand)):
			me.pioche.random().moveTo(me.hand) # on re remplit la main jusqu'à 3 cartes
		increaseSecoursToken(who = "La phase 4")
	if IamNotAlien(): # on détruit les survies + range la defausse
		cardCounter = 0
		for card in table:
			if card.owner._id == me._id:
				if card.size == "Survie":
					card.delete()
				if card.size == "Default" and "Blocked" not in card.type:
					playCard(card, pad = 130+cardCounter)
					cardCounter += 30

######################
####### UTILS  #######
######################

def IamAlien(group = (), x = 0, y = 0):
	return isAlien(me)

def IamNotAlien(group = (), x = 0, y = 0):
	return not IamAlien()

def isAlien(somePlayer):
	return somePlayer.getGlobalVariable("isAlien") == "True"

def isCard(card, cardNum):
	knownCards = { 
		4:"00000001-0000-0001-0001-000000000047",
		7:"00000001-0000-0001-0001-000000000053",
		8:"00000001-0000-0001-0001-000000000055",
		9:"00000001-0000-0001-0001-000000000057",
		"Balise":"00000001-0000-0001-0001-000000000110",
		"Assimilation":"00000001-0000-0001-0001-000000000111",
		"Secours":"00000001-0000-0001-0001-000000000112"}
	return card[0].model == knownCards.get(cardNum)

def canDraw1Survie(card, x = 0, y = 0):
	return IamNotAlien() and isCard(card, 9)

def canDraw2Survie(card, x = 0, y = 0):
	return IamNotAlien() and isCard(card, 7)

def canLoadBeacon(card, x = 0, y = 0):
	return IamNotAlien() and (isCard(card, 4) or isCard(card, "Balise")) and getGlobalVariable("stateBalise") == "Activated"

def canActivateBeacon(card, x = 0, y = 0):
	return IamNotAlien() and (isCard(card, 4) or isCard(card, "Balise")) and getGlobalVariable("stateBalise") == "Loaded"

def countTotalPlayersPV():
	sum = 0
	for thisPlayer in getPlayers():
		sum += thisPlayer.volonté
	return sum

def canFlip(card, x = 0, y = 0):
	return not "Blocked" in card[0].type

def refreshAssimilationTokenPosition():
	mute()
	position = {
		1: (289,-258), 2: (281,-296), 3: (251,-271), 4: (241,-310), 5: (214,-280), 
		6: (201,-320), 7: (178,-288), 8: (161,-324), 9: (140,-291), 10: (118,-325), 
		11: (101,-289), 12: (77,-323), 13: (45,-300) }
	x, y = position.get(eval(getGlobalVariable("rankAssimilation")),(0,0))
	card = getOneCardOnTableByType("Assimilation")
	card.moveToTable(x, y, True)
	if getGlobalVariable("rankAssimilation") == "13":
		notifyBarAll("La partie est terminée, la Créature l'emporte !")
		playSound("finAlien")

def addToAssimilationRank(adder):
	setGlobalVariable("rankAssimilation", str(eval(getGlobalVariable("rankAssimilation"))+adder))
	refreshAssimilationTokenPosition()

def canIncreaseAssimilationToken(card, x = 0, y = 0):
	return IamAlien() and isCard(card, "Assimilation")

def canDecreaseAssimilationToken(card, x = 0, y = 0):
	return IamAlien() and isCard(card, "Assimilation")

def addToSecoursRank(adder):
	setGlobalVariable("rankSecours", str(eval(getGlobalVariable("rankSecours"))+adder))
	refreshSecoursTokenPosition()

def refreshSecoursTokenPosition():
	mute()
	position = {
		1: (-334,-322), 2: (-324,-283), 3: (-294,-310), 4: (-283,-271), 5: (-256,-300), 
		6: (-242,-262), 7: (-216,-296), 8: (-199,-256), 9: (-175,-291), 10: (-156,-257), 
		11: (-134,-292), 12: (-111,-257), 13: (-94,-292), 14: (-69,-262), 15: (-52,-298),
		16: (-28,-268), 17: (-13,-306), 18: (12,-276), 19: (45,-300) }
	x, y = position.get(eval(getGlobalVariable("rankSecours")),(-10,-10))
	card = getOneCardOnTableByType("Secours")
	card.moveToTable(x, y, True)
	if getGlobalVariable("rankSecours") == "19":
		notifyBarAll("La partie est terminée, les Naufragés sont sauvés et l'emportent !")
		playSound("finSecours")

def canIncreaseSecoursToken(card, x = 0, y = 0):
	return IamNotAlien() and (isCard(card, 8) or isCard(card, "Secours"))

def canDecreaseSecoursToken(card, x = 0, y = 0):
	return IamNotAlien() and isCard(card, "Secours")

def getOneCardOnTableByType(type = ""):
	for card in table:
		if type in card.type:
			return card

def remoteCallAll(functionName, params = []):
	mute()
	for p in getPlayers():
		remoteCall(p,functionName,params)

def notifyBarAll(message, color = "#FF0000"):
	remoteCallAll("notifyBar",[color,message])
	notify(message)

def allPlayersAreReady():
	readyPlayers = filter(lambda x : x.getGlobalVariable("ready") == "True",getPlayers())
	return len(readyPlayers) == len(getPlayers())

def createRangeCards(destination, fromID, toID):
	for i in range(fromID, toID+1):
		destination.create("00000001-0000-0001-0001-000000000{}".format(str(i).zfill(3)))

def howManyCardsInStack():
	return [1,1,2,2,3,3][len(getPlayers())-1]

def drawBackgroundCard(cardId, line, position, quantityUnder = 0):
	cards = table.create(cardId, -325+130*(position-1), -200+165*(line-1), 1+quantityUnder, True)
	if str(type(cards)).find('class') == 1:
		cards = [cards]
	for card in cards:
		card.type = "Blocked"
		
		if quantityUnder > 0:
			card.markers[quantityMarker] = quantityUnder
		card.sendToBack()

def printGameDuration(a=0,b=0,c=0):
	begin = datetime.fromtimestamp(eval(getGlobalVariable("dateTimeDebut")))
	duration = datetime.utcfromtimestamp((datetime.now() - begin).total_seconds())
	notify("La partie a durée {}".format(duration.strftime('%Hh%Mmin')))

######################
#### PILE ACTIONS ####
######################

def shuffle(group, x = 0, y = 0):
    mute()
    group.shuffle()
    notify("{} mélange sa {}.".format(me, group.name))

######################
#### HAND ACTIONS ####
######################

def playCard(card, x = 0, y = 0, pad = 0, shiftNext = True):
	mySpot = eval(me.getGlobalVariable("mySpot"))
	card.moveToTable(mySpot[0]+pad, mySpot[1], True)

def playRandomly(group, x = 0, y = 0):
	for i in range(0,5):
		card = group.random()
		
		if card.size == "Default": #si c'est un lieu
			playCard(card)
			notify("{} joue une carte au hasard".format(me))
			return None
	whisper("Pas de chance, pas de carte lieu trouvée après 5 tentatives")

def surrender(group = (), x = 0, y = 0):
	me.volonté = 3
	for card in table:
		if card.proprio == str(me._id):
			card.isFaceUp = True
			card.moveTo(me.hand)
	notify("{} lâche prise...".format(me))
	increaseAssimilationToken()

def resist(group = (), x = 0, y = 0, pv = 1):
	myCards = filter(lambda card : card.proprio == str(me._id),table)
	dialog = cardDlg(myCards)
	dialog.title = "Sélectionner {} cartes à récupérer".format(2*pv)
	dialog.min = 1*pv
	dialog.max = 2*pv
	
	cardsSelected = dialog.show()
	if len(cardsSelected) > 0:
		for card in cardsSelected:
			card.moveTo(me.hand)
		notify("{} a résisté et a récupéré {} cartes".format(me, len(cardsSelected)))
		me.volonté -= 1*pv

def resist2(group = (), x = 0, y = 0):
	resist(pv = 2)

#######################
#### TABLE ACTIONS ####
#######################

def takeOneSurvie(cards = (), x = 0, y = 0, player = me):
	mute()
	card = shared.survies.random()
	card.moveTo(player.hand)
	notify("{} pioche une carte survie".format(player))

def takeTwoSurvie(cards = (), x = 0, y = 0):
	takeOneSurvie()
	takeOneSurvie()

def setMySpot(groups, x = 0, y = 0):
	me.setGlobalVariable("mySpot", str([x, y]))

def loadBeacon(groups = (), x = 0, y = 0):
	mute()
	for card in table:
		if "Balise" in card.type:
			x, y = card.position
			card.moveToTable(x, y+65, True)
	setGlobalVariable("stateBalise", "Loaded")
	notify("{} a chargé la balise".format(me))

def activateBeacon(groups = (), x = 0, y = 0):
	mute()
	for card in table:
		if "Balise" in card.type:
			x, y = card.position
			card.moveToTable(x, y-65, True)
	setGlobalVariable("stateBalise", "Activated")
	notify("{} a activé la balise, les secours avancent".format(me))
	addToSecoursRank(1)

def increaseAssimilationToken(groups = (), x = 0, y = 0):
	addToAssimilationRank(1)
	notify("{} fait avancer l'assimilation".format(me))

def decreaseAssimilationToken(groups, x = 0, y = 0):
	addToAssimilationRank(-1)
	notify("{} fait reculer l'assimilation".format(me))

def increaseSecoursToken(groups =(), x = 0, y = 0, who = me):
	addToSecoursRank(1)
	notify("{} fait avancer les secours".format(who))

def decreaseSecoursToken(groups, x = 0, y = 0):
	addToSecoursRank(-1)
	notify("{} fait reculer les secours".format(me))

def flip(cards, x = 0, y = 0):
    mute()
    for card in cards:
		card.isFaceUp = not card.isFaceUp
 
def phaseInc(group, x = 0, y = 0):
	nextPhase = currentPhase()[1] % 4 +1
	notify("Passage en phase {}".format(nextPhase))
	
	if nextPhase == 1:
		nextTurn(force=True)
	setPhase(nextPhase)

	if nextPhase == 3:
		for card in table:
			if "Blocked" not in card.type and card.size == "Default":
				card.isFaceUp = True
	
	if nextPhase == 4:
		remoteCallAll("cleanupPhase4")

def muteSound(group, x = 0, y = 0):
	me.setGlobalVariable("isSoundMuted", str(not eval(me.getGlobalVariable("isSoundMuted"))))
