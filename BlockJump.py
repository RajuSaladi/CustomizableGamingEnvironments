import numpy as np
import cv2

class Environment:

	def __init__(self):
		#Parameters
		playModeOptions = ["Random","User"]
		self.PlayMode = playModeOptions[0]#"Random"#"User"#
		self.frameSize = (300,800,3)
		self.displayWindowName = "DragonJump"
		self.groundLevel = 10
		self.GravityStrength = 2
		self.EgoMotionList = ["Left","Right","StayThere","Up"]
		self.StateVectorShape = (1,60)
		self.gapBetweenTrafficVehices = 2
		self.UPCOUNTERTHRESHOLD = 10

		self.EgoWidth = 15
		self.EgoLength = 30
		self.EgoMovedX = 10
		self.EgoMovedY = 10

		self.BlockWidth = 15
		self.BlockLength = 30
		self.blockMovedX = 5
		self.blockMovedY = 0

		#Variables
		self.EgoScoreValue = 0
		self.EgoX = 0
		self.EgoY = self.frameSize[0]-self.groundLevel-self.EgoLength
		self.existingBlocksList = []
		self.egoUpMotionCounter = 0

	def initialzeFrame(self):
		inputImage = np.zeros(self.frameSize)
		inputImage = self.DrawGroundLine(inputImage,self.groundLevel)
		cv2.putText(inputImage,"Score:"+str(self.EgoScoreValue), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 255)
		return inputImage
	
	def viewFrame(self,inputImage):
		cv2.imshow(self.displayWindowName,inputImage)
		k = cv2.waitKey(1) & 0xff

	def DrawGroundLine(self,inputImage,groundLevel = 10):
		cv2.line(inputImage, (0, inputImage.shape[0] - groundLevel), (inputImage.shape[1],inputImage.shape[0] - groundLevel), (255,255,255), 2)
		return inputImage

	def EgoPlacement(self,inputImage):
		inputImage = self.CreateBox(inputImage,self.EgoX,self.EgoY,self.EgoWidth,self.EgoLength,Type = "EgoPlayer")
		return inputImage
	
	def addNewBlocksToScene(self,inputImage,existingBlocksList,noOfLevels,boxWidth,boxLength,frameSize = (300,300,3),groundLevel = 10,TRAFFICTHRESHOLD = 0.95,GAPBETWEENTRAFFICVEHICLES = 100):
		noOfboxsToAdd = np.random.choice(noOfLevels)
		lanesForboxsToFillList = np.random.sample(noOfLevels) > max(TRAFFICTHRESHOLD,0.3)
		laneWidth = int(inputImage.shape[1]/noOfLevels)
		for i in range(0,len(lanesForboxsToFillList)):
			eachLaneForTraffic = lanesForboxsToFillList[i]
			if(eachLaneForTraffic == True):
				boxPosX = laneWidth-boxWidth
				boxPosY = frameSize[0]-groundLevel-boxLength
				if(self.BlockPlacementCheck(existingBlocksList,boxPosX,boxPosY,boxWidth,boxLength,GAPBETWEENTRAFFICVEHICLES) == True):
					inputImage = self.CreateBox(inputImage,boxPosX,boxPosY,boxWidth,boxLength,"Block")
					existingBlocksList.append((boxPosX,boxPosY,boxWidth,boxLength,"Block"))
		return inputImage,existingBlocksList

	def getTheBlocksVisualization(self,inputImage,existingBlocksList,boxWidth,boxLength):
		for eachBlockPos in existingBlocksList:
			boxPosX,boxPosY,boxWidth,boxLength,boxType = eachBlockPos
			inputImage = self.CreateBox(inputImage,boxPosX,boxPosY,boxWidth,boxLength,boxType)
		return inputImage

	def movementOfBlocks(self,existingBlocksList,blockMovedX,blockMovedY):
		newBlockPosList = []
		for i in range(0,len(existingBlocksList)):
			boxPosX,boxPosY,boxWidth,boxLength,boxType = existingBlocksList[i]
			if(boxType == "Block"):
				boxPosX = boxPosX - blockMovedX
				boxPosY = boxPosY - blockMovedY
				#if((boxPosX>imageShape[1]) | (boxPosY>imageShape[0])):
				if((boxPosX<0) | (boxPosY<0)):
					continue
			newBlockPosList.append((boxPosX,boxPosY,boxWidth,boxLength,boxType))
		return newBlockPosList

	def movementOfEgoBlock(self,EgoMotion):
		self.EgoX,self.EgoY = self.AddGravityEffect(self.EgoX,self.EgoY,self.GravityStrength)
		if(EgoMotion == "Left"):
			self.EgoX = max(self.EgoX - self.EgoMovedX,0)
		elif(EgoMotion == "Right"):
			self.EgoX = min(self.EgoX + self.EgoMovedX,self.frameSize[1])
		elif(EgoMotion == "Up"):
			self.EgoY = max(self.EgoY - self.EgoMovedY,0)
		elif(EgoMotion == "Down"):
			self.EgoY = min(self.EgoY + self.EgoMovedY,self.frameSize[0]-self.groundLevel-self.EgoLength)
		else:
			self.EgoX = self.EgoX
			self.EgoY = self.EgoY
		self.EgoX = min(self.frameSize[1]-self.EgoWidth,max(0,self.EgoX))
		self.EgoY = min(self.frameSize[0]-self.groundLevel-self.EgoLength,max(0,self.EgoY))


	def EgoMotionPlanner(self):
		if(self.PlayMode == "User"):	
			EgoMotion = self.GetkeyStroke()
		elif(self.PlayMode == "Random"):
			EgoMotion =  np.random.choice(self.EgoMotionList)
		else:
			EgoMotion =  np.random.choice(self.EgoMotionList)
		if(EgoMotion == "Up"):
			self.egoUpMotionCounter += 1
		if(self.egoUpMotionCounter >=self.UPCOUNTERTHRESHOLD):
			if(EgoMotion == "Up"):
				EgoMotion = "StayThere"
			if(self.EgoY >= self.frameSize[0]-self.groundLevel-self.EgoLength):
				self.egoUpMotionCounter = 0
		return EgoMotion

	def AddGravityEffect(self,EgoPosX,EgoPosY,GravityStrength):
		EgoPosX = EgoPosX
		EgoPosY = EgoPosY + GravityStrength
		return EgoPosX,EgoPosY

	def GetkeyStroke(self):
		#keyStrokeCaptured = cv2.waitKeyEx()
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
		#print("Selected useraction is "+str(userAction))
		return userAction

	def getRewardValue(self):
		NotHitToTraffic = self.BlockPlacementCheck(self.existingBlocksList,self.EgoX,self.EgoY,self.EgoWidth,self.EgoLength,self.gapBetweenTrafficVehices)
		#pdb.set_trace()
		if(NotHitToTraffic == True):
			rewardValue = 1
		else:
			rewardValue =  -1
		self.EgoScoreValue = self.EgoScoreValue + rewardValue
		if(rewardValue <0):
			done = -1
		elif(self.EgoScoreValue > 1000):
			done = 1
		else:
			done = 0
		return rewardValue,done

	def CreateBox(self,inputImage,PosX,PosY,Width = 15,Length = 30,Type = "Block"):
		box1 = (PosX,PosY)
		box2 = (PosX+Width,PosY+Length)
		#cv2.rectangle(inputImage, box1, box2 , (255,0,0), 2)
		if(Type == "Block"):
			Colour = (0,0,255)
		elif(Type == "EgoPlayer"):
			Colour = (255,0,0)
		else:
			Colour = (0,0,255)
		
		contours = np.array( [[PosX,PosY], [PosX,PosY+Length], [PosX+Width, PosY+Length], [PosX+Width,PosY]] )
		smallcontours = np.array( [[PosX+int(1*Width/4),PosY+int(1*Length/4)], [PosX+int(1*Width/4),PosY+int(3*Length/4)], [PosX+int(3*Width/4), PosY+int(3*Length/4)], [PosX+int(3*Width/4),PosY+int(1*Length/4)]] )
		cv2.fillPoly(inputImage, pts =[contours], color=Colour)
		cv2.fillPoly(inputImage, pts =[smallcontours], color=(127,127,127))
		return inputImage

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
	
	def BlockPlacementCheck(self,existingBlocksList,boxPosX,boxPosY,boxWidth,boxLength,gapBetweenBlocks = 2):
		CheckFlag = False
		currentBox = [boxPosX-gapBetweenBlocks,boxPosY-gapBetweenBlocks,boxWidth+2*gapBetweenBlocks,boxLength+2*gapBetweenBlocks,"__"]
		if(len(existingBlocksList) == 0):
			return True
		existingBlocksList = np.array(existingBlocksList)
		iouTotal = self.VectorizedIou(currentBox,existingBlocksList)
		#pdb.set_trace()
		if(iouTotal.sum() == 0):
			CheckFlag = True
		return CheckFlag

	def GetSceneAsStateVector(self):
		if(len(self.existingBlocksList) > 0):
			temp = np.array(self.existingBlocksList)
			#pdb.set_trace()
			temp = temp[:,0:2].reshape(1,-1)
			if(temp.shape[1] >= self.StateVectorShape[1]-2):
				temp = temp[:,0:self.StateVectorShape[1]-2]
				#loopNum = 1
			else:
				result = np.zeros((self.StateVectorShape[0],self.StateVectorShape[1]-2))
				result[:temp.shape[0],:temp.shape[1]] = temp
				temp = result
				#loopNum = 2
		else:
			temp = np.zeros((self.StateVectorShape[0],self.StateVectorShape[1]-2))

		temp = np.append(np.array([self.EgoX,self.EgoY]).reshape(1,-1),temp)
		currentState = temp.reshape(self.StateVectorShape)
		currentState = np.array(currentState,dtype = np.float32)
		return currentState

	
	def reset(self):
		self.EgoScoreValue = 0
		self.EgoX = 0
		self.EgoY = self.frameSize[0]-self.groundLevel-self.EgoLength
		self.existingBlocksList = []
		self.egoUpMotionCounter = 0

	def render(self):
		self.currentFrame = self.initialzeFrame()
		self.currentFrame = self.EgoPlacement(self.currentFrame)
		self.currentFrame = self.getTheBlocksVisualization(self.currentFrame,self.existingBlocksList,self.BlockWidth,self.BlockLength)
		self.viewFrame(self.currentFrame)
	
	def DynamicEnvironMentChange(self):
		self.currentFrame,self.existingBlocksList = self.addNewBlocksToScene(self.currentFrame,self.existingBlocksList,1,self.BlockWidth,self.BlockLength)
		self.existingBlocksList = self.movementOfBlocks(self.existingBlocksList,self.blockMovedX,self.blockMovedY)

	def step(self):
		self.DynamicEnvironMentChange()
		egoAction = self.EgoMotionPlanner()
		self.movementOfEgoBlock(egoAction)
		thisRewardValue,doneStatus = self.getRewardValue()
		thisState = self.GetSceneAsStateVector()
		return thisState,thisRewardValue,doneStatus

"""
if __name__ == "__main__":
	
	env = Environment()
	env.reset()
	for i in range(1000):
		env.render()
		observation, reward, done = env.step()
		if(done == -1):
			print("GameOver")
			print("Final Score obtained is "+str(env.EgoScoreValue))
			break
		elif(done == 1):
			print("You Won")
			print("Final Score obtained is "+str(env.EgoScoreValue))
			break
"""