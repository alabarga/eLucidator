# LucidApp.py
# Base Class for LucidTronix eLucidator Applications
# Samwell Freeman
# June 2016

import os
import sys
import cv2
import pygame
import threading
import numpy as np
from pygame import *
import pygame.ftfont
from PIL import Image
from time import time
import urllib, cStringIO

class LucidApp(object):
	def __init__(self, name, cache_path='./cache/', fullscreen=False, resolution=(400, 300), 
				icon_path='./icons/default_icon.png', base_graphics='cv2'):
		super(LucidApp, self)
		self.name = name 
		self.cache_path = cache_path
		self.recording = False
		self.fullscreen = fullscreen
		self.resolution = resolution
		self.resolution_cv = (resolution[1], resolution[0], 3)
		self.playing = True
		self.base_graphics = base_graphics
		self.icon_size = (25, 25)
		self.icon = self.get_icon(icon_path)
		self.buttons = []
		self.input_string = ''
		print 'lucid app constructor', base_graphics, resolution

		if self.base_graphics == 'pygame':
			self.pygame_init()
			self.buttons.append(Button(self, 'exit', (10,10,75,30), (25,250,250), exit_pygame))
		elif self.base_graphics == 'cv2':
			self.cv2_init()
			self.buttons.append(Button(self, 'exit', (10,10,75,40), (50,50,50), exit_cv2))

	def __str__(self):
		return "LucidApp:" +  self.name

	def open(self):
		pass

	def close(self):
		pass

	def draw(self):
		if self.base_graphics == 'cv2':
			cv2.imshow('canvas', self.canvas)
		elif self.base_graphics == 'pygame':
			pygame.display.update()
		else:
			print 'graphics not implemented.'
		

	def cv2_init(self):
		if self.fullscreen:
			self.canvas = np.zeros(self.resolution_cv, np.uint8)
			cv2.namedWindow("canvas", cv2.WINDOW_NORMAL)          
			cv2.setWindowProperty("canvas", cv2.WND_PROP_FULLSCREEN, 1)
		else:
			self.canvas = np.zeros(self.resolution_cv, np.uint8)
			cv2.namedWindow("canvas")		
		self.fill()
		print 'cv2 init canvas', self.canvas.shape

	def pygame_init(self):
		pygame.display.init()
		pygame.ftfont.init()
		self.py_font = pygame.ftfont.Font(None, 24)

		if self.fullscreen:
			self.resolution = pygame.display.list_modes()[0]
			self.surface = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
		else:
			self.surface = pygame.display.set_mode(self.resolution)
		print 'pygame init surface'

	def get_icon(self, icon_path):
		if self.base_graphics == 'pygame':
			return pygame.image.load(icon_path)
		elif self.base_graphics == 'cv2':
			icon = cv2.imread(icon_path)
			if icon is None:
				print 'Could not load icon from path:', icon_path
				return
			return cv2.resize(icon, self.icon_size, interpolation=cv2.INTER_AREA)


	def label(self, text, x, y, size=1, color=(255,255,255), font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1.0, thickness=1):
		if self.base_graphics == 'pygame':
			my_label = self.py_font.render(text, size, color)
			self.surface.blit(my_label, (x, y))
		elif self.base_graphics == 'cv2':
			cv2.putText(self.canvas, text, (x, y), font, font_scale, color, thickness)			

	def fill(self, color=(0,0,0)):
		if self.base_graphics == 'pygame':
			self.surface.fill(color)
		elif self.base_graphics == 'cv2':
			self.canvas = np.zeros(self.resolution_cv, np.uint8)
			#self.canvas[0].fill(color[0])
			#self.canvas[1].fill(color[1])
			#self.canvas[2].fill(color[2])

	def show_image(self, image, left_corner=(0,0)):
		if self.base_graphics == 'pygame':
			self.surface.blit(image.to_surface(), left_corner)
		elif self.base_graphics == 'cv2':
			dim = image.to_array().shape
			if -1*left_corner[0] < dim[1]: 
				ix = 0
				iw = dim[1]
				if left_corner[0] < 0:
					ix = -left_corner[0]
				if 	ix+left_corner[0]+dim[1] > self.canvas.shape[1]:
					iw = self.canvas.shape[1] - (left_corner[0]+ix)

				assert ix >= 0 and iw <= dim[1]

				sx = max(0,left_corner[0])
				sy = max(0,left_corner[1])
				iwx = min(self.canvas.shape[1], left_corner[0] + dim[1])
				ihy = min(self.canvas.shape[0], left_corner[1] + dim[0])
				#print 'img shapes:', ix, iw, sx, sy, iwx, ihy, dim, self.canvas.shape, left_corner
				self.canvas[sy:ihy, sx:iwx] = image.to_array()[:,ix:iw]

	def show_image_cv(self, image_cv, left_corner):
		dim = image_cv.shape
		if -1*left_corner[0] < dim[1]: 
			ix = 0
			iw = dim[1]
			if left_corner[0] < 0:
				ix = -left_corner[0]
			if 	ix+left_corner[0]+dim[1] > self.canvas.shape[1]:
				iw = self.canvas.shape[1] - (left_corner[0]+ix)

			assert ix >= 0 and iw <= dim[1]

			sx = max(0,left_corner[0])
			sy = max(0,left_corner[1])
			iwx = min(self.canvas.shape[1], left_corner[0] + dim[1])
			ihy = min(self.canvas.shape[0], left_corner[1] + dim[0])
			#print 'img shapes:', ix, iw, sx, sy, iwx, ihy, dim, self.canvas.shape, left_corner
			self.canvas[sy:ihy, sx:iwx] = image_cv[:,ix:iw]		

	def show_image_cv2(self, image_cv, cx_idx, cy_idx, ix_idx=None, iy_idx=None):
		if ix_idx and iy_idx:
			self.canvas[cy_idx[0]:cy_idx[1], cx_idx[0]:cx_idx[1]] = image_cv[iy_idx[0]:iy_idx[1],ix_idx[0]:ix_idx[1]]
		else:
			self.canvas[cy_idx[0]:cy_idx[1], cx_idx[0]:cx_idx[1]] = image_cv

	def handle_keys(self):
		if self.base_graphics == 'pygame':
			for event in pygame.event.get():
				if (event.type == pygame.QUIT):
					pygame.quit()
					return -1
				elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					pygame.quit()
					return -1
		elif self.base_graphics == 'cv2':
			char = cv2.waitKey(1) & 0xFF
			if char > 31 and char < 127:
				self.input_string += str(chr(char))

			elif char == 27: # Escape
				return 0
			elif char == 8: # Delete
				if len(self.input_string):
					self.input_string = self.input_string[:-1]
			elif char == 10: # Enter/return key
				print 'Enter/return key'
			elif char == 9: # Tab
				print 'tab'
			elif char == 226: # Right shift
				print 'right shift'

			elif char == 227: # Left Ctrl
				print 'left ctrl'
			elif char == 228: # Right Ctrl
				print 'right ctrl'
			elif char != 255:
				print 'special char:', char
			return char




class Button:
	def __init__(self, app, name, rect, color, callback, icon=None):
		self.app = app
		self.name = name
		self.rect = rect
		self.color = color
		self.highlight = (40,205,150)
		self.cur_color = self.color
		self.callback = callback
		self.icon = icon
		self.last_press = 0

	def show(self):
		if self.app.base_graphics == 'pygame':
			pygame.draw.rect(self.app.surface, self.cur_color, self.rect, 0)
			self.app.label(self.name, self.rect[0]+6, self.rect[1]+(self.rect[3]/2) - 10)
		elif self.app.base_graphics == 'cv2':
			pt2 = (self.rect[0] + self.rect[2], self.rect[1] + self.rect[3])
			cv2.rectangle(self.app.canvas, (self.rect[0], self.rect[1]), pt2, self.cur_color, -1)
			self.app.label(self.name, self.rect[0]+4, self.rect[1]+(self.rect[3] - 10) )


	def over(self, x, y):
		is_over = self.rect[0] < x < self.rect[0]+self.rect[2] and self.rect[1] < y < self.rect[1]+self.rect[3]
		if is_over:
			self.cur_color = self.highlight
		else:
			self.cur_color = self.color
		return is_over

	def press(self):
		self.last_press = time()
		return self.callback()

def exit_pygame():
	pygame.quit()
	return -1

def exit_cv2():
	cv2.destroyAllWindows()
	return -1

def AAfilledRoundedRect(surface,rect,color,radius=0.4):

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = Rect(rect)
    color        = Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = Surface(rect.size,SRCALPHA)

    circle       = Surface([min(rect.size)*3]*2,SRCALPHA)
    draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)
