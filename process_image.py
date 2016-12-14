#we're gonna take a 10 x 10 grid of squares
#obstacles are black squares
#objects defined by shape, size, color
#each square gets an x, y coordinate

#return list of occupied grids using computer vision
#find minimimum path between starting object and matching object using a star search


#openCV was created by Intel, maintained by willow garage, and is open source
#it does everything image related - segmentation, motion tracking, facial recogniton
import cv2
#scientific computing
import numpy as np
#for measuring time 
import time
#image processing in python 
#Compute the mean structural similarity index between two images.
from skimage.measure import compare_ssim as ssim #to compare 2 images
# it's the leading pathfinding algorithm
#used in games like Warcraft III. 
#searching among all possible paths to the solution (goal) for the one that incurs the smallest 
#cost (least distance travelled, shortest time, etc.), and among these paths it first considers 
#the ones that appear to lead most quickly to the solution. 
#we generate our possibilities and pick the one with the least projected cost. 
#Once a possibility is generated and its cost is calculated, 
#it stays in the list of possibilities until all the better nodes have been searched before it
import astarsearch
#helper class, will help us traverse the image from left to right for image prcoessing
import traversal


def main(image_filename):
	'''
	Returns:
	1 - List of tuples which is the coordinates for occupied grid. 
	2 - Dictionary with information of path. 
	'''

	occupied_grids = []		# List to store coordinates of occupied grid 
	planned_path = {}		# Dictionary to store information regarding path planning  	
	
	# load the image and define the window width and height
	image = cv2.imread(image_filename)
	(winW, winH) = (60, 60)		# Size of individual cropped images 

	obstacles = []			# List to store obstacles (black tiles)  
	index = [1,1] #starting point
	#create blank image, initialized as a matrix of 0s the width and height
	blank_image = np.zeros((60,60,3), np.uint8)
	#create an array of 100 blank images
	list_images = [[blank_image for i in xrange(10)] for i in xrange(10)] 	#array of list of images 
	#empty #matrix to represent the grids of individual cropped images
	maze = [[0 for i in xrange(10)] for i in xrange(10)] 			

	#traversal for each square
	for (x, y, window) in traversal.sliding_window(image, stepSize=60, windowSize=(winW, winH)):
		# if the window does not meet our desired window size, ignore it
		if window.shape[0] != winH or window.shape[1] != winW:
			continue

	#	print index, image is our iterator, it's where were at returns image matrix
		clone = image.copy()
		#format square for openCV
		cv2.rectangle(clone, (x, y), (x + winW, y + winH), (0, 255, 0), 2)
		crop_img = image[x:x + winW, y:y + winH] 				#crop the image
		list_images[index[0]-1][index[1]-1] = crop_img.copy()			#Add it to the array of images

		#we want to print occupied grids, need to check if white or not
		average_color_per_row = np.average(crop_img, axis=0)
		average_color = np.average(average_color_per_row, axis=0)
		average_color = np.uint8(average_color)					#Average color of the grids

		#iterate through color matrix,
		if (any(i <= 240 for i in average_color)):				#Check if grids are colored
			maze[index[1]-1][index[0]-1] = 1				#ie not majorly white
			occupied_grids.append(tuple(index))				#These grids are termed as occupied_grids 

		if (any(i <= 20 for i in average_color)):				#Check if grids are black in color
	#		print ("black obstacles")
			obstacles.append(tuple(index))					#add to obstacles list

		#show this iteration
		cv2.imshow("Window", clone)
		cv2.waitKey(1)
		time.sleep(0.025)
	
		#Iterate
		index[1] = index[1] + 1							
		if(index[1]>10):
			index[0] = index[0] + 1
			index[1] = 1


	#get object list
	list_colored_grids = [n for n in occupied_grids if n not in obstacles]	#Grids with objects (not black obstacles)


	#Compare each image in the list of objects with every other image in the same list
	#Most similar images return a ssim score of > 0.9
	#Find the min path from the startimage to this similar image u=by calling astar function

	for startimage in list_colored_grids:
		key_startimage = startimage
		#start image
		img1 = list_images[startimage[0]-1][startimage[1]-1]
		for grid in [n for n in list_colored_grids  if n != startimage]:
			#next image
			img = 	list_images[grid[0]-1][grid[1]-1]
			#convert to grayscale
			image = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
			image2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			#compare structural similarity
			s = ssim(image, image2)
			#if they are similar
			if s > 0.9:
				#perform a star search between both
				result = astarsearch.astar(maze,(startimage[0]-1,startimage[1]-1),(grid[0]-1,grid[1]-1))
	#			print result
				list2=[]
				for t in result:
					x,y = t[0],t[1]
					list2.append(tuple((x+1,y+1)))			#Contains min path + startimage + endimage
					result = list(list2[1:-1]) 			#Result contains the minimum path required 

				if not result:						#If no path is found;
					planned_path[startimage] = list(["NO PATH",[], 0])
				planned_path[startimage] = list([str(grid),result,len(result)+1])

	for obj in list_colored_grids:
		if not(planned_path.has_key(obj)):					#If no matched object is found;
			planned_path[obj] = list(["NO MATCH",[],0])			

	return occupied_grids, planned_path



if __name__ == '__main__':

    # change filename to check for other images
    image_filename = "test_images/test_image1.jpg"

    main(image_filename)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
