import pygame as pg
import numpy as np
import random
import time

class Quad:
	def __init__(self, balls, width, height, x_offset, y_offset, path):
		self.balls = balls 
		self.path = path 
		self.quads = {}
		self.width = width
		self.height = height 
		self.x_offset = x_offset
		self.y_offset = y_offset
		self.groups = {} 

		self.resetQuadtree()
		self.generateQuadtree()
		return

	def resetQuadtree(self):
		self.groups = {} 
		self.quads = {}
		return

	def generateQuadtree(self):
		for section, boundary in SECTIONS.items():

			x_lower_bound = boundary[0]*self.width + self.x_offset
			y_lower_bound = boundary[1]*self.height + self.y_offset

			x_upper_bound = x_lower_bound+self.width
			y_upper_bound = y_lower_bound+self.height

			pg.draw.rect(WINDOW, GREEN, (x_lower_bound, y_lower_bound, self.width, self.height), 1)

			count = 0
			temp_balls = []
			for ball in self.balls:	
				if ball.x>x_lower_bound and ball.x<x_upper_bound and ball.y>y_lower_bound and ball.y<y_upper_bound:

					temp_balls.append(ball)
					count += 1

			if count>THRESHOLD:
				for ball in temp_balls:
					ball.tag = f"{self.path}_{section}"

				self.groups[section] = temp_balls
				self.quads[section] = Quad(temp_balls, self.width/2, self.height/2, x_lower_bound, y_lower_bound, f"{self.path}_{section}")
		return

	def searchBall(self, ball, depth):
		if not self.quads.keys() or len(ball.tag.split("_"))==depth:
			return

		try:
			#print(ball.tag, depth, self.quads.keys())
			self.quads[ball.tag.split("_")[depth]].searchBall(ball, depth+1)
		except Exception as e:
			#print(e)
			return

		if len(ball.tag.split("_"))-2==depth:
			for other_ball in self.groups[ball.tag.split("_")[depth]]:
				if other_ball.tag==ball.tag:
					continue

				pos_1 = np.array([ball.x, ball.y])
				pos_2 = np.array([other_ball.x, other_ball.y])

				dist = calc_dist(pos_1, pos_2)

				if dist<2*RADIUS:
					force = pos_1-pos_2
					norm = np.linalg.norm(force)
					force /= norm
					force *= FORCE_SCALER

					ball.update(force)
					other_ball.update(-force)
		return

class Ball:
	def __init__(self, x: float, y: float, color: set):
		self.x = x
		self.y = y 
		self.vx = np.random.choice([-1,1])*1.5
		self.vy = np.random.choice([-1,1])*1.5
		self.color = color 
		self.tag = None
		self.t0 = time.time()
		return

	def applyForce(self, force):
		self.vx = force[0]
		self.vy = force[1]
		return

	def fixEdgeCases(self):
		if self.x>WIDTH:
			self.x = 0	
		if self.x<0:
			self.x = WIDTH 

		if self.y>HEIGHT:
			self.y = 0	
		if self.y<0:
			self.y = HEIGHT 
		return	

	def update(self, force=[0., 0.]):

		if time.time()-self.t0>LIGHT_DURATION:
			self.color = BEIGE

		if force[0]>0. or force[0]<0. or force[1]>0. or force[1]<0.:
			self.applyForce(force)
			self.color = RED
			self.t0 = time.time()

		self.x += self.vx
		self.y += self.vy

		self.fixEdgeCases()
		return

	def render(self):
		pg.draw.circle(WINDOW, self.color, (self.x, self.y), RADIUS, 2)
		return

def generate_balls():
	return [Ball(np.random.random()*WIDTH, np.random.random()*HEIGHT, random.choice(COLORS)) for _ in range(nBall)]

def calc_dist(v1, v2):
	return np.sqrt(np.sum([(i-j)**2 for i, j in zip(v1, v2)]))

def main():

	balls = generate_balls()

	quad = Quad(balls, HALF_WIDTH, HALF_HEIGHT, 0, 0, "root")

	is_running = True
	while is_running:
		for event in pg.event.get():
			if event.type==pg.QUIT:
				is_running = False
				break

		WINDOW.fill(GREY)

		quad.resetQuadtree()
		quad.generateQuadtree()

		for ball in quad.balls:
			quad.searchBall(ball, 1)

			ball.update()
			ball.render()

		pg.display.update()

	pg.quit()
	return

if __name__=="__main__":
	WIDTH = 800
	HEIGHT = 800 

	HALF_WIDTH = int(WIDTH/2)
	HALF_HEIGHT = int(HEIGHT/2)

	WHITE = (255, 255, 255)
	RED = (255, 0, 0)
	BEIGE = (255, 240, 219)
	GREEN = (0, 255, 127)
	BLUE = (0, 191, 255)
	PURPLE = (238, 130, 238)
	BLACK = (0, 0, 0)
	GREY = (20, 20, 20)

	COLORS = [
		WHITE,
		RED,
		BEIGE,
		GREEN,
		BLUE,
		PURPLE
	]

	nBall = 200
	RADIUS = 10 
	THRESHOLD = 2 
	FORCE_SCALER = 5.0
	LIGHT_DURATION = 0.1

	SECTIONS = {
		"NW": [0, 0],
		"NE": [1, 0],
		"SW": [0, 1],
		"SE": [1, 1],
	}

	pg.init()
	WINDOW = pg.display.set_mode((WIDTH, HEIGHT))
	pg.display.set_caption("Quadtree object collision test")

	main()