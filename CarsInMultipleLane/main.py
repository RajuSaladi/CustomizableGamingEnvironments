from GraphicFunctions import GraphicFunctions


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
