import pygame as pg
import numpy as np
import random
import time

class Ball:
	def __init__(self, x, y, radius, color):
		self.x = x
		self.y = y
		self.radius = radius 
		self.vx = random.choice([-1,1])*0.1
		self.vy = random.choice([-1,1])*0.1 
		self.color = color
		self.tag = ""
		self.t0 = time.time()
		return

	def is_collided(self, other_ball):
		x1, y1, x2, y2 = self.x, self.y, other_ball.x, other_ball.y
		dist = calcDist([x1, y1], [x2, y2])
		return dist<=self.radius+other_ball.radius

	def update(self, other_ball=None):
		if not other_ball==None:
			if self.is_collided(other_ball):
				self.vx = (self.x-other_ball.x)*0.01
				self.vy = (self.y-other_ball.y)*0.01
				self.color = RED
				self.t0 = time.time()

		if time.time()-self.t0>0.2:	
			self.color = WHITE

		self.x += self.vx
		self.y += self.vy

		if self.x<0 or self.x>WIDTH:
			self.vx *= -1
		if self.y<0 or self.y>HEIGHT:
			self.vy *= -1
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
		self.box = box

		self.color = color
		self.limit = limit 
		self.depth = depth 
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

	def inBox(self, ball):
		x, y, w, h = self.box.x, self.box.y, self.box.w, self.box.h 
		return (ball.x>x   and
			    ball.x<x+w and
			    ball.y>y   and
			    ball.y<y+h)

	def partition(self):
		x, y, w, h = self.box.x, self.box.y, self.box.w, self.box.h 
		self.sub_quads["NW"] = Quad( Box(x,     y,     w/2, h/2), self.color, self.limit, self.depth+1 )
		self.sub_quads["NE"] = Quad( Box(x+w/2, y,     w/2, h/2), self.color, self.limit, self.depth+1 )
		self.sub_quads["SW"] = Quad( Box(x,     y+h/2, w/2, h/2), self.color, self.limit, self.depth+1 )
		self.sub_quads["SE"] = Quad( Box(x+w/2, y+h/2, w/2, h/2), self.color, self.limit, self.depth+1 )
		self.is_partitioned = True
		return

	def insertBall(self, ball, quad_name=""):
		if not self.inBox(ball):
			return

		if self.is_partitioned:
			self.sub_quads["NW"].insertBall(ball, quad_name+"_NW")
			self.sub_quads["NE"].insertBall(ball, quad_name+"_NE")
			self.sub_quads["SW"].insertBall(ball, quad_name+"_SW")
			self.sub_quads["SE"].insertBall(ball, quad_name+"_SE")
		else:
			if len(self.balls)<self.limit:
				self.balls.append(ball)
				ball.tag = quad_name
			else:
				self.partition()

				self.balls.append(ball)
				for _ball in self.balls:
					self.sub_quads["NW"].insertBall(_ball, quad_name+"_NW")
					self.sub_quads["NE"].insertBall(_ball, quad_name+"_NE")
					self.sub_quads["SW"].insertBall(_ball, quad_name+"_SW")
					self.sub_quads["SE"].insertBall(_ball, quad_name+"_SE")
				self.balls.clear()
		return

	def processCollision(self, ball):
		if not self.is_partitioned:
			for other_ball in self.balls:
				if id(ball)==id(other_ball):
					continue	

				ball.update(other_ball)
			return

		#print(ball.tag, self.depth+1)
		try:
			tag = ball.tag.split("_")[self.depth+1]
		except:
			return

		self.sub_quads[tag].processCollision(ball)
		return

	def update(self):
		if not self.is_partitioned:
			for ball in self.balls:
				ball.update()
			return

		self.sub_quads["NW"].update()
		self.sub_quads["NE"].update()
		self.sub_quads["SW"].update()
		self.sub_quads["SE"].update()
		return

	def render(self):
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

		[quad.insertBall(ball, "root") for ball in balls]
		[quad.processCollision(ball) for ball in balls]
		
		quad.render()
		quad.reset()

		pg.display.flip()

	pg.quit()
	return

if __name__ == '__main__':
	WIDTH = 800
	HEIGHT = 800

	WHITE = (255,255,255)
	RED = (255,0,0)
	GREEN = (0,255,0)
	BLACK = (0,0,0)

	nBall = 100
	LIMIT = 5
	RADIUS = 20

	pg.init()
	WINDOW = pg.display.set_mode((WIDTH, HEIGHT))	
	pg.display.set_caption("Quadtree")
	main()

