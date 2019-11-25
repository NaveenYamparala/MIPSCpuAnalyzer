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

def setResultRegisterStatus(instr,status):
    if(instr.resultRegisterType == 'R'):
        # print(g.Registers[instr.resultRegisterNumber].isBusy)
        if(status != g.Registers[instr.resultRegisterNumber].isBusy): # written because of BNE,DSUB issue without memory 
            g.Registers[instr.resultRegisterNumber].isBusy = status
            g.Registers[instr.resultRegisterNumber].instrResponsible = instr.full_instr
        # print(g.Registers[instr.resultRegisterNumber].isBusy)
    if(instr.resultRegisterType == 'F'):
        if(status != g.FRegisters[instr.resultRegisterNumber].isBusy):
            g.FRegisters[instr.resultRegisterNumber].isBusy = status
            g.FRegisters[instr.resultRegisterNumber].instrResponsible = instr.full_instr

def checkIfOperandsAreBusy(instr):
    reg2 = False
    reg3 = False
    if(instr.name in ['J','HLT']):
        return False
    if(instr.name[0].upper() == 'B'):
        if(instr.operand2[0].upper() in ['F','R'] and RepresentsInt(instr.operand2[1])):
            if(instr.operand2[0].upper() == 'R'):
                reg2 = g.Registers[int(instr.operand2[1])].isBusy and (not g.Registers[int(instr.operand2[1])].instrResponsible == instr.full_instr)
            else:
                reg2 = g.FRegisters[int(instr.operand2[1])].isBusy and (not g.FRegisters[int(instr.operand2[1])].instrResponsible == instr.full_instr)
        
        if(instr.operand1[0].upper() in ['F','R'] and RepresentsInt(instr.operand1[1])):
            if(instr.operand1[0].upper() == 'R'):
                reg3 = g.Registers[int(instr.operand1[1])].isBusy and (not g.Registers[int(instr.operand1[1])].instrResponsible == instr.full_instr)
            else:
                reg3 = g.FRegisters[int(instr.operand1[1])].isBusy and (not g.FRegisters[int(instr.operand1[1])].instrResponsible == instr.full_instr)
    else:
        if(instr.operand2[0].upper() in ['F','R'] and RepresentsInt(instr.operand2[1])):
            if(instr.operand2[0].upper() == 'R'):
                reg2 = g.Registers[int(instr.operand2[1])].isBusy and (not g.Registers[int(instr.operand2[1])].instrResponsible == instr.full_instr)
            else:
                reg2 = g.FRegisters[int(instr.operand2[1])].isBusy and (not g.FRegisters[int(instr.operand2[1])].instrResponsible == instr.full_instr)
            
        if(instr.operand3[0].upper() in ['F','R'] and RepresentsInt(instr.operand3[1])):
            if(instr.operand3[0].upper() == 'R'):
                reg3 = g.Registers[int(instr.operand3[1])].isBusy and (not g.Registers[int(instr.operand3[1])].instrResponsible == instr.full_instr)
            else:
                reg3 = g.FRegisters[int(instr.operand3[1])].isBusy and (not g.FRegisters[int(instr.operand3[1])].instrResponsible == instr.full_instr)
    return reg2 or reg3

# def IsExeStageBusy(instr):
#     if(instr.FuncUnitUsed == "INT"):
#         return g.IntUnitBusy
#     if(instr.FuncUnitUsed == "FP ADDER"):
#         return g.FPAddSubUnitBusy
#     if(instr.FuncUnitUsed == "FP MULTIPLIER"):
#         return g.FPMultiplicationUnitBusy
#     if(instr.FuncUnitUsed == "FP DIVIDER"):
#         return g.FPDivisionUnitBusy

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def doCalculationIfRequired(instr):
    if(not instr.name.endswith('.D')): # .D must use FP registers. So not .D uses intger register
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
            return #! TODO
        if(instr.name == 'SW'):
            return #! TODO
        if(instr.name.find('ADD') != -1):
            if(instr.name == "DADDI"):
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = int(instr.operand3[0]) # In decimal
                result = int(op2,2) + int(op3) # result is integer
                result = '{:032b}'.format(result)
                g.Registers[int(instr.operand1[1])].data = result
            else:
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = g.Registers[int(instr.operand3[1])].data # In binary
                result = int(op2,2) + int(op3,2) # result is integer
                result = '{:032b}'.format(result)
                g.Registers[int(instr.operand1[1])].data = result
            return
        if(instr.name.find('SUB') != -1):
            if(instr.name == "DSUBI"):
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = int(instr.operand3[0]) # In decimal
                result = int(op2,2) - int(op3) # result is integer
                result = '{:032b}'.format(result)
                g.Registers[int(instr.operand1[1])].data = result
            else:
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = g.Registers[int(instr.operand3[1])].data # In binary
                result = int(op2,2) - int(op3,2) # result is integer
                result = '{:032b}'.format(result)
                g.Registers[int(instr.operand1[1])].data = result
            return
        if(instr.name.find('AND') != -1):
            if(instr.name == "ANDI"):
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = int(instr.operand3[0]) # In decimal
                result = int(op2,2) & int(op3) # result is integer
                result = '{:032b}'.format(result)
                g.Registers[int(instr.operand1[1])].data = result
            else:
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = g.Registers[int(instr.operand3[1])].data # In binary
                result = int(op2,2) & int(op3,2) # result is integer
                result = '{:032b}'.format(result)
                g.Registers[int(instr.operand1[1])].data = result
            return
        if(instr.name.find('OR') != -1):
            if(instr.name == "ORI"):
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = int(instr.operand3[0]) # In decimal
                result = int(op2,2) | int(op3) # result is integer
                result = '{:032b}'.format(result)
                g.Registers[int(instr.operand1[1])].data = result
            else:
                op2 = g.Registers[int(instr.operand2[1])].data # In binary
                op3 = g.Registers[int(instr.operand3[1])].data # In binary
                result = int(op2,2) | int(op3,2) # result is integer
                result = '{:032b}'.format(result)
                g.Registers[int(instr.operand1[1])].data = result
            return

def resetRemainingInstructions(startIndex,instructions,instructions_copy):
    sliced_instrs = copy.deepcopy(instructions_copy[startIndex:])
    del instructions[startIndex+1:]
    instructions.extend(sliced_instrs)
    return instructions

def findLoops(instrs,loopInstrs,lbls_dict):
    for lbl,lbl_index in lbls_dict.items():
        for index,i in enumerate(instrs):
            if(i.name.startswith('B')):
                if(i.operand3 == lbl):
                    loopInstrs[lbl] = instrs[lbl_index:index+1]
    return loopInstrs

def initI_Cache():
    g.ICache['00'] = []
    g.ICache['01'] = []
    g.ICache['10'] = []
    g.ICache['11'] = []

def checkInstrCache(instr):
    g.instructionCacheRequests += 1
    print(instr.name)
    binaryAddress = '{:010b}'.format(int(instr.hex_address,16))
    blockNumber = binaryAddress[4:6]
    cacheBlockContents = g.ICache[blockNumber]
    if(instr.hex_address in cacheBlockContents): # Hit
        g.instructionCacheHits += 1
        return g.config.iCacheCycles
    else: # Miss
        data = instr.hex_address
        val = []
        val.append(data)
        for i in range(0,3):
            data = hex(int(data,16) + 4)
            val.append(data)
        g.ICache[blockNumber] = val
        return 2 * (g.config.iCacheCycles + g.config.memCycles)









