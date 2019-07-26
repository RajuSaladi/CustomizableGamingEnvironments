import numpy as np
import pdb
import matplotlib.pyplot as plt


class SignalGeneration:
	
	def RandomRegressionCoefficientGenerator(self,noOfPowers = None):
		coefficientsList = np.array([])
		coefficientsList = np.append(coefficientsList,np.random.random())
		if noOfPowers is None:
			noOfPowers = np.random.choice(5)
		for i in range(0,noOfPowers):
			coefficientsList = np.append(coefficientsList,np.random.random())
		return coefficientsList

	def getSignalForThisInput(self,xc,coefficientsList,thisType):
		thisSignalCombination = sG.SignalCombinator(xc,thisType,len(coefficientsList))
		outputSignal = sG.GenerateSignal(coefficientsList,thisSignalCombination)
		return outputSignal

	def addGeneratedSignalToExisting(self,xc,coefficientsList,thisType,outputSignal = np.array([])):
		thisOutputSignal = self.getSignalForThisInput(xc,coefficientsList,thisType)
		outputSignal = np.append(outputSignal,thisOutputSignal)
		return outputSignal

	def GenerateSignal(self,coefficientsList,xSignalCombination):
		if(coefficientsList.shape == (1,)):
			outputSignal = coefficientsList*xSignalCombination
		else:
			outputSignal = np.matmul(coefficientsList,xSignalCombination)
		return outputSignal

	def SignalCombinator(self,xc,thisType,lengthOfSignal):
		xReg = None
		if(thisType == "Linear"):
			for i in range(0,lengthOfSignal):
				if xReg is None:
					xReg = xc**i
				else:
					xReg = np.vstack((xReg,xc**i))
		elif(thisType == "Sine"):
			for i in range(0,lengthOfSignal):
				if xReg is None:
					xReg = np.sin(xc)**i
				else:
					xReg = np.vstack((xReg,np.sin(xc)**i))
		else:
			for i in range(0,lengthOfSignal):
				if xReg is None:
					xReg = (xc*np.sin(xc))**i
				else:
					xReg = np.vstack((xReg,(xc*np.sin(xc))**i))
		return xReg


	def GenerateSignals(self,NOOFSIGNALS=1,Type = "Linear"):
		SignalSettingList = {}
		for i in range(NOOFSIGNALS):
			SignalSettingList["Signal_{}".format(i+1)] = {}
			SignalSettingList["Signal_{}".format(i+1)]["Type"] = np.random.choice(["Sine","Linear","Linear+Sine"])
			SignalSettingList["Signal_{}".format(i+1)]["coefficientsList"] = sG.RandomRegressionCoefficientGenerator()
		return SignalSettingList

	def GenerateFaultSignal(self,faultSignal,faultType):
		if(faultType == "LinearIncrease"):
			dFaultSignal = faultSignal
		elif(faultType == "LinearDecay"):
			dFaultSignal = -1*faultSignal
		elif(faultType == "ExponentialIncrease"):
			dFaultSignal = faultSignal*np.exp(faultSignal)
		elif(faultType == "ExponentialDecrease"):
			dFaultSignal = -1*faultSignal*np.exp(faultSignal)
		elif(faultType == "Pulse"):
			dFaultSignal = 100
		faultSignal = faultSignal + dFaultSignal
		return faultSignal

	def choseFaultType(self):
		faultList = ["LinearIncrease","LinearDecay","ExponentialIncrease","ExponentialDecrease","Pulse"]
		thisFaultType = np.random.choice(faultList)
		return thisFaultType

	def getFaultParameters(self):
		thisFaultType = self.choseFaultType()
		INITIALFAULTSTARTPOINT = np.random.choice(10)*np.random.random()
		return thisFaultType,INITIALFAULTSTARTPOINT



class PlantControlModel:

	def PlantModel(self,inputX,u1,u2):
		A,B1,B2 = self.getPlantParams()
		noise = np.random.normal(0, 1, inputX.shape)
		#pdb.set_trace()
		dX = np.matmul(A,inputX) + B1*u1 + B2*u2 + noise
		inputX = inputX + dX
		return inputX

	def getPlantParams(self):
		A = np.array([	[0,-0.1,0,0,0],
						[0,0,-0.1,0,0],
						[0,0,0,-0.1,0],
						[0,0,0,0,-0.1],
						[-0.1,0,0,0,0],
					])

		B1 = np.array( [0,0,0,-1,0]).reshape(5,1)

		B2 = np.array([0,0,0,0,0]).reshape(5,1)

		return A,B1,B2

	def operationConditionDefnition(self):
		minInputX = np.array([-20,-40,-20,-100,-10]).reshape(5,1)
		maxInputX = np.array([20,40,20,100,10]).reshape(5,1)
		return minInputX,maxInputX
		
	
	def FaultCheck(self,inputX):
		FaultStatus = False
		violatedSignal = None
		minInputX,maxInputX = self.operationConditionDefnition()
		if((inputX<minInputX).any()):
			FaultStatus = True
			violatedSignal = np.where(inputX<minInputX)[0][0]
		elif((inputX>maxInputX).any()):
			FaultStatus = True
			violatedSignal = np.where(inputX>maxInputX)[0][0]
		return FaultStatus,violatedSignal

class PlantEnvironment:

	
	def __init__(self):
		
		self.PCM = PlantControlModel()
		self.NOOFXSIGNALS = 5
		self.NOOFUSIGNALS = 1
		self.INITIALINPUTSTATE = np.zeros(shape=(self.NOOFXSIGNALS,1))
		self.inputX = self.INITIALINPUTSTATE
		self.inputU = 0
		self.faultInput = 0

		self.outputSignal = self.inputX
		self.faultFlagSignal = self.faultInput
		self.inputUSignal = self.inputU
		self.xAxisSignal = np.array(range(0,1000))
		
			
		self.t = 0
		self.dt = 1

	def step(self,dinputU):

		self.inputX = self.PCM.PlantModel(self.inputX,self.inputU,self.faultInput)
		faultFlag,violatedSignal = self.PCM.FaultCheck(self.inputX)
		
		if(faultFlag == True):
			self.inputX = self.INITIALINPUTSTATE
			print("Faulty Signal is X{}".format(violatedSignal+1))

		self.inputUSignal = np.hstack((self.inputUSignal,self.inputU))
		self.outputSignal = np.hstack((self.outputSignal,self.inputX))
		self.faultFlagSignal = np.hstack((self.faultFlagSignal,int(faultFlag)))


		self.inputU = self.inputU + dinputU
		self.t = self.t + self.dt

	def render(self):
		plt.clf()
		plt.plot(self.xAxisSignal[0:self.t+self.dt][-20:],self.inputUSignal[-20:],label="InputSignal")
		plt.plot(self.xAxisSignal[0:self.t+self.dt][-20:],self.faultFlagSignal[-20:],label="FaultStatus")
		for thisSignalNum in range(self.NOOFXSIGNALS):
			plt.plot(self.xAxisSignal[0:self.t+self.dt][-20:],self.outputSignal[thisSignalNum,-20:],label="Signal_{}".format(thisSignalNum))
		plt.pause(0.05)
		plt.legend(loc = 'best')
		#plt.show()


if __name__ == "__main__":
	
	env = PlantEnvironment()
	
	i = 0
	while(i<1000):
		i = i + 1
		dinputU = np.random.random()
		env.step(dinputU)
		env.render()


"""

if __name__ == "__main__":

	PCM = PlantControlModel()
	NOOFXSIGNALS = 5
	NOOFUSIGNALS = 1
	INITIALINPUTSTATE = np.zeros(shape=(NOOFXSIGNALS,1))
	inputX = INITIALINPUTSTATE
	inputU = 0
	faultInput = 0

	outputSignal = inputX
	faultFlagSignal = faultInput
	inputUSignal = inputU
	xAxisSignal = np.array(range(0,1000))


	t = 0
	dt = 1

	while(t<1000):

		inputX = PCM.PlantModel(inputX,inputU,faultInput)
		faultFlag,violatedSignal = PCM.FaultCheck(inputX)
		
		if(faultFlag == True):
			inputX = INITIALINPUTSTATE
			print("Faulty Signal is X{}".format(violatedSignal+1))

		inputUSignal = np.hstack((inputUSignal,inputU))
		outputSignal = np.hstack((outputSignal,inputX))
		faultFlagSignal = np.hstack((faultFlagSignal,int(faultFlag)))

		dinputU = np.random.random()
		inputU = inputU + dinputU
		t = t + dt

		plt.clf()
		plt.plot(xAxisSignal[0:t+dt][-20:],inputUSignal[-20:],label="InputSignal")
		plt.plot(xAxisSignal[0:t+dt][-20:],faultFlagSignal[-20:],label="FaultStatus")
		for thisSignalNum in range(NOOFXSIGNALS):
			plt.plot(xAxisSignal[0:t+dt][-20:],outputSignal[thisSignalNum,-20:],label="Signal_{}".format(thisSignalNum))
		plt.pause(0.05)
	plt.legend(loc = 'best')
	plt.show()
"""