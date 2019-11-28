# * Variables 
from Classes import *

def Init():
    global config,data
    global ICache,DCache_0,DCache_1,LRUBlockOfSet_0,LRUBlockOfSet_1
    global IntUnitStatus
    # global MemUnitBusy
    global FPAddSubUnitStatus
    global FPMultiplicationUnitStatus
    global FPDivisionUnitStatus
    global FTStage,IDStage,ExeStage,MemStage,WBStage,IU
    global Registers
    global FRegisters
    global instructionCacheRequests,instructionCacheHits,dataCacheRequests,dataCacheHits

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
    DCache_0 = {}
    DCache_1 = {}
    LRUBlockOfSet_0 = 0
    LRUBlockOfSet_1 = 0
    data = {}
    Registers = []
    FRegisters = []
    instructionCacheRequests = 0
    dataCacheRequests = 0
    instructionCacheHits = 0
    dataCacheHits = 0
    for i in range(31):
        FRegisters.append(Register(''))