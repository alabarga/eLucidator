# ImageStream.py
# Base Class for LucidTronix ImageStream objects
# Samwell Freeman
# June 2016

import os
import sys
import cv2
import pygame
import threading
import numpy as np
from PIL import Image
import urllib, cStringIO

class ImageStream(object):
	def __init__(self, source='dir', format='pygame', cache_path='./'):
		super(ImageStream, self)
		self.source = source
		self.format = format
		self.cache_path = cache_path
		self.recording = False
		self.images = []
		self.cur_image = 0

	def __str__(self):
		return "Image Stream from:" +  self.source


	def prev(self, crop=None):
		if len(self.images) > 0:
			self.cur_image = (self.cur_image-1) % self.size()
			return  self.images[self.cur_image].to_surface()
		elif self.format == 'pygame':
			print 'returning dog as pygame'
			return pygame.image.load('./images/dog.jpg')
		else:
			print 'next failed returning None.', self.format
			return None

	def next(self, crop=None):
		if len(self.images) > 0:
			image = self.images[self.cur_image]
			self.cur_image = (self.cur_image+1) % self.size()
			return image
		elif self.format == 'pygame':
			print 'returning dog as pygame'
			return pygame.image.load('./images/dog.jpg')
		else:
			print 'next failed returning None.', self.format
			return None

	def size(self):
		return len(self.images)



class InternetImage:
	def __init__(self, img_path, keyword_path, url=False):
		self.pil_shape = (400, 300)
		self.img_path = img_path
		self.keyword_path = keyword_path
		self.url = url
		self.loaded = False
		self.img = None

	def load_image_file(self):
		self.img = Image.open(self.img_path).convert('RGB')
		self.img = self.img.resize(self.pil_shape, Image.ANTIALIAS)
		self.loaded = True

	def load_image_url(self):
		try:
			ifile = cStringIO.StringIO(urllib.urlopen(self.img_path).read())
			print 'Try to open image at:', self.img_path

			self.img = Image.open(ifile).convert('RGB')
			self.img = self.img.resize(self.pil_shape, Image.ANTIALIAS)
	
			self.img_path = self.keyword_path + os.path.basename(self.img_path)
			print 'Try to save image at:', self.img_path
			if not os.path.exists(self.img_path):
				self.img.save(self.img_path)
			print 'Saved image at:', self.img_path
	
			self.loaded = True	

		except Exception, e:
			print 'Error reading:', self.img_path
			print 'Error message:', e.message

	def load(self):
		if self.url:
			self.load_image_url()
		else:
			self.load_image_file()

	def to_surface(self):
		mode = self.img.mode
		size = self.img.size
		data = self.img.tostring()
		surface = pygame.image.fromstring(data, size, mode)
		return surface