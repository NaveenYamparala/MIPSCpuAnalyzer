# * Variables 
from Classes import *

def Init():
    global config
    global ICache
    global IntUnitStatus
    # global MemUnitBusy
    global FPAddSubUnitStatus
    global FPMultiplicationUnitStatus
    global FPDivisionUnitStatus
    global FTStage,IDStage,ExeStage,MemStage,WBStage,IU
    global Registers
    global FRegisters
    global instructionCacheRequests,instructionCacheHits

    config = Configuration()
    IntUnitStatus = FuncUnitInfo(False,'')  # IU
    #MemUnitBusy = False
    FPAddSubUnitStatus = FuncUnitInfo(False,'')
    FPMultiplicationUnitStatus = FuncUnitInfo(False,'')
    FPDivisionUnitStatus = FuncUnitInfo(False,'')
    FTStage = StageInfo(False,'')
    IDStage = StageInfo(False,'')
    ExeStage = StageInfo(False,'')
    MemStage = StageInfo(False,'')
    WBStage = StageInfo(False,'')
    IU = StageInfo(False,'')
    ICache = {}
    Registers = []
    FRegisters = []
    instructionCacheRequests = 0
    instructionCacheHits = 0
    for i in range(31):
        FRegisters.append(Register(''))