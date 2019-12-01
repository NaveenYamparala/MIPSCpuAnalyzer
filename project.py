import sys
from Classes import *
from Functions import *
import GlobalVariables as g
from tabulate import tabulate
import copy

# * Getting arguments from command line
# instFile = sys.argv[1]
# dataFile = sys.argv[2]
# regFile = sys.argv[3]
# configFile = sys.argv[4]
# resultFile = sys.argv[5]
instFile = "inst.txt"
dataFile = "data.txt"
regFile = "reg.txt"
configFile = "config.txt"
resultFile = "result.txt"


g.Init()  # Init Global Variables


# * Reading Data File
with open(dataFile,'r') as c:
    dLines = c.readlines()
    memAddr = 256  # As of now this is in decimal , equivalant to 0x100
    for d in dLines:
        d = d.replace("\n","")
        g.data[str(memAddr)] = d
        memAddr = memAddr + 4
# print(data)

# * Reading Reg File
with open(regFile,'r') as c:
    regs = c.readlines()
    for r in regs:
        r = r.replace("\n","")
        g.Registers.append(Register(r))


# * Reading and Processing Config file
# with open("config.txt",'r') as c:
with open(configFile,'r') as c:
    cLines = c.readlines()
    # g.config = Configuration()
    # TODO Try doing this in a better way
    g.config.adderCycles = int(cLines[0].split(':')[1].split(',')[0].strip())
    g.config.adderPipeLined = 1 if cLines[0].split(':')[1].split(',')[1].strip() == "yes" else 0
    g.config.multCycles = int(cLines[1].split(':')[1].split(',')[0].strip())
    g.config.multPipeLined = 1 if cLines[1].split(':')[1].split(',')[1].strip() == "yes" else 0
    g.config.divCycles = int(cLines[2].split(':')[1].split(',')[0].strip())
    g.config.divPipeLined = 1 if cLines[2].split(':')[1].split(',')[1].strip() == "yes" else 0
    g.config.memCycles = int(cLines[3].split(':')[1])
    g.config.iCacheCycles = int(cLines[4].split(':')[1])
    g.config.dCacheCycles = int(cLines[5].split(':')[1])


# * Reading Instr File
with open(instFile,'r') as c:
    instrLines = c.readlines()
    instructions = [] # to hold objects of type Instruction class
    labaels_dict = {}
    hex_address = '0x0'
    for index,i in enumerate(instrLines):
        i = i.replace('\n','')
        i = i.replace('\t','')
        i = i.upper()
        if(len(i) != 0):
            i = i.strip()
            if(i.find(":") == -1): # instruction doesn't have label  ADD.D F4, F6, F2
                if( i == 'HLT'):
                    instructions.append(Instruction(i, '', i,g.config,hex_address))
                    hex_address = hex(int(hex_address,16) + 4)
                    continue
                str1 = i.split(" ",1)
                name = str1[0].strip() #ADD.D
                if(name.upper() == 'J'):
                    instructions.append(Instruction(name.upper(), [str1[1]], i,g.config,hex_address))
                    hex_address = hex(int(hex_address,16) + 4)
                    continue
                str1.pop(0)
                op = str1[0].split(',')
                operands = parseOperands(op)
                instructions.append(Instruction(name, operands, i,g.config,hex_address))
            else: # instruction has label   GG: L.D F1, 4(R4)
                label = i.split(":")[0]
                labaels_dict[label] = index
                str1 = i.split(":")[1].strip() #L.D F1, 4(R4)
                str2 = str1.split(" ",1) #['L.D','F1,','4(R4)']
                name = str2[0].strip() # L.D
                str2.pop(0)
                str2[0] = str2[0].strip()
                op = str2[0].split(',')
                operands = parseOperands(op) # ['F1,','4(R4)']
                instructions.append(Instruction(name, operands, i,g.config,hex_address))
            hex_address = hex(int(hex_address,16) + 4)

# * Cache
initI_Cache()
initD_Cache()
        
copyOfInstructions = copy.deepcopy(instructions)
instrsCopy = copy.deepcopy(copyOfInstructions)
loopBodyInstructions = {}
jumpDirection = {}
loopBodyInstructions,jumpDirection = findLoops(instrsCopy,loopBodyInstructions,labaels_dict,jumpDirection)
# I assumed unconditional jumps will always be forward

# * Simulate 
cntinue = True
cycleCount = 0
doneCount = 0
end = 0
while(cntinue):
    cycleCount += 1
    doneCount = 0
    for index,inst in enumerate(instructions):
        end = 0
        if(inst.currentStage == 'DONE'):
            doneCount += 1
            if(doneCount == (len(instructions))):
                cntinue = False
            continue

        ### FT STAGE ###
        elif(inst.prevStage == ''):  # New Instruction or Inst is continuing in FT stage
            if(g.FTStage.IsBusy and g.FTStage.InstrResponsibleUniqueCode != inst.instrUniqueCode):
                continue # Can't go to FT Stage
            else: 
                if(inst.FTCycleCount == 0 ): # Will execute once per instr # and (index == 0 or instructions[index-1].name != 'HLT')
                    inst.FTCycleCount = checkInstrCache(inst)

                inst.currentStage = 'FT'
                inst.FTCycleCount -= 1

                g.FTStage.IsBusy = True
                g.FTStage.InstrResponsibleUniqueCode = inst.instrUniqueCode

                if(inst.FTCycleCount == 0):
                    inst.prevStage = 'FT'
                    if(instructions[index-1].isBranchTaken == True):
                        inst.currentStage = 'DONE'
                        g.FTStage.IsBusy = False
                        g.FTStage.InstrResponsibleUniqueCode = inst.instrUniqueCode
                        inst.FT = cycleCount
                    break

        ### ID STAGE ###
        elif(inst.prevStage == 'FT'):
            if(g.IDStage.IsBusy and g.IDStage.InstrResponsibleUniqueCode != inst.instrUniqueCode):
                continue # Can't go to ID Stage
            else:
                if(inst.currentStage != 'ID'):
                    # Setting the Result registers to Busy  (for RAW Hazard)
                    setResultRegisterStatus(inst,True)

                    g.FTStage.IsBusy = False
                    g.FTStage.InstrResponsibleUniqueCode = ''

                    inst.FT = cycleCount - 1
                    inst.currentStage = 'ID'

                if(instructions[index-1].isBranchTaken == True):
                    inst.currentStage = 'DONE'
                    inst.FT = cycleCount
                    break

                inst.currentStage = 'ID'
                inst.IDCycleCount -= 1

                g.IDStage.IsBusy = True
                g.IDStage.InstrResponsibleUniqueCode = inst.instrUniqueCode

                if(inst.IDCycleCount <= 0 ): # ID Stage is finished -- and not IsExeStageBusy(inst)
                    if(not checkIfResultRegisterBusy(inst)):
                        if(not checkIfOperandsAreBusy(inst)):

                            inst.prevStage = 'ID'

                            if(inst.ExCycleCount == 'Nan'): # i.e instruction is HLT or BNE or BEQ or J
                                # inst.currentStage = 'DONE'

                                # g.IDStage.IsBusy = False
                                # g.IDStage.InstrResponsibleUniqueCode = ''

                                output = doCalculationIfRequired(inst)

                                if(output == 'TAKEN'):
                                    inst.currentStage = 'DONE'
                                    inst.isBranchTaken = True

                                    g.IDStage.IsBusy = False
                                    g.IDStage.InstrResponsibleUniqueCode = ''

                                    if(jumpDirection[inst.jumpTo] == 'backward'):
                                        instructions = resetRemainingInstructions(index+2,instructions,copyOfInstructions)
                                        instructions[index+2:1]=copy.deepcopy(loopBodyInstructions[inst.jumpTo])
                                        copyOfInstructions = copy.deepcopy(instructions)
                                    else:
                                        lbl_index = labaels_dict[inst.jumpTo]
                                        del instructions[index+2:lbl_index] 
                                        copyOfInstructions = copy.deepcopy(instructions)                                       
                                    # instructions[index+1].FT = cycleCount
                                    # instructions[index+1].currentStage = 'DONE'

                                    #Resetting Result register statuses
                                    setResultRegisterStatus(inst,False)

                                    # Resetting FU statuses
                                    g.FTStage.IsBusy = False
                                    g.IDStage.IsBusy = False
                                    g.IU.IsBusy = False
                                    g.MemStage.IsBusy = False
                                    g.WBStage.IsBusy = False
                                    g.FPAddSubUnitStatus.IsBusy = False
                                    g.FPDivisionUnitStatus.IsBusy = False
                                    g.FPMultiplicationUnitStatus.IsBusy = False

                                    inst.ID = cycleCount # ID cycleCount is done here to accycleCount for stalls in ID stage
                                    # break
                        else:
                            inst.RAW = 'Y'
                    else:
                        inst.WAW = 'Y'
                        if(checkIfOperandsAreBusy(inst)):
                            inst.RAW = 'Y'

                    continue
                
        ### EXE STAGE ###
        elif(inst.prevStage == 'ID'):

            if(inst.isMemStagePresent): ## EXE stage = (IU + MEM)

                # IU
                if(inst.prevStage == 'ID' and inst.currentStage == 'ID' and not g.IU.IsBusy):

                    #Releasing ID stage
                    if(inst.ID == ''):
                        g.IDStage.IsBusy = False
                        g.IDStage.InstrResponsibleUniqueCode = ''
                        inst.ID = cycleCount-1

                    inst.currentStage = 'IU'

                    g.IU.IsBusy = True
                    g.IU.InstrResponsibleUniqueCode = inst.instrUniqueCode

                    doCalculationIfRequired(inst)

                    continue

                # MEM
                if(g.MemStage.IsBusy and g.MemStage.InstrResponsibleUniqueCode != inst.instrUniqueCode):
                    inst.Struct = 'Y'
                else:
                    if(inst.memCycles == 0 and inst.currentStage != 'MEM'):
                        if(checkMemoryBufferConflict(instructions, index,cycleCount)): # returns True if there is buffer conflict
                            inst.Struct = 'Y'
                            continue
                        inst.memCycles = checkDataCache(inst,1)

                    inst.currentStage = 'MEM'

                    # Releasing IU
                    if(inst.IU == ""):
                        inst.IU = cycleCount -1
                        g.IU.IsBusy = False
                        g.IU.InstrResponsibleUniqueCode = ''

                    # Occupying MEM
                    g.MemStage.IsBusy = True
                    g.MemStage.InstrResponsibleUniqueCode = inst.instrUniqueCode

                    inst.memCycles -= 1
                    if(inst.memCycles == 0): # and not g.WBStage.IsBusy
                        if(inst.name.endswith('.D') and inst.dataWordFetchNumber == 1):
                            inst.data_ByteAddress += 4
                            inst.memCycles = checkDataCache(inst,2)
                        else:
                            inst.prevStage = 'EXE'

            else: ## EXE Stage = ( EXE )
                if(inst.ExCycleCount == 'Nan'):
                    inst.ID = cycleCount-1
                    inst.currentStage = 'DONE'

                    g.IDStage.IsBusy = False
                    g.IDStage.InstrResponsibleUniqueCode = ''
                    continue

                if(not checkIfFunctionalUnitBusy(inst)):
                    inst.ExCycleCount -= 1
                    if(inst.currentStage != 'EXE'):
                        #Releasing ID stage
                        g.IDStage.IsBusy = False
                        g.IDStage.InstrResponsibleUniqueCode = ''
                        inst.ID = cycleCount-1


                        inst.currentStage = 'EXE'
                        toggleFunctionalUnitStatus(inst)
                    if(inst.ExCycleCount == 0): # and not g.WBStage.IsBusy
                        inst.prevStage = 'EXE'
                else:
                    inst.Struct = 'Y'

        ### WB STAGE ###
        elif(inst.prevStage == 'EXE'):
            if(g.WBStage.IsBusy and g.WBStage.InstrResponsibleUniqueCode != inst.instrUniqueCode and g.WBStage.InstrResponsibleFTCycle < inst.FT):
                inst.Struct = 'Y'
                continue 
            else:
                
                inst.EX = cycleCount - 1

                #Occupying WB unit
                g.WBStage.IsBusy = True
                g.WBStage.InstrResponsibleUniqueCode = inst.instrUniqueCode
                g.WBStage.InstrResponsibleFTCycle = inst.FT

                if(inst.isMemStagePresent):
                    g.MemStage.IsBusy = False
                    g.MemStage.InstrResponsibleUniqueCode = ''
                else:
                    toggleFunctionalUnitStatus(inst)
                

                inst.prevStage = 'WB'
                inst.WB = cycleCount  # Read and write done in same cycle
            
                # Releasing result register
                setResultRegisterStatus(inst,False) # Read and write done in same cycle

        ## Done Stage ## This stage is written just to release WB Stage Unit in next cycle after WB stage is done
        elif(inst.prevStage == 'WB'):

            if(g.WBStage.InstrResponsibleUniqueCode == inst.instrUniqueCode):
                # Releasing WB unit
                g.WBStage.IsBusy = False
                g.WBStage.InstrResponsibleUniqueCode = ''

            inst.currentStage = 'DONE'


# * Writing to Result file
resultLine = ['Instruction','FT','ID','EX','WB','RAW','WAR','WAW','Struct']
with open(resultFile,'w') as r:
    bigArr = []
    for index,i in enumerate(instructions):
        arr = []
        arr.append(i.full_instr)
        arr.append(str(i.FT))
        if(index != len(instructions)-1):
            arr.append(str(i.ID))
            # arr.append(str(i.IU))
            arr.append('' if i.EX == 0 else str(i.EX))
            arr.append('' if i.WB == 0 else str(i.WB))
            arr.append('' if i.ID == '' else str(i.RAW))
            arr.append('' if i.ID == '' else str(i.WAR))
            arr.append('' if i.ID == '' else str(i.WAW))
            arr.append('' if i.ID == '' else str(i.Struct))
                
        # else:
        #     arr.append(i.full_instr)
        bigArr.append(arr)
    r.writelines(tabulate(bigArr,headers=resultLine,tablefmt="plain"))
    r.write('\n\n')
    r.write('\nTotal number of access requests for instruction cache: ' + str(g.instructionCacheRequests))
    r.write('\nNumber of instruction cache hits: ' + str(g.instructionCacheHits))
    r.write('\nTotal number of access requests for data cache: ' + str(g.dataCacheRequests))
    r.write('\nNumber of data cache hits: ' + str(g.dataCacheHits))
    