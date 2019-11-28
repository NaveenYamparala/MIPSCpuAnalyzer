# class student:
#     def __init__(self,n,a):
#         self.full_name = n
#         self.age = a
#     def get_age(self):
#         return self.age

class Instruction:
    def __init__(self,name,operands,fullInstr,config,hex_address):
        self.hex_address = hex_address
        self.full_instr = fullInstr
        self.instrUniqueCode = fullInstr + '_' + hex_address
        self.name = name.upper()
        self.operand1 = operands[0] if len(operands) > 0 else None
        self.operand2 = operands[1] if len(operands) > 1 else None
        self.operand3 = operands[2] if len(operands) > 2 else None
        self.currentStage = ""      # Takes "FT","ID", "EX","WB", "DONE"
        self.prevStage = ""      # Takes "FT","ID", "EX","WB", "DONE"
        self.RAW = "N"
        self.WAR = "N"
        self.WAW = "N"
        self.Struct = "N"
        self.FT = ''
        self.ID = ''
        self.IU = ''
        self.EX = ''
        self.WB = ''
        self.FTCycleCount = 0
        self.IDCycleCount = 1
        self.ExCycleCount = self.findCycleCount(self.name,config) 
        self.FuncUnitUsed = self.findFU(self.name)
        self.isMemStagePresent = True if name.upper() in ['LW', 'SW', 'L.D', 'S.D','DADD','DADDI','DSUB','DSUBI','AND', 'ANDI', 'OR', 'ORI'] else False
        self.resultRegisterType = self.operand1[0] if self.operand1 is not None and self.name != 'J' else ''
        self.resultRegisterNumber = int(self.operand1[1]) if self.operand1 is not None and self.name != 'J' else ''
        self.memCycles = 1 if name.upper() in ['DADD','DADDI','DSUB','DSUBI','AND', 'ANDI', 'OR', 'ORI'] else 0
        self.jumpTo = self.findJumpTo(self.name,operands)
        self.data_ByteAddress = 0
        self.dataWordFetchNumber = 1

    def findJumpTo(self,name,operands):
        if(name in ['BEQ', 'BNE']):
            return operands[2]
        elif(name.upper() == 'J'):
            return operands[0]
        else:
            return ''
        

    def findFU(self,instrName):
        zero = ['HLT','J','BEQ','BNE']
        two = ['DADD','DADDI','DSUB','DSUBI','AND', 'ANDI', 'OR', 'ORI']
        loadStore = ['LW', 'SW', 'L.D', 'S.D']
        addSub = ['ADD.D','SUB.D']
        if (instrName.upper() in zero):
            return 'Nan'
        if(instrName.upper() in two):
            return "INT"
        if(instrName.upper() in loadStore):
            return "INT"
        if(instrName.upper() in addSub):
            return "FP ADDER"
        if(instrName.upper() == 'MUL.D'):
            return "FP MULTIPLIER"
        if(instrName.upper() == 'DIV.D'):
            return "FP DIVIDER"


    def findCycleCount(self,instrName,config):
        zero = ['HLT','J','BEQ','BNE']
        two = ['DADD','DADDI','DSUB','DSUBI','AND', 'ANDI', 'OR', 'ORI']
        loadStore = ['LW', 'SW', 'L.D', 'S.D']
        addSub = ['ADD.D','SUB.D']
        if (instrName.upper() in zero):
            return 'Nan'
        if(instrName.upper() in two):
            return 1
        if(instrName.upper() in loadStore):
            return 1 #+ config.memCycles
        if(instrName.upper() in addSub):
            return config.adderCycles
        if(instrName.upper() == 'MUL.D'):
            return config.multCycles
        if(instrName.upper() == 'DIV.D'):
            return config.divCycles


class Configuration:
    def __init__(self):
        self.adderCycles = 0
        self.adderPipeLined = False
        self.multCycles = 0
        self.multPipeLined = False
        self.divCycles = 0
        self.divPipeLined = False
        self.memCycles = 0
        self.iCacheCycles = 0
        self.dCacheCycles = 0

class Register:
    def __init__(self,data):
        self.data = data
        self.isBusy = False
        self.instructionsResponsible = []

class StageInfo:
    def __init__(self,IsBusy,instr):
        self.IsBusy = IsBusy
        self.InstrResponsibleUniqueCode = instr
        self.InstrResponsibleFTCycle = 0

class FuncUnitInfo:
    def __init__(self,IsBusy,instr):
        self.IsBusy = IsBusy
        self.instrResponsible = instr