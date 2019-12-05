# * Functions
import GlobalVariables as g
import copy

def parseOperands(opArray):
    if(len(opArray) == 0): # HLT instruction
        return []
    if(len(opArray) == 3):
        st1 = opArray[0].split(",")
        op1 = st1[0].strip()
        st2 = opArray[1].split(",")
        op2 = st2[0].strip()
        op3 = opArray[2].strip()
    else:
        st1 = opArray[0].strip()
        op1 = st1.split(",")[0] # F1
        st2 = opArray[1].strip().split("(")
        op2 = st2[0]
        op3 = st2[1].split(")")[0]
    return op1,op2,op3

def toggleFunctionalUnitStatus(instr):
    if(instr.FuncUnitUsed == "INT"):
        g.IntUnitStatus.IsBusy = not g.IntUnitStatus.IsBusy
        g.IntUnitStatus.InstrResponsible = instr.full_instr
    if(instr.FuncUnitUsed == "FP ADDER"):
        g.FPAddSubUnitStatus.IsBusy = not g.FPAddSubUnitStatus.IsBusy
        g.FPAddSubUnitStatus.InstrResponsible = instr.full_instr
    if(instr.FuncUnitUsed == "FP MULTIPLIER"):
        g.FPMultiplicationUnitStatus.IsBusy = not g.FPMultiplicationUnitStatus.IsBusy
        g.FPMultiplicationUnitStatus.InstrResponsible = instr.full_instr
    if(instr.FuncUnitUsed == "FP DIVIDER"):
        g.FPDivisionUnitStatus.IsBusy = not g.FPDivisionUnitStatus.IsBusy
        g.FPDivisionUnitStatus.InstrResponsible = instr.full_instr

def checkIfFunctionalUnitBusy(instr):
    if(instr.FuncUnitUsed == "INT"):
        return g.IntUnitStatus.IsBusy and g.IntUnitStatus.InstrResponsible != instr.full_instr
    if(instr.FuncUnitUsed == "FP ADDER"):
        return g.FPAddSubUnitStatus.IsBusy and g.FPAddSubUnitStatus.InstrResponsible != instr.full_instr and not g.config.adderPipeLined
    if(instr.FuncUnitUsed == "FP MULTIPLIER"):
        return g.FPMultiplicationUnitStatus.IsBusy and g.FPMultiplicationUnitStatus.InstrResponsible != instr.full_instr and not g.config.multPipeLined
    if(instr.FuncUnitUsed == "FP DIVIDER"):
        return g.FPDivisionUnitStatus.IsBusy and g.FPDivisionUnitStatus.InstrResponsible != instr.full_instr and not g.config.divPipeLined

def checkIfResultRegisterBusy(instr):
    if(instr.name in ['J','HLT','BNE','BEQ','S.D','SW']):
        return False
    if(instr.resultRegisterType == 'R'):
        resRegister = g.Registers[instr.resultRegisterNumber]
        return resRegister.isBusy and not (instr.instrUniqueCode in resRegister.instructionsResponsible and resRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
    else:
        resRegister = g.FRegisters[instr.resultRegisterNumber]
        return resRegister.isBusy and not (instr.instrUniqueCode in resRegister.instructionsResponsible and resRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])

def setResultRegisterStatus(instr,status):
    if(instr.resultRegisterType == 'R'):
        resultReg = g.Registers[instr.resultRegisterNumber]
        if(status == resultReg.isBusy): 
            resultReg.instructionsResponsible.append(instr.instrUniqueCode)
        else:
            if(status == True):
                resultReg.isBusy = status
                resultReg.instructionsResponsible = [instr.instrUniqueCode]
            else:
                resultReg.instructionsResponsible.remove(instr.instrUniqueCode)
                if(len(resultReg.instructionsResponsible) == 0):
                    resultReg.isBusy = status

    if(instr.resultRegisterType == 'F'):
        resultReg = g.FRegisters[instr.resultRegisterNumber]
        if(status == resultReg.isBusy): 
            resultReg.instructionsResponsible.append(instr.instrUniqueCode)
        else:
            if(status == True):
                resultReg.isBusy = status
                resultReg.instructionsResponsible = [instr.instrUniqueCode]
            else:
                resultReg.instructionsResponsible.remove(instr.instrUniqueCode)
                if(len(resultReg.instructionsResponsible) == 0):
                    resultReg.isBusy = status

def checkIfOperandsAreBusy(instr):
    reg2Status = False
    reg3Status = False
    if(instr.name in ['J','HLT']):
        return False
    if(instr.name in ['SW','S.D']):
        if(instr.operand1[0].upper() == 'R'):
                op2RRegister = g.Registers[int(instr.operand1[1])]
                reg2Status = op2RRegister.isBusy and not (instr.instrUniqueCode in op2RRegister.instructionsResponsible and op2RRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
        else:
            op2FRegister = g.FRegisters[int(instr.operand1[1])]
            reg2Status = op2FRegister.isBusy and not (instr.instrUniqueCode in op2FRegister.instructionsResponsible and op2FRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
    
    if(instr.name[0].upper() == 'B'):
        if(instr.operand2[0].upper() in ['F','R'] and RepresentsInt(instr.operand2[1])):
            if(instr.operand2[0].upper() == 'R'):
                op2RRegister = g.Registers[int(instr.operand2[1])]
                reg2Status = op2RRegister.isBusy and not (instr.instrUniqueCode in op2RRegister.instructionsResponsible and op2RRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
            else:
                op2FRegister = g.FRegisters[int(instr.operand2[1])]
                reg2Status = op2FRegister.isBusy and not (instr.instrUniqueCode in op2FRegister.instructionsResponsible and op2FRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
        
        if(instr.operand1[0].upper() in ['F','R'] and RepresentsInt(instr.operand1[1])):
            if(instr.operand1[0].upper() == 'R'):
                op1RRegister = g.Registers[int(instr.operand1[1])]
                reg3Status = op1RRegister.isBusy and not (instr.instrUniqueCode in op1RRegister.instructionsResponsible and op1RRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
            else:
                op1FRegister = g.FRegisters[int(instr.operand1[1])]
                reg3Status = op1FRegister.isBusy and not (instr.instrUniqueCode in op1FRegister.instructionsResponsible and op1FRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
    else:
        if(instr.operand2[0].upper() in ['F','R'] and RepresentsInt(instr.operand2[1])):
            if(instr.operand2[0].upper() == 'R'):
                op2RRegister = g.Registers[int(instr.operand2[1])]
                reg2Status = op2RRegister.isBusy and not (instr.instrUniqueCode in op2RRegister.instructionsResponsible and op2RRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
            else:
                op2FRegister = g.FRegisters[int(instr.operand2[1])]
                reg2Status = op2FRegister.isBusy and not (instr.instrUniqueCode in op2FRegister.instructionsResponsible and op2FRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
            
        if(instr.operand3[0].upper() in ['F','R'] and RepresentsInt(instr.operand3[1])):
            if(instr.operand3[0].upper() == 'R'):
                op3RRegister = g.Registers[int(instr.operand3[1])]
                reg3Status = op3RRegister.isBusy and not (instr.instrUniqueCode in op3RRegister.instructionsResponsible and op3RRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
            else:
                op3FRegister = g.FRegisters[int(instr.operand3[1])]
                reg3Status = op3FRegister.isBusy and not (instr.instrUniqueCode in op3FRegister.instructionsResponsible and op3FRegister.instructionsResponsible.index(instr.instrUniqueCode) in [0])
    return reg2Status or reg3Status

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def doCalculationIfRequired(instr):
    if(not instr.name.endswith('.D')): # .D must use FP registers. So not .D uses integer register
        if(instr.name.startswith('B')): # Branching instruction
            if(instr.name == 'BNE'):
                op1 = g.Registers[int(instr.operand1[1])].data
                op2 = g.Registers[int(instr.operand2[1])].data
                if(op1 != op2):
                    return 'TAKEN'
                else:
                    return 'NOT TAKEN'
            if(instr.name == 'BEQ'):
                op1 = g.Registers[int(instr.operand1[1])].data
                op2 = g.Registers[int(instr.operand2[1])].data
                if(op1 == op2):
                    return 'TAKEN'
                else:
                    return 'NOT TAKEN'
        if(instr.name == 'J'):
                return 'TAKEN'
        if(instr.name == 'LW'):
            resReg = g.Registers[int(instr.operand1[1])]
            op2 = instr.operand2
            op3 = g.Registers[int(instr.operand3[1])].data
            address = int(op2) + twosComplToDec(op3)
            instr.data_ByteAddress = address
            data = g.data[str(address)]
            resReg.data = data
            return 
        if(instr.name == 'SW'):
            op2 = instr.operand2
            op3 = g.Registers[int(instr.operand3[1])].data
            resAddress = int(op2) + twosComplToDec(op3)
            instr.data_ByteAddress = resAddress
            resData = g.Registers[int(instr.operand1[1])].data
            g.data[str(resAddress)] = resData
            return 
        if(instr.name.find('ADD') != -1):
            if(instr.name == "DADDI"):
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = int(instr.operand3[0]) # In decimal
                result = twosComplToDec(op2) + int(op3) # result is integer
                # result = '{:032b}'.format(result)
                result = decToTwosCompl(result)
                g.Registers[int(instr.operand1[1])].data = result
            else: # DADD
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = g.Registers[int(instr.operand3[1])].data # In binary
                result = twosComplToDec(op2) + twosComplToDec(op3) # result is integer
                # result = '{:032b}'.format(result)
                result = decToTwosCompl(result)
                g.Registers[int(instr.operand1[1])].data = result
            return
        if(instr.name.find('SUB') != -1):
            if(instr.name == "DSUBI"):
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = int(instr.operand3[0]) # In decimal
                result = twosComplToDec(op2) - int(op3) # result is integer
                # result = '{:032b}'.format(result)
                result = decToTwosCompl(result)
                g.Registers[int(instr.operand1[1])].data = result
            else: #DSUB
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = g.Registers[int(instr.operand3[1])].data # In binary
                result = twosComplToDec(op2) - twosComplToDec(op3) # result is integer
                # result = '{:032b}'.format(result)
                result = decToTwosCompl(result)
                g.Registers[int(instr.operand1[1])].data = result
            return
        if(instr.name.find('AND') != -1):
            if(instr.name == "ANDI"):
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = int(instr.operand3[0]) # In decimal
                result = twosComplToDec(op2) & int(op3) # result is integer
                # result = '{:032b}'.format(result)
                result = decToTwosCompl(result)
                g.Registers[int(instr.operand1[1])].data = result
            else: #AND
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = g.Registers[int(instr.operand3[1])].data # In binary
                result = twosComplToDec(op2) & twosComplToDec(op3) # result is integer
                # result = '{:032b}'.format(result)
                result = decToTwosCompl(result)
                g.Registers[int(instr.operand1[1])].data = result
            return
        if(instr.name.find('OR') != -1):
            if(instr.name == "ORI"):
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = int(instr.operand3[0]) # In decimal
                result = twosComplToDec(op2) | int(op3) # result is integer
                # result = '{:032b}'.format(result)
                result = decToTwosCompl(result)
                g.Registers[int(instr.operand1[1])].data = result
            else: #OR
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = g.Registers[int(instr.operand3[1])].data # In binary
                result = twosComplToDec(op2) | twosComplToDec(op3) # result is integer
                # result = '{:032b}'.format(result)
                result = decToTwosCompl(result)
                g.Registers[int(instr.operand1[1])].data = result
            return
    else:
        if(instr.name == 'L.D'):
            resReg = g.Registers[int(instr.operand1[1])]
            op2 = instr.operand2
            op3 = g.Registers[int(instr.operand3[1])].data
            address = int(op2) + twosComplToDec(op3)
            instr.data_ByteAddress = address
        if(instr.name == 'S.D'):
            op2 = instr.operand2
            op3 = g.Registers[int(instr.operand3[1])].data
            resAddress = int(op2) + twosComplToDec(op3)
            instr.data_ByteAddress = resAddress


def resetRemainingInstructions(startIndex,instructions,instructions_copy):
    sliced_instrs = copy.deepcopy(instructions_copy[startIndex:])
    del instructions[startIndex:]
    instructions.extend(sliced_instrs)
    return instructions


# finds loops and returns loop + 1 instructions
def findLoops(instrs,loopInstrs,lbls_dict,jumpDirection):
    for lbl,lbl_index in lbls_dict.items():
        for index,i in enumerate(instrs):
            if(i.name.startswith('B') or i.name == 'J'):
                if(i.jumpTo == lbl):
                    if(lbl_index > index):
                        jumpDirection[lbl] = 'forward'
                        loopInstrs[lbl] = []
                    else:
                        jumpDirection[lbl] = 'backward'
                        loopInstrs[lbl] = instrs[lbl_index:index+2]
    return loopInstrs,jumpDirection

def initI_Cache():
    g.ICache['00'] = []
    g.ICache['01'] = []
    g.ICache['10'] = []
    g.ICache['11'] = []

def initD_Cache():
    g.DCache_0[0] = []
    g.DCache_0[1] = []
    g.DCache_1[0] = []
    g.DCache_1[1] = []


def checkInstrCache(instr):
    g.instructionCacheRequests += 1
    # print(instr.name)
    # binaryAddress = '{:010b}'.format(int(instr.hex_address,16))
    # blockNumber = binaryAddress[4:6]
    byteAddress = int(instr.hex_address,16)
    blockNumber = byteAddress/16
    blockNumber = '{:02b}'.format(int(blockNumber))
    cacheBlockContents = g.ICache[blockNumber]
    if(instr.hex_address in cacheBlockContents): # Hit
        g.instructionCacheHits += 1
        return g.config.iCacheCycles, False
    else: # Miss
        if(g.memoryBus.IsBusy):
            g.instructionCacheHits -= 1
            return g.config.iCacheCycles, True

        # Setting memory bus busy
        g.memoryBus.IsBusy = True
        g.memoryBus.instrResponsible = instr.instrUniqueCode
        
        data = hex(int(int(instr.hex_address,16)/16) * 16) # gives first word address of cache block
        val = []
        val.append(data)
        for i in range(0,3):
            data = hex(int(data,16) + 4)
            val.append(data)
        g.ICache[blockNumber] = val
        return 2 * (g.config.iCacheCycles + g.config.memCycles), False

def checkDataCache(instr,wordNumber):
    g.dataCacheRequests += 1
    blockNumberInmemory = instr.data_ByteAddress / 16   # Block number = (byte address)/(bytes per block)
    setNumber = int(blockNumberInmemory) % 2  # Set number = (Block number) modulo (Number of sets in the cache)
    instr.dataWordFetchNumber = wordNumber
    if(instr.name.startswith('L')): # Loads
        if(setNumber == 0):
            for key,value in g.DCache_0.items():
                if(instr.data_ByteAddress in value): # Hit
                    g.dataCacheHits +=1
                    g.LRUBlockOfSet_0 = 1 if key == 0 else 0
                    return g.config.dCacheCycles, False
            # Miss
            if(g.memoryBus.IsBusy):
                return g.config.dCacheCycles, True

            # Setting memory bus busy
            g.memoryBus.IsBusy = True
            g.memoryBus.instrResponsible = instr.instrUniqueCode
            
            data = int(instr.data_ByteAddress/16) * 16 # gives first word address of cache block
            val = []
            for i in range(0,4):
                val.append(data + (i*4))
            g.DCache_0[g.LRUBlockOfSet_0] = val
            g.LRUBlockOfSet_0 = 1 if g.LRUBlockOfSet_0 == 0 else 0
            return 2 * (g.config.dCacheCycles + g.config.memCycles), False
        else:
            for key,value in g.DCache_1.items():
                if(instr.data_ByteAddress in value): # Hit
                    g.dataCacheHits +=1
                    g.LRUBlockOfSet_1 = 1 if key == 0 else 0
                    return g.config.dCacheCycles, False
            # Miss
            if(g.memoryBus.IsBusy and g.memoryBus.instrResponsible != instr.instrUniqueCode):
                return g.config.dCacheCycles, True
            
            # Setting memory bus busy
            g.memoryBus.IsBusy = True
            g.memoryBus.instrResponsible = instr.instrUniqueCode

            data = int(instr.data_ByteAddress/16) * 16 # gives first word address of cache block
            val = []
            # val.append(data)
            for i in range(0,4):
                val.append(data + (i*4))
            g.DCache_1[g.LRUBlockOfSet_1] = val
            g.LRUBlockOfSet_1 = 1 if g.LRUBlockOfSet_1 == 0 else 0
            return 2 * (g.config.dCacheCycles + g.config.memCycles), False
    else: # Stores
        if(setNumber == 0):
            for key,value in g.DCache_0.items():
                if(instr.data_ByteAddress in value): # Hit 
                    g.dataCacheHits +=1
                    g.LRUBlockOfSet_0 = 1 if key == 0 else 0
                    if(not key in g.DirtyBlockOfSet_0): # Make it dirty
                        g.DirtyBlockOfSet_0.append(key)
                    return g.config.dCacheCycles, False
                    # else:
                    #     g.DirtyBlockOfSet_0.remove(key)
                    #     g.LRUBlockOfSet_0 = key
            # Miss
            if(g.memoryBus.IsBusy):
                return g.config.dCacheCycles, True
            
            # Setting memory bus busy
            g.memoryBus.IsBusy = True
            g.memoryBus.instrResponsible = instr.instrUniqueCode

            data = int(instr.data_ByteAddress/16) * 16 # gives first word address of cache block
            val = []
            for i in range(0,4):
                val.append(data + (i*4))
            g.DCache_0[g.LRUBlockOfSet_0] = val
            if(g.LRUBlockOfSet_0 in g.DirtyBlockOfSet_0): # Removing dirty bit
                g.DirtyBlockOfSet_0.remove(g.LRUBlockOfSet_0)
            g.LRUBlockOfSet_0 = 1 if g.LRUBlockOfSet_0 == 0 else 0
            return 2 * (g.config.dCacheCycles + g.config.memCycles), False
        else:
            for key,value in g.DCache_1.items():
                if(instr.data_ByteAddress in value): # Hit
                    g.dataCacheHits +=1
                    g.LRUBlockOfSet_1 = 1 if key == 0 else 0
                    if(not key in g.DirtyBlockOfSet_1): # Make it dirty
                        g.DirtyBlockOfSet_1.append(key)
                    return g.config.dCacheCycles, False
                    # else:
                    #     g.DirtyBlockOfSet_1.remove(key)
                    #     g.LRUBlockOfSet_1 = key
            # Miss
            if(g.memoryBus.IsBusy):
                return g.config.dCacheCycles, True
            
            # Setting memory bus busy
            g.memoryBus.IsBusy = True
            g.memoryBus.instrResponsible = instr.instrUniqueCode

            data = int(instr.data_ByteAddress/16) * 16 # gives first word address of cache block
            val = []
            # val.append(data)
            for i in range(0,4):
                val.append(data + (i*4))
            g.DCache_1[g.LRUBlockOfSet_1] = val
            if(g.LRUBlockOfSet_1 in g.DirtyBlockOfSet_1): # Removing dirty bit
                g.DirtyBlockOfSet_1.remove(key)
            g.LRUBlockOfSet_1 = 1 if g.LRUBlockOfSet_1 == 0 else 0
            return 2 * (g.config.dCacheCycles + g.config.memCycles), False

def checkMemoryBufferConflict(instructions,index,cycleCount):
    i = index + 1
    while i <= len(instructions):
        if(instructions[i].prevStage == 'FT' and not (g.IDStage.IsBusy and g.IDStage.InstrResponsibleUniqueCode != instructions[i].instrUniqueCode) and instructions[i].currentStage != 'ID'):
            return True
        else:
            return False

                 


def decToTwosCompl(decimal):
    s = bin(decimal & int("1"*32, 2))[2:]
    return ("{0:0>%s}" % (32)).format(s)

def twosComplToDec(binary_string):
    val = int(binary_string,2)
    bits = len(binary_string)
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val 









