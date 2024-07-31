import pygame as pg
import numpy as np
import random
import math 
import time

class Ball:
	def __init__(self, x, y, radius, color):
		self.x = x
		self.y = y
		self.radius = radius 

		''' initialize normalized velocity '''
		self.vx = random.choice([-1,1])
		self.vy = random.choice([-1,1]) 
		self.vx, self.vy = calcUnitVector(self.vx, self.vy)

		self.color = color

		''' tag is used to search for specific Ball within quadtree '''
		self.tag = ""

		''' used for lighting duration upon collision with another ball '''
		self.t0 = time.time()
		return

	def isCollided(self, other_ball):
		x1, y1, x2, y2 = self.x, self.y, other_ball.x, other_ball.y
		dist = calcDist([x1, y1], [x2, y2])
		return dist<=self.radius+other_ball.radius

	def fixBoundaryCases(self):
		if self.x<0 or self.x>WIDTH:
			self.vx *= -1
		if self.y<0 or self.y>HEIGHT:
			self.vy *= -1
		return

	def update(self, other_ball=None):
		if not other_ball==None:
			if self.isCollided(other_ball):
				''' calculate normalized vector pointing the opposite direction from the collided ball '''
				self.vx = self.x-other_ball.x
				self.vy = self.y-other_ball.y

				try:
					self.vx, self.vy = calcUnitVector(self.vx, self.vy)
				except Exception as e:
					pass

				''' ball color changes upon collision '''
				self.color = RED
				self.t0 = time.time()

		if time.time()-self.t0>0.2:	
			''' ball color changes back to the original color '''
			self.color = WHITE

		''' update the position of the ball '''
		self.x += self.vx
		self.y += self.vy

		self.fixBoundaryCases()
		return

	def render(self):
		pg.draw.circle(WINDOW, self.color, (self.x, self.y), RADIUS, 1)
		return

class Box:
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w 
		self.h = h
		return

class Quad:
	def __init__(self, box, color, limit, depth):
		''' dimensions of a quad '''
		self.box = box

		''' color of the quad borders which is different from the ball color '''
		self.color = color

		''' maximum number of balls that can fit in this specific quad '''
		self.limit = limit 

		''' represents the number of recursions applied in generating the quadtree '''
		self.depth = depth 

		''' initialize quadtree data structure for every frame '''
		self.reset()
		return

	def reset(self):
		self.is_partitioned = False
		self.balls = []
		self.sub_quads = {
			"NW": None,
			"NE": None,
			"SW": None,
			"SE": None,
		}
		return



	def partition(self):
		x, y, w, h = self.box.x, self.box.y, self.box.w, self.box.h 
		self.sub_quads["NW"] = Quad( Box(x,     y,     w/2, h/2), self.color, self.limit, self.depth+1 )
		self.sub_quads["NE"] = Quad( Box(x+w/2, y,     w/2, h/2), self.color, self.limit, self.depth+1 )
		self.sub_quads["SW"] = Quad( Box(x,     y+h/2, w/2, h/2), self.color, self.limit, self.depth+1 )
		self.sub_quads["SE"] = Quad( Box(x+w/2, y+h/2, w/2, h/2), self.color, self.limit, self.depth+1 )
		self.is_partitioned = True
		return

	def insertBall(self, ball, quad_name=""):
		''' skip if the ball is not in this quad '''
		if not inBox(self.box, ball):
			return

		if self.is_partitioned:
			''' if the quad already has generated sub-quads, pass the ball to the sub-quads '''
			self.sub_quads["NW"].insertBall(ball, quad_name+"_NW")
			self.sub_quads["NE"].insertBall(ball, quad_name+"_NE")
			self.sub_quads["SW"].insertBall(ball, quad_name+"_SW")
			self.sub_quads["SE"].insertBall(ball, quad_name+"_SE")
		else:
			if len(self.balls)<self.limit:
				''' if the ball can still fit in this quad, store the ball and tag it accordingly '''
				self.balls.append(ball)
				ball.tag = quad_name
			else:
				''' if the ball cannot fit in this quad anymore, generate sub-quads '''
				self.partition()

				''' pass all the balls stored in this quad to the sub-quads '''
				self.balls.append(ball)
				for _ball in self.balls:
					self.sub_quads["NW"].insertBall(_ball, quad_name+"_NW")
					self.sub_quads["NE"].insertBall(_ball, quad_name+"_NE")
					self.sub_quads["SW"].insertBall(_ball, quad_name+"_SW")
					self.sub_quads["SE"].insertBall(_ball, quad_name+"_SE")

				''' delete all the balls stored in this quad to free up the memory '''
				self.balls.clear()
		return

	def processCollision(self, ball):
		''' 
		quads that do not have sub-quads are the ones having balls.
		check collision status against all the balls in the quad.
		update the physics of current ball accordingly
		'''
		if not self.is_partitioned:
			for other_ball in self.balls:
				if id(ball)==id(other_ball):
					continue	

				ball.update(other_ball)
			return

		''' quadtree fails to find a ball in some cases. buggy logic. '''
		try:
			tag = ball.tag.split("_")[self.depth+1]
		except Exception as e:
			return

		''' check collision recursively '''
		self.sub_quads[tag].processCollision(ball)
		return

	def render(self):
		''' render quadtree recursively '''
		if not self.is_partitioned:
			for ball in self.balls:
				ball.render()

			pg.draw.rect(WINDOW, GREEN, (self.box.x, self.box.y, self.box.w, self.box.h), 1)
			return

		self.sub_quads["NW"].render()
		self.sub_quads["NE"].render()
		self.sub_quads["SW"].render()
		self.sub_quads["SE"].render()
		return

def calcDist(v1, v2):
	return np.sqrt(np.sum([(i-j)**2 for i, j in zip(v1, v2)]))

def calcUnitVector(x, y):
	mag = math.sqrt(x**2+y**2)
	x /= mag
	y /= mag
	return (x, y)

def inBox(box, ball):
	x, y, w, h = box.x, box.y, box.w, box.h 
	return (ball.x>x   and
		    ball.x<x+w and
		    ball.y>y   and
		    ball.y<y+h)

def main():
	quad = Quad(Box(0,0,WIDTH,HEIGHT),GREEN,LIMIT,0)

	balls = [Ball(random.randint(0, WIDTH), random.randint(0, HEIGHT), RADIUS, WHITE) for _ in range(nBall)]

	is_running = True
	while is_running:
		for event in pg.event.get():
			if event.type==pg.QUIT:
				is_running = False
				break	

		WINDOW.fill(BLACK)	

		''' insert each ball in the quadtree '''
		[quad.insertBall(ball, "root") for ball in balls]

		''' handle collision and ball position updates '''
		[quad.processCollision(ball) for ball in balls]
		
		quad.render()

		''' reset quadtree data structure for next frame '''
		quad.reset()

		pg.display.flip()

	pg.quit()
	return

if __name__ == '__main__':
	WIDTH  = 800
	HEIGHT = 800

	WHITE = (255,255,255)
	RED   = (255,0,0)
	GREEN = (0,255,0)
	GREY  = (20,20,20)
	BLACK = (0,0,0)

	''' number of balls to generate '''
	nBall = 500

	''' maximum number of balls that can fit in a given quad '''
	LIMIT = 5

	''' ball radius '''
	RADIUS = 7

	pg.init()
	WINDOW = pg.display.set_mode((WIDTH, HEIGHT))	
	pg.display.set_caption("Quadtree Collision Detection")

	main()

