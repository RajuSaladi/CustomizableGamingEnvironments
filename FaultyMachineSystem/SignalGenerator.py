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


	def GenerateSignals(self,NOOFSIGNALS=1):
		SignalSettingList = {}
		for i in range(NOOFSIGNALS):
			SignalSettingList["Signal_{}".format(i+1)] = {}
			SignalSettingList["Signal_{}".format(i+1)]["Type"] = np.random.choice(["Sine","Linear","Linear+Sine"])
			SignalSettingList["Signal_{}".format(i+1)]["coefficientsList"] = sG.RandomRegressionCoefficientGenerator()
		return SignalSettingList


if __name__ == "__main__":

	sG = SignalGeneration()
	NOOFSIGNALS = 10
	#inputSignal = np.array([2,10])
	thisType = np.random.choice(["Sine","Linear","Linear+Sine"])
	coefficientsList = sG.RandomRegressionCoefficientGenerator()
	
	SignalSettingList = sG.GenerateSignals(NOOFSIGNALS)
	
	i = 0
	di = 10
	outputSignal = {}
	xAxisSignal = np.array(range(0,1000))
	while(i<1000):
		inputSignal = np.array(range(i,di+i))
		i = i + di
		plt.clf()
		for thisSignalNum in range(1,NOOFSIGNALS+1):
			thisSignalName = "Signal_{}".format(thisSignalNum)
			if(i == di):
				outputSignal[thisSignalName] = np.array([])
			#for i in range(1,len(inputSignal)):
			#outputSignal[thisSignalName] = sG.addGeneratedSignalToExisting(inputSignal[i-1:i],SignalSettingList[thisSignalName]["coefficientsList"],SignalSettingList[thisSignalName]["Type"],outputSignal[thisSignalName])
			#plt.plot(inputSignal[0:i],outputSignal[thisSignalName],label="thisSignalName")
			outputSignal[thisSignalName] = sG.addGeneratedSignalToExisting(inputSignal,SignalSettingList[thisSignalName]["coefficientsList"],SignalSettingList[thisSignalName]["Type"],outputSignal[thisSignalName])
			plt.plot(xAxisSignal[0:i][-200:],outputSignal[thisSignalName][-200:],label=thisSignalName)
		plt.pause(0.005)
		#plt.cla()
	plt.legend(loc = 'best')
	plt.show()
