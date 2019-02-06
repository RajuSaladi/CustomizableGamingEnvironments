import numpy as np
import cv2
import pdb
#import pygame

class Environment:

	def __init__(self):
		#Parameters
		playModeOptions = ["Random","User","Algorithm"]
		self.PlayMode = playModeOptions[2]
		self.frameSize = (300,300,3)
		self.displayWindowName = "CarLaneChange"
		self.noOfLanes = 3
		self.EgoMotionList = ["StayThere","Left","Right","Up","Down"]
		self.StateVectorShape = (1,60)
		self.gapBetweenTrafficVehices = 2

		self.trafficCarWidth = 15
		self.trafficCarLength = 30
		self.trafficMovedX = 0
		self.trafficMovedY = 2

		self.EgoCarWidth = 15
		self.EgoCarLength = 30
		self.EgoMovedX = 2
		self.EgoMovedY = 0

		#Variables
		self.EgoScoreValue = 0
		self.EgoCarPosX = int(self.frameSize[1]/2)
		self.EgoCarPosY = int(self.frameSize[0]-20)
		self.trafficVehiclePosList = []

	def initializeFrame(self):
		inputImage = np.zeros(self.frameSize)
		inputImage = self.drawLanes(inputImage,self.noOfLanes)
		cv2.putText(inputImage,"Score:"+str(self.EgoScoreValue), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 255)
		return inputImage

	def CreateCar(self,inputImage,carPosX,carPosY,carWidth = 15,carLength = 30,carType = "Traffic",):
		box1 = (carPosX,carPosY)
		box2 = (carPosX+carWidth,carPosY+carLength)
		#cv2.rectangle(inputImage, box1, box2 , (255,0,0), 2)
		if(carType == "Traffic"):
			carColour = (0,0,255)
		elif(carType == "EgoVehicle"):
			carColour = (255,0,0)
		else:
			carColour = (0,0,255)
		
		contours = np.array( [[carPosX,carPosY], [carPosX,carPosY+carLength], [carPosX+carWidth, carPosY+carLength], [carPosX+carWidth,carPosY]] )
		smallcontours = np.array( [[carPosX+int(1*carWidth/4),carPosY+int(1*carLength/4)], [carPosX+int(1*carWidth/4),carPosY+int(3*carLength/4)], [carPosX+int(3*carWidth/4), carPosY+int(3*carLength/4)], [carPosX+int(3*carWidth/4),carPosY+int(1*carLength/4)]] )
		cv2.fillPoly(inputImage, pts =[contours], color=carColour)
		cv2.fillPoly(inputImage, pts =[smallcontours], color=(127,127,127))
		return inputImage

	def ViewScreen(self,inputImage):
		cv2.imshow(self.displayWindowName,inputImage)
		k = cv2.waitKey(1) & 0xff

	def drawLanes(self,inputImage,noOfLanes):
		linesPosition = []
		for i in range(0,noOfLanes+1):
			xPos = int(i*inputImage.shape[1]/noOfLanes)
			cv2.line(inputImage, (xPos, 0), (xPos, inputImage.shape[0]), (255,255,255), 2)
		return inputImage

	def NewTrafficAddition(self,inputImage,trafficVehiclePosList,noOfLanes,carWidth,carLength,TRAFFICTHRESHOLD = 0.95,GAPBETWEENTRAFFICVEHICLES = 2):
		#noOfCarsToAdd = np.random.choice(noOfLanes - 1)
		lanesForCarsToFillList = np.random.sample(noOfLanes) > max(TRAFFICTHRESHOLD,0.3)
		laneWidth = int(inputImage.shape[1]/noOfLanes)
		#print(lanesForCarsToFillList)
		for i in range(len(lanesForCarsToFillList)):
			eachLaneForTraffic = lanesForCarsToFillList[i]
			if(eachLaneForTraffic == True):
				#pdb.set_trace()
				carPosX = i*laneWidth + np.random.choice(laneWidth-carWidth)
				if(self.CarPlacementCheck(trafficVehiclePosList,carPosX,0,carWidth,carLength,GAPBETWEENTRAFFICVEHICLES) == True):
					inputImage = self.CreateCar(inputImage,carPosX,0,carWidth,carLength,"Traffic")
					trafficVehiclePosList.append((carPosX,0,carWidth,carLength,"Traffic"))
		return inputImage,trafficVehiclePosList

	def getTheTrafficVisualization(self,inputImage,trafficVehiclePosList,carWidth,carLength):
		for eachVehiclePos in trafficVehiclePosList:
			carPosX,carPosY,carWidth,carLength,carType = eachVehiclePos
			inputImage = self.CreateCar(inputImage,carPosX,carPosY,carWidth,carLength,carType)
		return inputImage
	
	def movementOfTraffic(self,trafficVehiclePosList,imageShape,trafficMovedX,trafficMovedY):
		newTrafficVehiclePosList = []
		for i in range(0,len(trafficVehiclePosList)):
			carPosX,carPosY,carWidth,carLength,carType = trafficVehiclePosList[i]
			if(carType == "Traffic"):
				carPosX = carPosX + trafficMovedX
				carPosY = carPosY + trafficMovedY
				if((carPosX>imageShape[1]) | (carPosY>imageShape[0])):
					continue
			newTrafficVehiclePosList.append((carPosX,carPosY,carWidth,carLength,carType))
		return newTrafficVehiclePosList


	def VectorizedIou(self,currentBox, boxesList):
		x11, y11, w1, l1,_ = currentBox#np.split(currentBox, 4, axis=1)
		x12 = x11+w1
		y12 = y11 + l1
		x21, y21, w2, l2,_ = np.split(boxesList, 5, axis=1)
		#pdb.set_trace()
		x21 = np.asarray(x21, dtype=float)
		y21 = np.asarray(y21, dtype=float)
		w2 = np.asarray(w2, dtype=float)
		l2 = np.asarray(l2, dtype=float)
		x22 = x21 + w2
		y22 = y21+l2

		xA = np.maximum(x11, np.transpose(x21))
		yA = np.maximum(y11, np.transpose(y21))
		xB = np.minimum(x12, np.transpose(x22))
		yB = np.minimum(y12, np.transpose(y22))
		interArea = np.maximum((xB - xA + 1), 0) * np.maximum((yB - yA + 1), 0)
		boxAArea = (x12 - x11 + 1) * (y12 - y11 + 1)
		boxBArea = (x22 - x21 + 1) * (y22 - y21 + 1)
		iou = interArea / (boxAArea + np.transpose(boxBArea) - interArea)
		return iou
	
	def CarPlacementCheck(self,trafficVehiclePosList,carPosX,carPosY,carWidth,carLength,gapBetweenTrafficVehices):
		CheckFlag = False
		currentBox = [carPosX-gapBetweenTrafficVehices,carPosY-gapBetweenTrafficVehices,carWidth+2*gapBetweenTrafficVehices,carLength+2*gapBetweenTrafficVehices,"__"]
		if(len(trafficVehiclePosList) == 0):
			return True
		trafficVehiclePosList = np.array(trafficVehiclePosList)
		iouTotal = self.VectorizedIou(currentBox,trafficVehiclePosList)
		#pdb.set_trace()
		if(iouTotal.sum() == 0):
			CheckFlag = True
		return CheckFlag

	def EgoPlacement(self,inputImage):
		inputImage = self.CreateCar(inputImage,self.EgoCarPosX,self.EgoCarPosY,self.EgoCarWidth,self.EgoCarLength,"EgoVehicle")
		return inputImage

	def MovementOfEgoVehicle(self,EgoMotion):
		if(EgoMotion == "Left"):
			self.EgoCarPosX = self.EgoCarPosX - self.EgoMovedX
		elif(EgoMotion == "Right"):
			self.EgoCarPosX = self.EgoCarPosX + self.EgoMovedX
		elif(EgoMotion == "Up"):
			self.EgoCarPosY = self.EgoCarPosY - self.EgoMovedY
		elif(EgoMotion == "Down"):
			self.EgoCarPosY = self.EgoCarPosY + self.EgoMovedY
		else:
			self.EgoCarPosX = self.EgoCarPosX
			self.EgoCarPosY = self.EgoCarPosY

	def EgoMotionPlanner(self,inputAction):
		if(self.PlayMode == "User"):	
			EgoMotion = self.GetkeyStroke()
		elif(self.PlayMode == "Random"):
			EgoMotion =  np.random.choice(self.EgoMotionList)
		else:
			EgoMotion =  self.EgoMotionList[inputAction]
		return EgoMotion

	def getRewardValue(self):
		NotHitToTraffic = self.CarPlacementCheck(self.trafficVehiclePosList,self.EgoCarPosX,self.EgoCarPosY,self.EgoCarWidth,self.EgoCarLength,self.gapBetweenTrafficVehices)
		#pdb.set_trace()
		if(NotHitToTraffic == True):
			rewardValue = 1
		else:
			rewardValue =  -10
		
		if(self.checkForWithinScreen(self.EgoCarPosX,self.EgoCarPosY,self.EgoCarWidth,self.EgoCarLength,self.frameSize) == False):
			rewardValue = rewardValue-100
		self.EgoScoreValue = self.EgoScoreValue + rewardValue
		if(rewardValue <0):
			done = False
		elif(self.EgoScoreValue > 1000):
			done = True
		else:
			done = False
		return rewardValue,done

	def checkForWithinScreen(self,carPosX,carPosY,carWidth,carLength,frameSize):
		checkFlag =True
		if((carPosX+carWidth >= frameSize[1]) | (carPosX < 0)):
			checkFlag = False
		#if((carPosY+carLength >= frameSize[0]) | (carPosY < 0)):
			#checkFlag = False
		#pdb.set_trace()
		return checkFlag

	def GetTrafficeSceneAsStateVector(self):

		if(len(self.trafficVehiclePosList) > 0):
			temp = np.array(self.trafficVehiclePosList)
			#pdb.set_trace()
			temp = temp[:,0:2].reshape(1,-1)
			if(temp.shape[1] >= self.StateVectorShape[1]-2):
				temp = temp[:,0:self.StateVectorShape[1]-2]
			else:
				result = np.zeros((self.StateVectorShape[0],self.StateVectorShape[1]-2))
				result[:temp.shape[0],:temp.shape[1]] = temp
				temp = result
		else:
			temp = np.zeros((self.StateVectorShape[0],self.StateVectorShape[1]-2))

		temp = np.append(np.array([self.EgoCarPosX,self.EgoCarPosY]).reshape(1,-1),temp)
		currentState = temp.reshape(self.StateVectorShape)
		currentState = np.array(currentState,dtype = np.float32)
		currentState = currentState.reshape(-1)
		return currentState

	def GetkeyStroke(self):
		keyStrokeCaptured = cv2.waitKeyEx(30)
		if (keyStrokeCaptured == 2490368):
			userAction =  "Up"
		elif (keyStrokeCaptured == 2621440):
			userAction =  "Down"
		elif (keyStrokeCaptured == 2424832):
			userAction =  "Left"
		elif (keyStrokeCaptured == 2555904):
			userAction = "Right"
		else:
			userAction = "StayThere"
		return userAction

	def reset(self):
		self.EgoScoreValue = 0
		self.EgoCarPosX = int(self.frameSize[1]/2)
		self.EgoCarPosY = int(self.frameSize[0]-20)
		self.trafficVehiclePosList = []
		thisState = self.GetTrafficeSceneAsStateVector()
		self.currentFrame = self.initializeFrame()
		return thisState

	def render(self):
		self.currentFrame = self.initializeFrame()
		self.currentFrame = self.EgoPlacement(self.currentFrame)
		self.currentFrame = self.getTheTrafficVisualization(self.currentFrame,self.trafficVehiclePosList,self.trafficCarWidth,self.trafficCarLength)
		self.ViewScreen(self.currentFrame)
	
	def DynamicEnvironMentChange(self):
		self.currentFrame,self.trafficVehiclePosList = self.NewTrafficAddition(self.currentFrame,self.trafficVehiclePosList,self.noOfLanes,self.trafficCarWidth,self.trafficCarLength)
		self.trafficVehiclePosList = self.movementOfTraffic(self.trafficVehiclePosList,self.frameSize,self.trafficMovedX,self.trafficMovedY)

	def step(self,inputActionIndex = 0):
		self.DynamicEnvironMentChange()
		egoAction = self.EgoMotionPlanner(inputActionIndex)
		self.MovementOfEgoVehicle(egoAction)
		thisRewardValue,doneStatus = self.getRewardValue()
		thisState = self.GetTrafficeSceneAsStateVector()
		return thisState,thisRewardValue,doneStatus,"_"

"""
if __name__ == "__main__":
	
	env = Environment()
	env.reset()
	for i in range(1000):
		env.render()
		observation, reward, done,info = env.step()
		if(done == -1):
			print("GameOver")
			print("Final Score obtained is "+str(env.EgoScoreValueValue))
			break
		elif(done == 1):
			print("You Won")
			print("Final Score obtained is "+str(env.EgoScoreValueValue))
			break
"""