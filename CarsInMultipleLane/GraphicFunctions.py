import numpy as np
import cv2
import pdb

class GraphicFunctions:
	
	def initializeFrame(self,imageShape = (300,300,3),noOfLanes = 3):
		self.DISPLAYNAME = "CarTrafficGame"
		inputImage = np.zeros(imageShape)
		inputImage = self.drawLanes(inputImage,noOfLanes)
		#self.ViewScreen(inputImage)
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
		cv2.imshow(self.DISPLAYNAME,inputImage)
		#cv2.waitKey(0)
		k = cv2.waitKey(1) & 0xff
	
	def drawLanes(self,inputImage,noOfLanes):
		linesPosition = []
		for i in range(0,noOfLanes+1):
			xPos = int(i*inputImage.shape[1]/noOfLanes)
			cv2.line(inputImage, (xPos, 0), (xPos, inputImage.shape[0]), (255,255,255), 2)
		return inputImage

	def NewTrafficAddition(self,inputImage,trafficVehiclePosList,noOfLanes,carWidth,carLength,TRAFFICTHRESHOLD = 0.95):
		#noOfCarsToAdd = np.random.choice(noOfLanes - 1)
		lanesForCarsToFillList = np.random.sample(noOfLanes) > max(TRAFFICTHRESHOLD,0.3)
		laneWidth = int(inputImage.shape[1]/noOfLanes)
		#print(lanesForCarsToFillList)
		for i in range(len(lanesForCarsToFillList)):
			eachLaneForTraffic = lanesForCarsToFillList[i]
			if(eachLaneForTraffic == True):
				#pdb.set_trace()
				carPosX = i*laneWidth + np.random.choice(laneWidth-carWidth)
				if(self.CarPlacementCheck(trafficVehiclePosList,carPosX,0,carWidth,carLength) == True):
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
	
	def CarPlacementCheck(self,trafficVehiclePosList,carPosX,carPosY,carWidth,carLength,GAPBETWEENVEHICLES = 2):
		CheckFlag = False
		currentBox = [carPosX-GAPBETWEENVEHICLES,carPosY-GAPBETWEENVEHICLES,carWidth+2*GAPBETWEENVEHICLES,carLength+2*GAPBETWEENVEHICLES,"__"]
		if(len(trafficVehiclePosList) == 0):
			return True
		trafficVehiclePosList = np.array(trafficVehiclePosList)
		iouTotal = self.VectorizedIou(currentBox,trafficVehiclePosList)
		#pdb.set_trace()
		if(iouTotal.sum() == 0):
			CheckFlag = True
		return CheckFlag

	def placeEgoVehicle(self,inputImage,EgoCarPosX,EgoCarPosY,EgoCarWidth,EgoCarLength):
		inputImage = self.CreateCar(inputImage,EgoCarPosX,EgoCarPosY,EgoCarWidth,EgoCarLength,"EgoVehicle")
		return inputImage

	def MovementOfEgoVehicle(self,EgoMotion,EgoCarPosX,EgoCarPosY,EgoCarWidth,EgoCarLength,	EgoMovedX,EgoMovedY):
		if(EgoMotion == "Left"):
			EgoCarPosX = EgoCarPosX - EgoMovedX
		elif(EgoMotion == "Right"):
			EgoCarPosX = EgoCarPosX + EgoMovedX
		elif(EgoMotion == "Up"):
			EgoCarPosY = EgoCarPosY - EgoMovedY
		elif(EgoMotion == "Down"):
			EgoCarPosY = EgoCarPosY + EgoMovedY
		return EgoCarPosX,EgoCarPosY

	def EgoMotionPlanner(self,EgoMotionList,EgoCarPosX,EgoCarPosY,EgoCarWidth,EgoCarLength,EgoMovedX,EgoMovedY,trafficVehiclePosList):
		return np.random.choice(EgoMotionList)

"""
if __name__ == "__main__":

	GrF = GraphicFunctions()

	frameSize = (300,300,3)
	noOfLanes = 3
	trafficCarWidth = 15
	trafficCarLength = 30
	trafficMovedX = 0
	trafficMovedY = 2
	EgoCarPosX = int(frameSize[1]/2)
	EgoCarPosY = int(frameSize[0]-20)
	EgoCarWidth = 15
	EgoCarLength = 30
	EgoMovedX = 2
	EgoMovedY = 0
	EgoMotionList = ["Left","Right","Up","Down"]
	trafficVehiclePosList = []

	for i in range(0,1000):
		currentFrame = GrF.initializeFrame(frameSize,noOfLanes)
		currentFrame,trafficVehiclePosList = GrF.NewTrafficAddition(currentFrame,trafficVehiclePosList,noOfLanes,trafficCarWidth,trafficCarLength)
		currentFrame = GrF.getTheTrafficVisualization(currentFrame,trafficVehiclePosList,trafficCarWidth,trafficCarLength)
		trafficVehiclePosList = GrF.movementOfTraffic(trafficVehiclePosList,frameSize,trafficMovedX,trafficMovedY)
		currentFrame = GrF.placeEgoVehicle(currentFrame,EgoCarPosX,EgoCarPosY,EgoCarWidth,EgoCarLength)
		EgoMotion = GrF.EgoMotionPlanner(EgoMotionList,EgoCarPosX,EgoCarPosY,EgoCarWidth,EgoCarLength,EgoMovedX,EgoMovedY,trafficVehiclePosList)
		EgoCarPosX,EgoCarPosY = GrF.MovementOfEgoVehicle(EgoMotion,EgoCarPosX,EgoCarPosY,EgoCarWidth,EgoCarLength,EgoMovedX,EgoMovedY)
		GrF.ViewScreen(currentFrame)
"""