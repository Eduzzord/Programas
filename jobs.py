import Terminal, Login, Character, GameState, time, Quest, Field, Packet, Key, Inventory
from collections import OrderedDict
import os, sys, json
##################################################
##  jobs.py                                     ##
##  JOBS v = 3.4				##
##  Created by raech on 10/18/19.		##		
##################################################
# User Vars
# level to switch characters
manualOrder = False
manualList = ['POSITION;JOBID;LEVELTOSTOP', "POS2,JOBID2,LVL2", "ETC"]


classlist = ["Mercedes", "Evan", "Aran", "Shade", "Jett", "Kinesis", "Luminous", "Phantom", "Xenon", "Cadena", "Path Finder", "Kaiser",
            "Mihile", "Battle Mage", "Wild Hunter", "Demon Slayer", "Blaster", "Demon Avenger", "Mechanic", "Corsair", "Angelic Buster", 
            "Blaze Wizard", "Dawn Warrior", "Buccaneer", "Cannoneer", "Hero", "Dark Knight", "Bowman", "Fire/Poison", "Ice/Light", 
            "Bishop", "Shadower", "Wind Archer", "Thunder Breaker", "Blaze Wizard", "Illium", "Night Walker", "Dual Blade", 
            "Hayato", "Paladin", "Ho Young", "Ark"]

def GetClassesList():
    fi = os.getcwd()+"/Jobs/Classes.json"
    if os.path.isfile(fi):
        with open(fi, "r") as read_file:
            return json.load(read_file)
    else:
        return "Empty"

Jobs = GetClassesList()["Jobs"]

limitLevel = 150

# potions
hpPot = 0x21 # PG UP
mpPot = 0x22 # PG DOWN
# auto attack key (terminal one)
terminalKey = 30 # A ( eh literalmente o numero de opcao 30 se vc mostrar a lista inteira no terminal dropdown de atk, 33 = D, etc )
attackKey = 0x41 # A ( tem q corresponder a o terminalKey, mas em windows VK_CODE

# use Snail
lootTime = 7
snailTime = time.time() + 90

# Star Force
whitelist = []
Resistance = [3712, 3212, 3312, 3512, 3412]
Cygnus = [1112, 1312, 1512, 1212, 1412]
Explorers = [112, 122, 132, 212, 222, 232, 312, 322, 412, 422, 512, 522]
#Explorers = [412, 132, 512, 522, 132, 212, 222, 232, 312, 312, 412, 422]
Demons = [3112, 3122]
# Job List

##############
# Code Below #
##############
###############################################
# Import Section
if not any("Jobs" in s for s in sys.path):
    sys.path.append(os.getcwd()+"/Jobs")
    sys.path.append(os.getcwd()+"\Jobs")
if not any("Quests" in s for s in sys.path):
    sys.path.append(os.getcwd()+"/Jobs/Quests")
    sys.path.append(os.getcwd()+"\Jobs\Quests")

# Extra Modules
try:
    import packets
except:
    print("Error Importing Packet Headers")

###################
# List of Headers #
###################
#specter = packets.Ark()
itemtogglePacket = packets.ItemToggle()
skillHeader = packets.Skill()
hyperHeader = packets.Hyper()
buyHeader = packets.NPCBuy()
blockHeader = packets.NPCBlock()
useHeader = packets.ItemUse()
forfeitHeader = packets.Quest()
choiceHeader = packets.NPCChoice()
reactorHeader = packets.ReactorIntereaction() # comes [0]send [1]recv
shipHeader = packets.Ship()
# StarForce Header, RECV, Opcode, Star Catch[3]
sHeaders = packets.Starforce()
# Request, Result, Bought, MesoRequest, Locker, MoveToIventory[4]
cHeaders = packets.MesoCashShop()
htr = packets.HTRID()
guideHeader = packets.Guide()
##################################

###################
# Small Functions #
###################
def is_local_user():
    field_struct = Field.GetCharacters()
    for pos in range(len(field_struct)):
        user = field_struct[pos]
        if not Terminal.IsLocalUser(user.id):
            return False

    return True

def JobChange(cid):
    result = cid
    lvls = [30, 60, 100]
    for i in range(2,5):
        if Character.GetLevel() == lvls[i-2] and Character.GetJob() != cid["Job"][i]:
            if (type(cid["Skill"][i-1]) is str and ";" not in cid["Skill"][i-1]):
                result["Type"] = ["auto", "auto", "auto", "auto", "auto"]
                result["Delay"] = [-100, -100, -100, -100, -100]
                break;
            if (type(cid["Skill"][i-1]) is int):
                result["Type"] = ["auto", "auto", "auto", "auto", "auto"]
                result["Delay"] = [-100, -100, -100, -100, -100]
                break;
    return result

def UseMasteryBook(sid, lvl):
    if lvl == 20:
        mastery = 2431789
    else:
        mastery = 2431790
    if Inventory.FindItemByID(mastery).valid:
        Npc.ClearSelection()
        Npc.RegisterSelection(str(sid))
        Inventory.UseItem(mastery)
        time.sleep(1)

def SnailPacket():
    snail = Packet.COutPacket(itemtogglePacket)
    snail.Encode4(int(time.monotonic() * 1000))
    snail.Encode2(Inventory.FindItemByID(5000054).pos)
    Packet.SendPacket(snail)

def Snail():
    if Terminal.GetProperty("snailtime", None) == None:
        Terminal.SetProperty("snailtime", snailTime)
    if Terminal.GetProperty("snailtime", None) < time.time():
        SnailPacket()
        time.sleep(lootTime)
        SnailPacket()
        Terminal.SetProperty("snailtime", snailTime)

def EquipWeapon(wid, lvl, job):
    if Character.GetLevel() == lvl and Character.GetJob() == job:
        if not Terminal.GetCheckBox("Rush By Level"):
            return
        if Character.GetEquippedItemIDBySlot(-11) != wid:
            if not Inventory.FindItemByID(wid).valid:
                return
            print("Equipping")
            Terminal.SetRadioButton("SIRadioMelee", True)
            Terminal.SetLineEdit("SISkillID", "equipping")
            Terminal.SetCheckBox("Skill Injection", False)
            Terminal.SetCheckBox("Auto Attack", False)
            time.sleep(3)
            Inventory.SendChangeSlotPositionRequest(1, Inventory.FindItemByID(wid).pos, -11, -1)
            time.sleep(3)
            #Terminal.SetCheckBox("Auto Equip", True)
            #time.sleep(7)
            #Terminal.SetCheckBox("Auto Equip", False)

def SetMacro(sid, delay):
    if is_local_user():
        if not Terminal.GetCheckBox("macro1_check"):
            Terminal.SetCheckBox("macro1_check", True)
            Terminal.SetSpinBox("macro1_spin", delay)
            if sid == 0:
                Terminal.SetComboBox("macro1_combo", 1)
            else:
                Terminal.SetComboBox("macro1_combo", 31)
                Key.Set(0x42, 1, sid)
    else:
        Terminal.SetCheckBox("macro1_check", False)

def FaceMiddle():
    if Terminal.IsSolvingRune():
        print("Reseting Moved")
        Terminal.SetProperty("moved", True)
    else:
        if Terminal.GetProperty("moved", True):
            print("Moving")
            mid = int((Field.GetRect().left + Field.GetRect().right) / 2)
            if Character.GetPos().x > mid:
                newpos = Character.GetPos().x - 3
            else:
                newpos = Character.GetPos().x + 2
            Character.MoveX(newpos, 50)
            Terminal.SetProperty("moved", False)

def StopMoving(maps, level=None):
    if not Terminal.GetCheckBox("Kami Vac"):
        if maps[0] == 0:
            if level[0] < Character.GetLevel() < level[1]:
                FaceMiddle()
                Terminal.SetCheckBox("bot/autoDie/waitMins", False)
            else:
                Terminal.SetCheckBox("bot/autoDie/waitMins", True)
            return
        if Field.GetID() in maps:
            FaceMiddle()
            Terminal.SetCheckBox("bot/autoDie/waitMins", False)
        else:
            if Character.GetLevel() not in [10, 30, 60, 100]:
                Terminal.SetCheckBox("bot/autoDie/waitMins", True)


###############################################################################################
# Imports #
try:
    import skills
except:
    print("Error Importing Skill Assigner")

try:
    import hypers
except:
    print("Error Importing Hyper Assigner")

try:
    import move
except:
    print("Error Importing Movement Script")

try:
    import sind
except:
    print("Error Importing SIND Script")

try:
    import utils
except:
    print("Error Importing Utilities Script")

# By Class Modules
if Terminal.GetProperty("Main Job", -1) == 4212:
    try:
        import kanna
    except:
        print("error importing kanna")

    kanna.Main()
    Terminal.SetCheckBox("Summon Kishin", True)

if Terminal.GetProperty("Main Job", -1) == 332:
    try:
        import pathfinder
    except:
        print("error importing pathfinder")

    pathfinder.PathfinderJob()

if Terminal.GetProperty("Main Job", -1) == 16412:
    try:
        import hoyoung
    except:
        print("error importing evan")
    
    #Terminal.SetCheckBox("GFMAv1", True)
    if Character.GetJob() != 16412:
        hoyoung.YoungJob(guideHeader)

if Terminal.GetProperty("Main Job", -1) == 2217:
    try:
        import evan
    except:
        print("error importing evan")
    
    evan.EvanJob()

if Terminal.GetProperty("Main Job", -1) == 2712:
    try:
        import lumi
    except:
        print("error importing lumi")
    
    lumi.LumiJob(choiceHeader)
    #if Character.GetSkillLevel(155121341) == 0 and Character.GetJob() == 2712:
    #    Terminal.SetCheckBox("GFMAv1", True)
    #else:
    #    Terminal.SetCheckBox("GFMAv1", False)

if Terminal.GetProperty("Main Job", -1) == 3122 or Terminal.GetProperty("Main Job", -1) == 3112:
    try:
        import demons
    except:
        print("error importing demons")
        
    if Terminal.GetProperty("Job Name", -1) == "Demon Avenger":
        if Character.GetLevel() <= 159:
            Terminal.SetCheckBox("Auto Exceed", True)
            Terminal.SetSlider("sliderHP", 10)
            SetMacro(31011001, 5500)
    if Character.GetJob() == 3112:
        if Character.GetLevel() <= 159:
            StopMoving([103041115, 251010000, 220070000])
            SetMacro(0, 350)
            Jobs["Demon Slayer"] =  { "Job":[3001, 3100, 3110, 3111, 3112], "Skill":[0, 31000004, 31000004, 31000004, 31121010], "Delay":[-100, 300, 300, 300, 280], "Type":["auto", "dragon", "dragon", "dragon", "melee"]}
    demons.DemonsJob(forfeitHeader, choiceHeader)

if Terminal.GetProperty("Main Job", -1) == 3612:
    try:
        import xenon
    except:
        print("error importing xenon")

    safeStr = "safe"
    safeXenon = [29, 59, 85, 100, 125, 149, 170, 199]
    for i in safeXenon:
        if Character.GetLevel() == i:
            if Terminal.GetProperty(safeStr+str(i), True):
                Terminal.SetCheckBox("Auto AP", True)
                time.sleep(1)
                Terminal.SetProperty(safeStr+str(i), False)

    Terminal.SetCheckBox("Auto AP", False)

    xenon.XenonJob(shipHeader)

if 3212 <= Terminal.GetProperty("Main Job", -1) <= 3712 and Terminal.GetProperty("Main Job", -1) != 3612:
    try:
        import resistance
    except:
        print("error importing Resistance")

    resistance.ResistanceJob()
    if Terminal.GetProperty("Job Name", -1) == "Mechanic":
        EquipWeapon(1492014, 10, 3500)
        #utils.AutoBuff(bJob="mech", bBuff="human")
        StopMoving([103041115])

    if Terminal.GetProperty("Job Name", -1) == "Wild Hunter":
        EquipWeapon(1462092, 10, 3300)
        StopMoving([0],[30,60])
        if Character.GetLevel() >= 15 and not Character.HasBuff(2, 33001001):
            Jobs["Wild Hunter"] = { "Job":[3000, 3300, 3310, 3311, 3312], "Skill":[30001000, 33001105, 33101113, 33111112, 33111112], "Delay":[-100, 1100, 1100, 1100, 1100], "Type":["auto", "dragon", "dragon", "dragon", "dragon"]}
            
    if Terminal.GetProperty("Job Name", -1) == "Blaster":
        if Character.GetLevel() <= 14:
            Jobs["Blaster"] =  { "Job":[3000, 3700, 3710, 3711, 3712], "Skill":[0, 37001000, "37101000;37100002", "37110006;37110004", "37110006;37110004"], "Delay":[-100, -50, 60, 17, 17], "Type":["auto", "auto", "magic", "magic", "magic"]}
        EquipWeapon(1582000, 10, 3700)
        '''
        if Character.GetSkillLevel(155121341) == 0:
            if Character.GetJob() >= 3710:
                #Terminal.SetCheckBox("GFMAv1", True)
                Terminal.SetCheckBox("No Skill Effect", True)
        else:
            Terminal.SetCheckBox("GFMAv1", False)            
        '''

    if Terminal.GetProperty("Job Name", -1) == "Battle Mage":
        EquipWeapon(1382100, 10, 3200)
        shockMaps = [102040500, 211040100]
        StopMoving([103041115])
        if Character.HasBuff(2, 32001016) and Character.HasBuff(2, 32111016):
            if Field.GetID() in shockMaps:
                Jobs["Battle Mage"] = { "Job":[3000, 3200, 3210, 3211, 3212], "Skill":[30001000, 32001000, 32101000, "32111002;32111016", "32121002;32111016"], "Delay":[-100, 900, 900, 50, 50], "Type":["auto", "dragon", "dragon", "magic", "magic"]}

        if Character.GetJob() != 3212:
            utils.AutoBuff(bJob="bam", bBuff="haste")
        else:
            utils.AutoBuff(bJob="bam", bBuff="dark")

if Terminal.GetProperty("Main Job", -1) == 4112:
    try:
        import hayato
    except:
        print("error importing hayato")

    StopMoving([0], [100, 160])
    if Character.GetJob() != Terminal.GetProperty("Main Job", -1):
        hayato.HayatoJob()

if Terminal.GetProperty("Main Job", -1) == 2412:
    try:
        import phantom
    except:
        print("error importing phantom")

    phantom.PhantomJob()

if Terminal.GetProperty("Main Job", -1) == 2112:
    try:
        import aran
    except:
        print("error importing aran")

    aran.AranJob()

if Terminal.GetProperty("Main Job", -1) == 6112:
    try:
        import nova
    except:
        print("error importing Nova")

    nova.KaiserJob()

if Terminal.GetProperty("Main Job", -1) == 6512:
    try:
        import nova
    except:
        print("error importing Nova")

    nova.AngelicBusterJob()
    # Job 4 Skill
    if Character.GetJob() == 6512 and Character.GetSkillLevel(65120006) == 30 and Character.GetSkillLevel(65121100) > 15:
        Jobs["Angelic Buster"] = {"Job":[6512], "Skill":["65121100;60011216"], "Delay":[200], "Type":["mixed"]}
    # Level Skills
    if 101 <= Character.GetLevel() <= 115:
        lvlupSkills = [65120006, 65121100]
        for i in lvlupSkills:
            if Character.GetSkillLevel(i) < 30:
                if Character.GetSkillLevel(i) == 10:
                    UseMasteryBook(i, 20)
                elif Character.GetSkillLevel(i) == 20:
                    UseMasteryBook(i, 30)
    # Buy Skill Books
    if Character.GetLevel() == 100:
        book20 = 2431789
        book20Buffer = "00FA 00 0006 00251B2D 0001 00000000 002DC6C0"
        book30 = 2431790
        book30Buffer = "00FA 00 0007 00251B2E 0001 00000000 004C4B40"
        while Inventory.GetCount(book20) < 2:
            Terminal.SetCheckBox("Rush By Level", False)
            utils.BuyItem(buyHeader, blockHeader, book20Buffer, 100000102, 1011100, 2)
        while Inventory.GetCount(book30) < 2:
            utils.BuyItem(buyHeader, blockHeader, book30Buffer, 100000102, 1011100, 2)
        Terminal.SetCheckBox("Rush By Level", True)

    if not Character.HasBuff(2, 65121011) and Character.GetSkillLevel(65121011) > 0:
        Character.UseSkill(65121011)
        time.sleep(0.5)
    if Character.GetJob() == 6500 and Character.GetSkillLevel(65001100) == 20:
        Jobs["Angelic Buster"] = {"Job":[6500], "Skill":["65001100;60011216"], "Delay":[250], "Type":["mixed"]}

if Terminal.GetProperty("Main Job", -1) == 6412:
    try:
        import nova
    except:
        print("error importing Nova")

    nova.CadenaJob()
    if GameState.IsInGame() and not Character.IsOwnFamiliar(9960098):
        Jobs["Cadena"] = {"Job":[6002, 6400, 6410, 6411, 6412], "Skill":[60021278, 64001001, 64001001, 64001001, 64001001], "Delay":[-100, 100, 100, 100, 100], "Type":["auto", "auto", "auto", "auto", "auto"]}
    if len(Field.GetMobs()) > 0 and Character.GetJob() <= 6410 and Character.GetLevel() <= 45 and Field.GetID() < 900000000:
        Terminal.SetCheckBox("Kami Vac", True)


if Terminal.GetProperty("Main Job", -1) == 2512:
    try:
        import shade
    except:
        print("error importing shade")

    shade.ShadeJob(forfeitHeader, skillHeader)
    if Quest.GetQuestState(38011) != 2:
        Terminal.SetCheckBox("Auto SP", False)
        Jobs["Shade"]["Job"] = [2500, 2500, 2500, 2500, 2500]
        Jobs["Shade"]["Type"] = ["dragon", "dragon", "dragon", "dragon", "dragon"]
        Jobs["Shade"]["Delay"] = [1100, 1100, 1100, 1100, 1100]
        Jobs["Shade"]["Skill"] = [25001000, 25001000, 25101000, 25111000, 25121000]
    else:
        Terminal.SetCheckBox("Auto SP", True)


if Terminal.GetProperty("Main Job", -1) == 15512:
    try:
        import ark
    except:
        print("error importing ark")

    try:
        import specter
        import threading
    except:
        print("failed importing specter")


    ark.ArkJob()
    # THREADING PART TESTING
    class Skill():
        def __init__(self, sid):
            self.id = sid
            self.lvl = Character.GetSkillLevel(sid)

    specterID = 155101006
    specterState = 155000007
    abyss = Skill(400051334)
    creep = Skill(155111306)
    speedBase       = 4
    buffList        = []

    def FinalSpeed():
        final = speedBase
        if Character.HasBuff(2, 155101005):
            final += -2
        return final

    skillHeader     = 0x015C
    stateHeader     = 0x0158
    cancelHeader    = 0x015B
    barHeader       = 0x026B

# Time Stamp
# int(time.monotonic() * 1000)

    def CheckAttack():
        if Character.HasBuff(2, specterState):
            #Terminal.SetCheckBox("General FMA", True)
            Terminal.SetCheckBox("Skill Injection", True)
        else:
            Terminal.SetCheckBox("Skill Injection", False)
            #Terminal.SetCheckBox("General FMA", False)


# 015C 093ECF8A 00000014 84612BBB 01 FFFFFFFF 0620 05 00 00000000
    def SkillPacket(skill):
        aPacket = Packet.COutPacket(skillHeader)
        aPacket.Encode4(skill.id)
        aPacket.Encode4(skill.lvl)
        aPacket.EncodeBuffer("B3B073BA 01 FFFFFFFF 8620")
        aPacket.Encode1(FinalSpeed())
        aPacket.EncodeBuffer("00 00000000")
        Packet.SendPacket(aPacket)
        CheckAttack()
        time.sleep(0.1)
        CheckAttack()
        cPacket = Packet.COutPacket(cancelHeader)
        cPacket.Encode4(skill.id)
        cPacket.EncodeBuffer("01")
        Packet.SendPacket(cPacket)
        CheckAttack()

# 0158 00062155 093EA74E 00000001 84612BBB 01 00000003 01 00 00000000 FFFFFFFF 00000000 0000 00
    def SpecterPacket():
        time.sleep(0.05)
        sPacket = Packet.COutPacket(stateHeader)
        sPacket.Encode4(int(time.monotonic() * 1000))
        sPacket.Encode4(specterID)
        sPacket.EncodeBuffer("00000001 B3B073BA 01 FFFFFFFF 00000000 0000 00")
        Packet.SendPacket(sPacket)

    def SendPacketInTime():
        SpecterPacket()
        if creep.lvl >= 1:
            SkillPacket(creep)
            time.sleep(1)

    def is_local_user():
        field_struct = Field.GetCharacters()
        for pos in range(len(field_struct)):
            user = field_struct[pos]
            if not Terminal.IsLocalUser(user.id):
                return False

        return True

    def Ark():
        while not Terminal.GetCheckBox("bot/transfer/meso"):
            Packet.BlockSendHeader(barHeader)
            if GameState.IsInGame() and not Terminal.IsSolvingRune() and not Terminal.IsRushing():
                if is_local_user() and creep.lvl >= 1 and Character.GetJob() in [15511,15512]:
                    if Terminal.GetProperty("gettingHTR", -1) == 5:
                        Terminal.SetCheckBox("Skill Injection", False)
                        time.sleep(0.5)
                    else:
                        CheckAttack()
                        SendPacketInTime()
                        CheckAttack()


    threadRunning = False
    for thread in threading.enumerate():
        if thread.name == "ArkThread":
            threadRunning = True
            break
        
    if not threadRunning and GameState.IsInGame():
        print("Starting Specter")
        arkthread = threading.Thread(name="ArkThread", target=Ark)
        arkthread.start()

    #if Quest.GetQuestState(34940) == 2:
    #    Jobs["Ark"]["Delay"] = [-1,-1,-1,-1,-1]        
    if Character.GetJob() >= 15511:
        Terminal.SetCheckBox("EQUIP Rush", True)
        Terminal.SetCheckBox("Auto Equip", False)

if Terminal.GetProperty("Main Job", -1) == 5112:
    try:
        import mihile
    except:
        print("error importing mihile")

    Terminal.SetCheckBox("No Delay Flash Jump", True)
    mihile.MihileJob()

if Terminal.GetProperty("Main Job", -1) == 14212:
    try:
        import kinesis
    except:
        print("error importing kinesis")

    kinesis.KinesisJob(skillHeader)
    if Character.GetLevel() < 25:
        Jobs["Kinesis"] = { "Job":[14000, 14200, 14210, 14211, 14212], "Skill":[142001001, "142001001;142001000", "142101002;142001000", "142101002;142110000", 142120000], "Delay":[-100, 350, 350, 350, 700], "Type":["auto", "mixed", "mixed", "mixed", "dragon"]}
    Terminal.SetCheckBox("Instant Final Smash", True)

if Terminal.GetProperty("Main Job", -1) == 2312:
    try:
        import mercedes
    except:
        print("error importing mercedes")

    mercedes.MercedesJob()
    Terminal.SetCheckBox("bot/mercedes_hack", True)

if Terminal.GetProperty("Main Job", -1) == 572:
    try:
        import jett
    except:
        print("error importing jett")

    jett.JettJob(forfeitHeader)

if Terminal.GetProperty("Main Job", -1) == 532:
    try:
        import cannoneer
        import explorers
    except:
        print("error import cannon master")

    cannoneer.CannoneerJob()
    if Character.GetJob() >= 501:
        explorers.ExplorersJob(forfeitHeader)


if 100 < Terminal.GetProperty("Main Job", -1) < 523:
    try:
        import explorers
    except:
        print("error importing explorers")

    currJob = str(Terminal.GetProperty("Job Name", -1))
    if Character.GetJob() != Terminal.GetProperty("Main Job", -1):
        explorers.ExplorersJob(forfeitHeader)


        if currJob == "Marksman":
            xbow = 2061000
            if Character.GetLevel() not in [30, 60, 100]:
                if Character.GetMeso() > 9999 and Inventory.GetItemCount(xbow) < 9999:
                    while Inventory.GetItemCount(xbow) < 9999:
                        Terminal.SetCheckBox("Rush By Level", False)
                        xbowBuffer = "00 0027 001F72C8 270F 00000000 00000001"
                        utils.BuyItem(buyHeader, blockHeader, xbowBuffer, 100000102, 1011100, 5)
                    Terminal.SetCheckBox("Rush By Level", True)

        if currJob == "Night Lord":
            if Character.GetJob() == 400 and Character.GetSkillLevel(4101008) <= 0:
                Jobs[currJob] = { "Job": [400, 400, 400, 400, 400], "Skill": [4001334, 4001334, 4001334, 4001334, 4001334], "Delay": [900, 900, 900, 900, 900], "Type":["dragon", "dragon", "dragon", "dragon", "dragon"] }
            if Character.GetLevel() == 30 and Character.GetJob() == 410:
                shur = 2070000
                if Inventory.GetItemCount(shur) < 2400:
                    while Inventory.GetItemCount(shur) < 2400:
                        Terminal.SetCheckBox("Rush By Level", False)
                        print("Buying Shurikens")
                        shurBuffer = "00 002F 001F95F0 0001 00000000 000001F4"
                        utils.BuyItem(buyHeader, blockHeader, shurBuffer, 100000102, 1011100, 15)
                        time.sleep(3)
                    Terminal.SetCheckBox("Rush By Level", True)
            EquipWeapon(1332063, 10, 400)
            EquipWeapon(1472061, 30, 410)

        if currJob == "Corsair":
            if Character.GetJob() == 520 and Character.GetSkillLevel(5201006) <= 0:
                Jobs[currJob] = { "Job": [520,520,520,520,520], "Skill": [5201001,5201001,5201001,5201001,5201001], "Delay": [900, 900, 900, 900, 900], "Type":["dragon", "dragon", "dragon", "dragon", "dragon"] }
            if Character.GetLevel() == 30 and Character.GetJob() == 520:
                bullet = 2330000
                if Inventory.GetItemCount(bullet) < 2400:
                    print("Buying Bullets")
                    bulletBuffer = "00 0036 00238D90 0001 00000000 00000258"
                    utils.BuyItem(buyHeader, blockHeader, bulletBuffer, 100000102, 1011100, 5)

            EquipWeapon(1482014, 10, 500)
            EquipWeapon(1492014, 30, 520)

        if currJob == "Buccaneer":
            EquipWeapon(1482014, 10, 500)

        # Dark Knight
        if currJob == "Dark Knight":
            EquipWeapon(1432002, 30, 1300)
            if Character.GetLevel() == 30 and Character.GetJob() == 130:
                if Character.GetEquippedItemIDBySlot(-11) != 1432002:
                    print("Buying Weapon")
                    spear = Inventory.FindItemByID(1432002)
                    if not spear.valid:
                        if Terminal.GetCheckBox("Rush By Level"):
                            Terminal.SetCheckBox("Rush By Level", False)
                        else:
                            spearBuffer = "00 0033 0015D9C2 0001 00000000 00009C40"
                            utils.BuyItem(buyHeader, blockHeader, spearBuffer, 102000000, 1021000, 1)
                    else:
                        time.sleep(3)
                        Inventory.SendChangeSlotPositionRequest(1, spear.pos, -1, -1)
                        time.sleep(3)
                        Terminal.SetCheckBox("Auto Equip", True)
                        time.sleep(10)
                        Terminal.SetCheckBox("Auto Equip", False)
                        Terminal.SetCheckBox("Rush By Level", True)

        Jobs[currJob] = JobChange(Jobs[currJob])        

    if currJob == "Night Lord":
        if Character.GetJob() == 412 and Character.GetSkillLevel(4121017) <= 0:
            Jobs[currJob] = { "Job": [400, 400, 400, 400, 412], "Skill": [4001334, 4001334, 4001334, 4001334, 4111015], "Delay": [900, 900, 900, 900, 900], "Type":["dragon", "dragon", "dragon", "dragon", "dragon"] }
    # Bishop Shenanigans
    if currJob == "Bishop":
        if Character.GetSkillLevel(155121341) == 0 and Character.GetJob() == 232 and Jobs["Bishop"]["Skill"][4] == 2321001 and not Terminal.IsSolvingRune():
            while not Character.HasBuff(2, 2321001):
                Terminal.SetLineEdit("SISkillID", "using genesis")
                Terminal.SetRadioButton("SIRadioMelee", True)
                Character.UseSkill(2321008)
                time.sleep(2)

if 999 < Terminal.GetProperty("Main Job", -1) < 1600:
    try:
        import cygnus
    except:
        print("error importing cygnus")

    cygnus.CygnusJob(forfeitHeader)


    if Terminal.GetProperty("Job Name", -1) == "Wind Archer" and Character.GetSkillLevel(13101022) > 0:
        if not (Character.HasBuff(2, 13101022) or Character.HasBuff(2, 13110022) or Character.HasBuff(2, 13120003)):
            Character.UseSkill(13101022)
            time.sleep(1)

    # TODO : Fix NIGHT WALKER NO THROWING STAR
    # grenade kami on shadow spark
    if Terminal.GetProperty("Job Name", -1) == "Night Walker":
        currJob = Terminal.GetProperty("Job Name", -1)
        if Character.GetSkillLevel(14001027) == 0:
            Jobs[currJob] = { "Job": [1400], "Skill": [14001020], "Delay": [-100], "Type":["auto"] }
        if Character.GetLevel() > 15:
                shur = 2070000
                if Inventory.GetItemCount(shur) < 2400:
                    while Inventory.GetItemCount(shur) < 2400:
                        Terminal.SetCheckBox("Rush By Level", False)
                        print("Buying Shurikens")
                        shurBuffer = "00 002F 001F95F0 0001 00000000 000001F4"
                        utils.BuyItem(buyHeader, blockHeader, shurBuffer, 100000102, 1011100, 15)
                        time.sleep(3)
                    Terminal.SetCheckBox("Rush By Level", True)

        if Character.GetSkillLevel(14111022) > 0 and Character.GetSkillLevel(155121341) == 0:
            Terminal.SetCheckBox("Grenade Kami", True)
        else:
            Terminal.SetCheckBox("Grenade Kami", False)

    # DW Moon Mode
    if Terminal.GetProperty("Main Job", -1) == 1112:
        if Character.GetSkillLevel(11101022) > 0 and Character.GetJob() <= 1111:
            if not Character.HasBuff(2, 11101022):
                Character.UseSkill(11101022)
        elif Character.GetSkillLevel(11111022) > 0 and Character.GetJob() == 1112:
            if not Character.HasBuff(2, 11111022):
                Character.UseSkill(11111022)
################################################
########
# Main #
########
def Main():
    # NEVER SHOULD BE ON AT ANY FCKING POINT IN TIME
    Terminal.SetComboBox("Familiar0", 1) # jr boogie for everyone
    Terminal.SetCheckBox("filter_familiar", False)
    Terminal.SetCheckBox("timedCCCheck", False)

    # Terminal Status
    if Terminal.GetProperty("legion", -1):
        Terminal.ChangeStatus(str(Terminal.GetProperty("legion", -1)))
    # Processing Login
    ResetMapping()
    move.MovementThread()
    sind.SINDThread()

    if GameState.GetLoginStep() > 0:
        DisableJob()
        utils.ResetProperty()
    if GameState.GetLoginStep() == 2:
        if Terminal.GetProperty("logging", True):
            Terminal.SetProperty("Mapping", True) 
            ResetJob()
            Terminal.SetCheckBox("Auto Login", False)
            Mapping()

            # Guarantee that a file exists on first instance of new account.
            if Login.GetCharCount() == 0:
                CreateCharacter(0)

            GenerateFile()
            data = ReadFile()
            if int(data["Character Slot Count"]) == int(len(data["Character List"])):
                if Login.GetChar(int(data["Character Slot Count"] - 1)).level >= limitLevel:
                    CreateCharacter(int(data["Character Slot Count"]), data)

            GenerateFile(True)
            Terminal.SetCheckBox("Auto Login", True)
            Terminal.SetProperty("logging", False)

    if GameState.IsInGame():
        if not Terminal.GetProperty("logging", True):
            Terminal.SetProperty("logging", True)

        if Character.GetJob() != 3001:
            EnableJob()

        GetLegionQuest()
        AssignTerminal()
        AssignJob()
        AssignSkill()
        if not (Terminal.GetProperty("Job Name", -1) == "Fire/Poison") and not (Terminal.GetProperty("Job Name", -1) == "Mechanic") \
                and not (Terminal.GetProperty("Job Name", -1) == "Wind Archer") \
                and not (Terminal.GetProperty("Job Name", -1) == "Ark"):
            utils.AutoBuff()
        utils.HyperRock(cHeaders[0], cHeaders[1], cHeaders[2], cHeaders[3], cHeaders[4], cHeaders[5], htr[0], htr[1])

        
        if Character.GetLevel() > 10:
            if 33 <= Character.GetLevel() <= 149:
                Terminal.SetCheckBox("bot/puffram", True)
            else:
                if Inventory.FindItemByID(5002099).valid and not Inventory.FindItemByID(5002099).isDead:
                    Terminal.SetCheckBox("bot/puffram", True)
                else:
                    Terminal.SetCheckBox("bot/puffram", False)
                    if Field.GetMobCount() > 0:
                        if not Terminal.IsRushing() and not Terminal.IsSolvingRune():
                            Snail()
        
        if Character.GetLevel() >= 160:
            Terminal.SetCheckBox("HP Pot Rush", True)
        if Character.GetLevel() in [55, 95, 159]:
            # safe guard, star level, whitelist , headers->
            utils.StarForce(False, 11, whitelist, sHeaders[0], sHeaders[1], sHeaders[2], sHeaders[3])

        if Character.GetJob() not in [15511, 15512] and Terminal.GetProperty("resistancejob", True):
            utils.AutoEquip()
        utils.MasterUtilities(hpPot, mpPot)

        UpdateFile()
        if manualOrder:
            if Character.GetLevel() >= Terminal.GetProperty("manualLimit", -1):
                data = ReadFile()
                utils.RushAndBuy(useHeader, buyHeader, blockHeader, data["Max Slots"])
        else:
            if Character.GetLevel() >= limitLevel and Terminal.GetProperty("Main Job", -1) == Character.GetJob():
                data = ReadFile()
                utils.RushAndBuy(useHeader, buyHeader, blockHeader, data["Max Slots"])

#############
# Auxiliars #
#############
def GenerateFile(refresh=False):
    fi = str(os.getcwd()+"/Jobs/Quests/Log/"+GetFileName()+".json")
    if not os.path.isfile(fi):
        with open(fi, "w") as write_file:
            json.dump(CreateDataInfo(), write_file, indent=4)
    else:
        if refresh:
            legion = 0
            mesos = 0
            with open(fi, "r") as read_file:
                fileData = json.load(read_file, object_pairs_hook=OrderedDict)
                accData = CreateDataInfo()

                for key in fileData:
                    if key == "Current Character":
                        for value in fileData[key]:
                            if value != "Mesos":
                                if accData[key]["Position"] > fileData[key]["Position"]:
                                    pos = int(accData[key]["Position"])
                                    lchar = Login.GetChar(pos)
                                    fileData["Character List"].update({pos : { "Name": lchar.name, "Job": lchar.jobid, "Level": lchar.level, "Mesos": "0"}})                                    
                                if fileData[key][value] != accData[key][value]:
                                    fileData[key][value] = accData[key][value]
                    elif key == "Character List":
                        for pos in fileData[key]:
                            if type(fileData[key][pos]["Mesos"]) is int:
                                fileData[key][pos]["Mesos"] = "0"
                                print('error here, fix ltr')
                            mesos += int(fileData[key][pos]["Mesos"].replace(',', ''))
                            legion += int(fileData[key][pos]["Level"])
                            for value in fileData[key][pos]:
                                if not (str(value) == "Mesos"):
                                    if fileData[key][pos][value] != accData[key][int(pos)][value]:
                                        fileData[key][pos][value] = accData[key][int(pos)][value]
                    else:
                        if fileData[key] != accData[key]:
                            fileData[key] = accData[key]

            stringlegion = "Legion Level = "+str(legion)
            Terminal.SetProperty("legion", stringlegion)
            Terminal.ChangeStatus(stringlegion)
            print(stringlegion)
            print("Total Mesos = ", format(mesos, ","))
            with open(fi, "w") as write_file:
                json.dump(fileData, write_file, indent=4)

def UpdateFile():
    resetAfter = 30
    updateTime = time.time() + resetAfter
    if not Terminal.GetProperty("fileUpdate", -1):
        Terminal.SetProperty("fileUpdate", updateTime)
    elif time.time() > Terminal.GetProperty("fileUpdate", -1):
        Terminal.SetProperty("fileUpdate", updateTime)
        x = str(str(time.localtime().tm_hour)+":"+str(time.localtime().tm_min))
        print(x)
        print(Character.GetName(), Terminal.GetProperty("Job Name", -1))
        fi = str(os.getcwd()+"/Jobs/Quests/Log/"+GetFileName()+".json")
        with open(fi, "r") as read_file:
            fileData = json.load(read_file, object_pairs_hook=OrderedDict)
            fileData["Current Character"]["Job ID"] = Character.GetJob()
            fileData["Current Character"]["Level"] = Character.GetLevel()
            fileData["Current Character"]["Mesos"] = format(Character.GetMeso(), ",")
            fileData["Character List"][str(Terminal.GetLineEdit("LoginChar"))]["Job"] = Character.GetJob()
            fileData["Character List"][str(Terminal.GetLineEdit("LoginChar"))]["Level"] = Character.GetLevel()
            fileData["Character List"][str(Terminal.GetLineEdit("LoginChar"))]["Mesos"] = format(Character.GetMeso(), ",")
        with open(fi, "w") as write_file:
            json.dump(fileData, write_file, indent=4)

def ReadFile():
    fi = os.getcwd()+"/Jobs/Quests/Log/"+GetFileName()+".json"
    if os.path.isfile(fi):
        with open(fi, "r") as read_file:
            return json.load(read_file)

def GetFileName():
    profile = Terminal.GetCurrentProfile()
    name = profile.split(".xml")
    name = name[0].split("/")
    return str(name[len(name) -1])

def EnableJob():
    options = ['No Boss Map Effect', 'No Fade Stages', 'No Letter Box', 'No Blue Boxes']
    for i in options:
        Terminal.SetCheckBox(i, True)

def DisableJob():
    # Reset By Job Property
    Terminal.SetProperty("demons1", True)
    Terminal.SetProperty("demons2", True)
    Terminal.SetProperty("demons3", True)
    Terminal.SetProperty("4thJobDone", True)
    Terminal.SetProperty("3rdJobDone", True)
    Terminal.SetProperty("2ndJobDone", True)
    Terminal.SetProperty("1stJobDone", True)
    Terminal.SetProperty("introcygnus", True)
    Terminal.SetProperty("cygnus2", True)
    Terminal.SetProperty("cygnus3", True)
    Terminal.SetProperty("cygnus4", True)    

    options =  ['Instant Final Smash', 'Auto Exceed', 'special/IAReset', 'Auto Equip', 'No Delay Flash Jump', 'macro1_check', 'No Fade Stages',
                'GFMAv2', 'EQUIP Rush', 'bot/mercedes_hack', 'GFMAv1', 'Buy Pet Food', 'macro3_check', 'No Letter Box', 'Grenade Kami', 'Full Map Attack', 
                'Summon Kishin', 'Liberated Spirit Circle Hack', 'Flame Orb Hack', 'No Boss Map Effect']

    for i in options:
        Terminal.SetCheckBox(i, False)

    Terminal.SetLineEdit("SISkillID", "logging")
    Terminal.SetRadioButton("SIRadioMelee", True)
    Terminal.SetCheckBox("Mob Falldown", True)
    Terminal.SetCheckBox("Legit Vac", True)
    Terminal.SetCheckBox("bot/autoDie/waitMins", True)
    Terminal.SetCheckBox("PetItemTeleport", True)
    #Terminal.SetCheckBox("Kami Loot", True)
    #Terminal.SetCheckBox("Kami Vac", True)
    Terminal.SetCheckBox("Auto AP", True)
    Terminal.SetSlider("sliderHP", 60)
    Terminal.SetComboBox("MPKey", 7)
    Terminal.SetCheckBox("Auto SP", True)

def ResetJob():
    # we should be at main lobby, so lets reset the Main Job var
    if Terminal.GetProperty("Main Job", -1) != 2:
        Terminal.SetProperty("Main Job", 2)
        #Terminal.SetProperty("Explorers", -1)

def ResetMapping():
    if Terminal.GetProperty("Mapping", False):
        if Character.GetLevel() >= limitLevel:
            Terminal.SetProperty("Mapping", True)

def AssignSkill():
    if Terminal.GetProperty("gettingHTR", -1) == 5:
        return

    #print(Character.GetMP())
    if (10 < Character.GetMP() <= 50) and Character.GetJob() not in Jobs["Kinesis"]["Job"] and Character.GetJob() not in Jobs["Demon Slayer"]["Job"]:
        Terminal.SetLineEdit("SISkillID", "0")
        return

    if Terminal.GetProperty("Main Job", -1) > 0:
        job = Terminal.GetProperty("Job Name", -1)
        skillList = Jobs[job]["Skill"]
        jobList = Jobs[job]["Job"]
        typeList = Jobs[job]["Type"]
        delayList = Jobs[job]["Delay"]

        if job != "Ark":
            if Character.GetSkillLevel(155121341) == 0:
                skills.SetSkills(jobList, skillList, delayList, typeList, terminalKey, attackKey)

            if Character.GetLevel() >= 160:
                if Character.GetSkillLevel(155121341) == 0 or Character.GetSkillLevel(2321052) == 0:
                    Terminal.SetCheckBox("macro1_check", False)
                    Terminal.SetCheckBox("macro2_check", False)
                    Terminal.SetCheckBox("macro3_check", False)
                    Terminal.SetCheckBox("macro4_check", False)
                    Terminal.SetCheckBox("macro5_check", False)
                    hypers.SetHypers(hyperHeader)
                
                elif Character.GetSkillLevel(155121341) > 0:
                    if job == "Ho Young":
                        skillList = ["2321055;164121001"]
                        delayList = [50]
                    else:
                        skillList = ["2321055;155121041"]
                        delayList = [80]
                    jobList = [Character.GetJob()]
                    typeList = ["mixed"]
                    skills.SetSkills(jobList, skillList, delayList, typeList, terminalKey, attackKey)
                    Terminal.SetRadioButton("SIRadioMelee", True)
                    Terminal.SetCheckBox("special/IAReset", True)
                    
        else:
            if Character.GetJob() >= 15511 and not Character.HasBuff(2, 155000007):
                Terminal.SetCheckBox("Skill Injection", False)
                return
            skills.SetSkills(jobList, skillList, delayList, typeList, terminalKey, attackKey)

def AssignTerminal():
    # Shop Options
    foodShops = [100000102, 103000002]
    if Field.GetID() in foodShops:
        Terminal.SetCheckBox("Buy Pet Food", True)
    else:
        if Terminal.GetCheckBox("Buy Pet Food"):
            Terminal.SetCheckBox("Buy Pet Food", False)
    '''
    # Good to have.
    if Terminal.IsRushing():
        Terminal.SetCheckBox("Kami Vac", False)

    
    # Kami Part
    kamiMaps = [100020400, 102030400]
    if Field.GetID() in kamiMaps:
        if Character.GetJob() in [501, 530, 15511, 15512, 2400, 3500, 6500, 3700, 16400]:
            Terminal.SetCheckBox("Auto Aggro", True)
            return
        Terminal.SetCheckBox("Kami Vac", True)

    if Terminal.GetProperty("Main Job", -1) == 4212 and not Terminal.IsRushing() and Character.GetLevel() < 160:
        Terminal.SetCheckBox("Kami Vac", True)


    # Auto Aggro Part
    jumpMaps = [200020000, 211040100]
    if Field.GetID() in jumpMaps:
        Terminal.SetCheckBox("main/mobnojump", True)
    else:
        Terminal.SetCheckBox("main/mobnojump", False)
    
    aggroMaps = [102030000, 310040300]
    if Field.GetID() in aggroMaps:
        Terminal.SetCheckBox("Auto Aggro", True)
    else:
        if not (1 <= Character.GetLevel() < 10) and not (Character.GetLevel() in [30,60,100]):
            Terminal.SetCheckBox("Auto Aggro", False)
        else:
            Terminal.SetCheckBox("Auto Aggro", True)
    '''

def AssignJob():
    if Terminal.GetProperty("Main Job", -1) == 2:
        if manualOrder:
            if Terminal.GetProperty("manualLimit", -1) <= 0:
                Terminal.SetProperty("manualLimit", 150)
            for i in range(len(manualList)):
                x = manualList[i].split(';')
                if int(x[0]) == int(Terminal.GetLineEdit("LoginChar")):
                    Terminal.SetProperty("Main Job", int(x[1]))
                    Terminal.SetProperty("manualLimit", int(x[2]))
                    break;
            for key in Jobs:
                if int(Terminal.GetProperty("Main Job", -1)) == Jobs[key]["Job"][-1]:
                    Terminal.SetProperty("Job Name", key)
                    break;
            print("Im a", Terminal.GetProperty("Main Job", -1), flush=True)
            return

        exclusions = [501, 530, 531, 532, 430, 431, 432, 433, 434, 508, 570, 571, 572, 301, 330, 331, 332, 3001, 3002, 3100, 3110, 3111, 3112, 3101, 3120, 3121, 3122, 3600, 3610, 3611, 3612]
        for key in Jobs:
            currJob = Character.GetJob()
            if currJob in Jobs[key]["Job"]:
                if 0 <= currJob <= 522:
                    if currJob not in exclusions:
                        if currJob == 0 and ( 3000000 < Field.GetID() < 4000000):
                            Terminal.SetProperty("Main Job", 532)
                            break;
                        if currJob == 0 and Field.GetID() > 900000000:
                            Terminal.SetProperty("Main Job", 332)
                            break;

                        if currJob != Jobs[key]["Job"][-1]:
                            if Terminal.GetProperty("Explorers", -1) > 0:
                                st = Terminal.GetProperty("Explorers", -1)
                                Terminal.SetProperty("Main Job", st)
                                break;
                        else:
                            Terminal.SetProperty("Main Job", Jobs[key]["Job"][-1])
                            break;
                    else:
                        Terminal.SetProperty("Main Job", Jobs[key]["Job"][-1])
                        break;
                elif 1000 <= currJob <= 1512:
                    if currJob not in exclusions:
                        if currJob != Jobs[key]["Job"][-1]:
                            if Terminal.GetProperty("Cygnus", -1) > 0:
                                st = Terminal.GetProperty("Cygnus", -1)
                                Terminal.SetProperty("Main Job", st)
                                break;
                        else:
                            Terminal.SetProperty("Main Job", Jobs[key]["Job"][-1])
                            break;
                    else:
                        Terminal.SetProperty("Main Job", Jobs[key]["Job"][-1])
                        break;
                elif 3000 <= currJob <= 3712:
                    if currJob not in exclusions:
                        if currJob != Jobs[key]["Job"][-1]:
                            if Terminal.GetProperty("Resistance", -1) > 0:
                                st = Terminal.GetProperty("Resistance", -1)
                                Terminal.SetProperty("Main Job", st)
                                break;
                        else:
                            Terminal.SetProperty("Main Job", Jobs[key]["Job"][-1])
                            break;
                    else:
                        if currJob == 3001:
                            st = Terminal.GetProperty("Demons", -1)
                            Terminal.SetProperty("Main Job", st)
                            break;
                        else:
                            Terminal.SetProperty("Main Job", Jobs[key]["Job"][-1])
                            break;
                else:
                    Terminal.SetProperty("Main Job", Jobs[key]["Job"][-1])
                    break;
        for key in Jobs:
            if int(Terminal.GetProperty("Main Job", -1)) == Jobs[key]["Job"][-1]:
                Terminal.SetProperty("Job Name", key)
                break;

        print("Im a", Terminal.GetProperty("Main Job", -1), flush=True)


def Mapping():
    if Terminal.GetProperty("Mapping", True):
        for char in Login.GetChars():
            if char.level >= limitLevel:
                if char.jobid in Explorers:
                    Explorers.remove(char.jobid)
                if char.jobid in Cygnus:
                    Cygnus.remove(char.jobid)
                if char.jobid in Resistance:
                    Resistance.remove(char.jobid)
                if char.jobid in Demons:
                    Demons.remove(char.jobid)

        if len(Explorers) <= 0:
            fexplorer = 1112
        else:
            fexplorer = Explorers[0]            
        if len(Resistance) <= 0:
            fresistance = 1112
        else:
            fresistance = Resistance[0]            
        if len(Demons) <= 0:
            fdemons = 1112
        else:
            fdemons = Demons[0]            
        if len(Cygnus) <= 0:
            fcygnus = 1112
        else:
            fcygnus = Cygnus[0]            

        Terminal.SetProperty("Explorers", fexplorer)
        Terminal.SetProperty("Cygnus", fcygnus)
        Terminal.SetProperty("Resistance", fresistance)
        Terminal.SetProperty("Demons", fdemons)
        #print("Next Explorer = ", fexplorer)
        #print("Next Cygnus = ", fcygnus)
        #print("Next Resistance = ", fresistance)
        #print("Next Demons = ", fdemons)
        Terminal.SetProperty("Mapping", False) 

def GetNextChar(charcount, data):
    MasterList = GetClassesList()
    if MasterList == "Empty":
        print("no list to use as base, fix this somewhere please")

    charlist = Login.GetChars()
    for char in charlist:
        for i in classlist:
            aux = str(MasterList["Class"][i])
            aux = aux.split(';') #classlist[i].split(';')
            if int(char.jobid) == int(aux[0]):
                classlist.remove(i)
                break
    print("Leveling Order = ", classlist)
    if len(classlist) > 0:
        aux = str(MasterList["Class"][classlist[0]])
        aux = aux.split(';') 
        return int(aux[1])
    else:
        return 14

def CreateCharacter(charcount, data=None):
    aux = 0
    ulvl = []
    if charcount == 0:
        Terminal.SetLineEdit("LoginChar", str(charcount))
        Terminal.SetCheckBox("Auto Login", True)
        Terminal.SetComboBox("settings/autochar_job", 6) # First char = Mercedes, shrugs why
        Terminal.SetCheckBox("settings/autochar", True)
        time.sleep(3)
        while not GameState.IsInGame():
            if int(time.time() % 10) == 0:
                Terminal.SetCheckBox("settings/autochar", False)
                print("Creating first Character!", flush=True)
            time.sleep(1)
        if GameState.IsInGame():
            Terminal.Logout()
            time.sleep(5)
        time.sleep(2)
        if GameState.GetLoginStep() >= 0:
            while not GameState.GetLoginStep() == 2:
                time.sleep(1)
                if int(time.time() % 10) == 0:
                    print("waiting some shit stuff", flush=True)
                time.sleep(1)
            Terminal.SetCheckBox("Auto Login", False)
            return

    charlist = Login.GetChars()
    for char in charlist:
        if char.level < limitLevel:
            ulvl.append(aux)
        aux += 1
    if len(ulvl) <= 0:
        Terminal.SetLineEdit("LoginChar", str(charcount))
        Terminal.SetCheckBox("Auto Login", True)
        Terminal.SetComboBox("settings/autochar_job", GetNextChar(int(charcount), data)) # Fix This
        Terminal.SetCheckBox("settings/autochar", True)
        while not GameState.IsInGame():
            if int(time.time() % 10) == 0:
                print("Creating new character!", flush=True)
            time.sleep(3)
        Terminal.SetCheckBox("settings/autochar", False)
        Terminal.Logout()
        time.sleep(3)
        if GameState.GetLoginStep() >= 0:
            while not GameState.GetLoginStep() == 2:
                time.sleep(1)
            print('we should be okay now')
        return

def GetLegionQuest():
    if Quest.GetQuestState(16013) != 2:
        if Character.GetLevel() not in [60, 98, 99, 100] and Character.GetLevel() > 60:
            legion = 0
            fi = os.getcwd()+"/Jobs/Quests/Log/"+GetFileName()+".json"
            with open(fi, "r") as read_file:
                data = json.load(read_file, object_pairs_hook=OrderedDict)
            for char in data["Character List"]:
                legion += int(data["Character List"][char]["Level"])

            if legion >= 501:
                if Terminal.GetCheckBox("Rush By Level"):
                    Terminal.SetCheckBox("Rush By Level", False)
                if Field.GetID() != 261000000:
                    Terminal.Rush(261000000)
                else:
                    if Quest.GetQuestState(16059) != 2:
                        if Quest.GetQuestState(16059) == 0:
                            Character.MoveX(-50, 10000)
                            Quest.StartQuest(16059, 9010106)
                    else:
                        if Quest.GetQuestState(16013) == 0:
                            Character.MoveX(-50, 10000)
                            Quest.StartQuest(16013, 9010106)
                            time.sleep(10)
                            Terminal.SetCheckBox("Rush By Level", True)


    
    
def CreateDataInfo():
    #print("Making Data")
    data = { "Current Character": { "Position" : 0 , "Job ID" : 0, "Level" : 0, "Mesos" : "0"},
            "Character Slot Count" : 0,
            "Free Slots": 0,
            "Max Slots": 0,
            "Character List": {}
            }
    curr = Terminal.GetLineEdit("LoginChar")
    charlist = Login.GetChars()
    slotcount = Login.GetCharSlot()
    charcount = Login.GetCharCount()
    data["Character Slot Count"] = charcount
    data["Max Slots"] = slotcount
    data["Free Slots"] = slotcount - charcount

    aux = 0
    ulvl = []
    for char in charlist:
        if char.level < limitLevel:
            ulvl.append(aux)
        data["Character List"].update({int(aux) : { "Name": char.name, "Job": char.jobid, "Level": char.level, "Mesos": "0"}})
        aux += 1
    
    if curr == "50":
        if len(ulvl) > 0:
            curr = ulvl[0]
        else:
            if int(charcount + 1) > len(charlist):
                curr = 99
            else:
                curr = int(charcount) + 1
    else:
        if int(curr) <= int(charcount):
            if charlist[int(curr)].level >= limitLevel:
                if len(ulvl) > 0:
                    curr = ulvl[0]
                else:
                    if int(charCount) == int(curr):
                        curr = 45
                    else:
                        curr = int(charcount) + 1

    if manualOrder:
        ulvl = []
        for i in range(len(manualList)):
            x = manualList[i].split(';')
            if int(data["Character List"][int(x[0])]["Level"]) < int(x[2]):
                ulvl.append(int(x[0]))
        if len(ulvl) > 0:
            curr = int(ulvl[0])

    print(ulvl)

    job = int(data["Character List"][int(curr)]["Job"])
    level = int(data["Character List"][int(curr)]["Level"])
    data["Current Character"]["Position"] = int(curr)
    data["Current Character"]["Level"] = int(level)
    data["Current Character"]["Job ID"] = int(job)
    Terminal.SetLineEdit("LoginChar", str(curr))
    return data

Main() 
