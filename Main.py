import AppEngine
from AppEngine import *

import LevelOne, LevelTwo, LevelThree
import JsonParser
import MainMenu
import Character
import Weapon
import Spritesheet

import random, time, sys, os


set_window("Roguelike Adventure", 960, 960) # { 15, 14 (*64) [960, 896] }
pygame.display.set_icon(pygame.image.load("icon.png"))

levelIndex = {
    1 : LevelOne.StageOne(),
    2 : LevelTwo.StageTwo(),
    3 : LevelThree.StageThree()
} 

rooms = {
    1 : [2, "east"],
    2 : [3, "north"],
    3 : [4, "west"],
}

roomBorders = {
    "east" : "hero.x + hero.width >= 960",
    "north" : "hero.y <= 1",
    "west" : "hero.x <= 1",
    "south" : "hero.y + hero.width >= 847"
}

oppDir = {
    "east" : "west",
    "west" : "east",
    "south" : "north",
    "north" : "south"
}

startPositions = {
    "east" : (20, 440),
    "north" : (440, 840),
    "west" : (930, 440),
    "south" : (440, 80)
}

ss = Spritesheet.spritesheet("Sprites/BlueHairedHero/blue_haired.png")
alpha = (0, 0, 0, 0)

parser = JsonParser.Parser()
parser.parse("GameConfig/config.json")
musicActive = parser.settings['musicSettings']['music']
sfxActive = parser.settings['musicSettings']['SFX']

currentLevel = parser.settings['levelSettings']['starting_level']
previousLevel = 0

parser.parse("Sprites/BlueHairedHero/walkCycle.json")

charWalkCycleDown = parser.settings['Down']
charWalkCycleUp = parser.settings['Up']
charWalkCycleRight = parser.settings['Right']
charWalkCycleLeft = parser.settings['Left']

cycles = [charWalkCycleDown, charWalkCycleLeft, charWalkCycleRight, charWalkCycleUp]
for element in cycles:
    for r in range(len(element)):
        element[r] = ss.image_at(tuple(element[r]), alpha)

menuActive = True
heroSpawned = False
inventorySpawned = False

HPred = 0
HPgreen = 255

inventorySlots = []
itemList = []

currentSelected = 0
nextAvailableSlot = 320


def start(heroCoords = None):
    global menuActive, itemList, obstCoords
    menuActive = False
    if 'heroChar' in globals() or 'heroChar' in locals():
        pass
    else:
        inventorySlots.clear()
        for x in range(4, 11):
            inventorySlots.append(sprite("Sprites/Inventory/inventory_slot.png", x * 64, 903, "slot" + str(x)))

    levelIndex[currentLevel].generateGround()
    levelIndex[currentLevel].generateObstacles()
    itemList = itemList + levelIndex[currentLevel].spawnTreasure()
    if musicActive == True:
        levelIndex[currentLevel].startMusic()
    if heroCoords != None:
        spawnHero(heroCoords)    
    else:        
        spawnHero()


def spawnHero(heroCoords = None):
    global hero, heroChar, heroBox, heroSpawned, inventorySpawned

    if heroCoords != None:
        hero = sprite(charWalkCycleRight[0], heroCoords[0], heroCoords[1], "hero")
    else:
        hero = sprite(charWalkCycleRight[0], 700, 453, "hero")
    hero.setHP(100)
    heroSpawned = True
    inventorySpawned = True

    if 'heroChar' in globals() or 'heroChar' in locals():
        pass
    else:
        heroChar = Character.Character()
        Sword = Weapon.Weapon("Sword", 260, 905, "Sprites/BlueHairedHero/sword.png", "Weapon")
        Sword.assignInvSlot(1)
        heroChar.addDimensions(Sword.spriteImage.width, Sword.spriteImage.height, heroChar.availableSlot)
        heroChar.addToInventory(Sword)
        Sword.pickedUp = True
        itemList.append(Sword)


menu = MainMenu.Menu()
if musicActive == True:
    menu.startMusic()

hoverText = text("", 13, black, 0, 0)

optionClicked = False

walkCycleRate = 0
walkFrame = 0

currentDirection = "west"
tempx = 0
tempy = 0
cannotWalkHere = ""

while(True):

    if walkCycleRate != 4:
        walkCycleRate += 1
    else:
        if walkFrame != 3:
            walkFrame += 1
        else:
            walkFrame = 0
        walkCycleRate = 0

    if menuActive == True:
        menu.detectHovers()
        menu.detectLoadClick()
        if menu.detectInfoClick() == True:
            optionClicked = True
        if optionClicked == True:
            if menu.detectBackArrow() == True:
                optionClicked = False
        if menu.detectPlayClick() == True:
            start()


    for item in itemList:

        if heroChar.storage[currentSelected + 1] == item:
            hoverText.changeText(item.name, black)
            hoverText.x = item.spriteImage.x
            hoverText.y = item.spriteImage.y - 30

        if hero.collide(item.spriteImage) and kb.activeKeys[K_e]:
            if heroChar.findTotalFilled() == 7:
                pass
            else:
                if sfxActive == True:
                    au.playSound("Music/Pick_Up.ogg")
                heroChar.addToInventory(item)
                heroChar.addDimensions(item.spriteImage.width, item.spriteImage.height, heroChar.availableSlot - 1)
                item.assignInvSlot(heroChar.availableSlot - 1)
                item.spriteImage.main = pygame.transform.scale(item.spriteImage.main, (48, 48))
                item.pickedUp = True
                item.spriteImage.x = nextAvailableSlot
                item.spriteImage.y = 905
                done = False
                for x in range(len(heroChar.storage)):
                    if done == False:
                        if heroChar.storage[x + 1] == "":
                            heroChar.availableSlot = x + 1
                            nextAvailableSlot = inventorySlots[x].x
                            done = True


    if kb.activeKeys[K_q] and heroChar.storage[currentSelected + 1] != "":
        if nextAvailableSlot < inventorySlots[currentSelected].x:
            pass
        else:
            nextAvailableSlot = inventorySlots[currentSelected].x

        if sfxActive == True:
            au.playSound("Music/Drop.ogg")
        hoverText.changeText("", black)
        itemSprite = heroChar.storage[currentSelected + 1].spriteImage
        itemSprite.moveToFront()
        dimen = heroChar.itemDimensions[currentSelected + 1].split(" ")
        itemSprite.main = pygame.transform.scale(itemSprite.main, ( int(dimen[0]) , int(dimen[1]) ))
        itemSprite.x = hero.x
        itemSprite.y = hero.y
        heroChar.storage[currentSelected + 1].pickedUp = False
        heroChar.storage[currentSelected + 1].invSlot = ""
        heroChar.removeFromInventory(currentSelected + 1)

    if kb.activeKeys[K_1]:
        currentSelected = 0
    elif kb.activeKeys[K_2]:
        currentSelected = 1
    elif kb.activeKeys[K_3]:
        currentSelected = 2
    elif kb.activeKeys[K_4]:
        currentSelected = 3
    elif kb.activeKeys[K_5]:
        currentSelected = 4
    elif kb.activeKeys[K_6]:
        currentSelected = 5
    elif kb.activeKeys[K_7]:
        currentSelected = 6
    
    if inventorySpawned == True:
        for s in range(7):
            if s == currentSelected:
                inventorySlots[s].modifyImage("Sprites/Inventory/inventory_slot_selected.png")
            else:
                inventorySlots[s].modifyImage("Sprites/Inventory/inventory_slot.png")

    if heroSpawned == True:
        hero.drawHealthText(hero.x - 3, hero.y - 24, 20, (HPred, HPgreen, 0), str(hero.HP))
        if (kb.activeKeys[K_w] or kb.activeKeys[K_UP]) and hero.edgeTop > 0:
            currentDirection = "north"
            hero.modifyImage(charWalkCycleUp[walkFrame])            
            if cannotWalkHere != currentDirection:
                hero.y -= 4
        if (kb.activeKeys[K_s] or kb.activeKeys[K_DOWN]) and hero.edgeBottom < 896:
            currentDirection = "south"
            hero.modifyImage(charWalkCycleDown[walkFrame])
            if cannotWalkHere != currentDirection:
                hero.y += 4
        if (kb.activeKeys[K_a] or kb.activeKeys[K_LEFT]) and hero.edgeLeft > 0:
            currentDirection = "west"
            hero.modifyImage(charWalkCycleLeft[walkFrame])
            if cannotWalkHere != currentDirection:
                hero.x -= 4
        if (kb.activeKeys[K_d] or kb.activeKeys[K_RIGHT]) and hero.edgeRight < 960:
            currentDirection = "east"
            hero.modifyImage(charWalkCycleRight[walkFrame])
            if cannotWalkHere != currentDirection:
                hero.x += 4

        for item in levelIndex[currentLevel].obstacleTiles:
            if item.sprite.collide(hero):
                if hero.HP != 0:
                    hero.HP -= 1
                    
                if HPred != 255:
                    HPred += 5.1
                    HPred = round(HPred)
                elif HPgreen != 0:
                    HPgreen -= 5.1
                    HPgreen = round(HPgreen)


        if eval(roomBorders[rooms[currentLevel][1]]):
            previousLevel = currentLevel
            temp = startPositions[rooms[currentLevel][1]]
            hero.destroy()
            hero = None
            levelIndex[currentLevel].destroy()
            currentLevel = rooms[currentLevel][0]
            start(temp)
        elif hero.x <= 1:
            previousLevel = 2
            temp = (930, 440)
            tempR = []
            for x in range(len(itemList)):
                if itemList[x].spriteImage.y == 905:
                    tempR.append(itemList[x])
            itemList = tempR
            hero.destroy()
            hero = None
            levelIndex[currentLevel].destroy()
            currentLevel = 1
            start(temp)


    if heroSpawned == True:
        temp = levelIndex[currentLevel].checkCollision(hero)
        cannotWalkHere = temp


    gameLoop(black)