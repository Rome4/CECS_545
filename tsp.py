#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Module for TSP utilities.
Author: Roman Millem
Date: 14 October 2020
"""

from collections import namedtuple
import math
import time
from typing import Tuple

City = namedtuple("City", "name x y")
Edge = namedtuple("Edge", "city1 city2 distance")

# Cache will store city distances (D) and edge distances (E)
CACHE: dict = {"D": {}, "E": {}}

class TspHandler:
	
	file: str = ""
	data: dict = {}
	
	# Initialize the class by setting and reading the TSP file
	def __init__(self, file: str) -> None:
		self.set_file(file)
		self.data = self.read_tsp_file()
	
	# Get data from this instance
	def get_data(self) -> dict:
		return self.data
	
	# Get the file from this instance
	def get_file(self) -> str:
		return self.file
	
	# Set the file instance
	def set_file(self, file: str) -> None:
		self.file = file
	
	# Parse a TSP-formatted file (comparable to the previous experiment)
	def read_tsp_file(self) -> dict:
		"""Parse a TSP-formatted file and return a dictionary of available fields."""
		
		if self.file == "":
			raise NameError("file parameter not passed")
		
		result: dict = {"NODE_COORD_SECTION": []}
		
		try:
			
			# Loop through line by line
			for line in open(self.file, 'r'):
				
				# Separate data
				line = line.rstrip('\n')
				keyvalues: list = line.split(':')
				coords: list = line.split(' ')
				line.split(' ')
				
				if len(keyvalues) > 1:
					# Add a key/value pair directly
					result[keyvalues[0]] = ((result[keyvalues[0]] + '\n' + keyvalues[1]) if keyvalues[0] in result else keyvalues[1]).lstrip()
					continue
				elif len(coords) == 3:
					# Or add a coordinate to the coord section
					result["NODE_COORD_SECTION"].append(City(coords[0], float(coords[1]), float(coords[2])))
			
			# Strong-type any applicable data fields
			result["DIMENSION"] = int(result["DIMENSION"])
			
		except OSError as e:
			raise OSError("could not open TSP file for reading: " + e)
		
		except IndexError as e:
			raise IndexError("malformed TSP file: " + e)
		
		if len(result["NODE_COORD_SECTION"]) != result["DIMENSION"]:
			raise OSError("dimension does not match supplied coordinates")
		
		# Return all sections
		return result

def get_distance(c1: City, c2: City) -> float:
	"""Calculate the distance between two points in 2D Euclidean space."""
	global CACHE
	
	if c1 == c2:
		return 0.0
	
	# The unweighted naming convention for the cache will be <lower>-<upper>
	name: str = ""
	if int(c1.name) < int(c2.name):
		name = c1.name + "-" + c2.name
	else:
		name = c2.name + "-" + c1.name
	
	# Check if the edge is already cached
	if name not in CACHE["D"]:
	
		# Add uncalculated value to cache
		CACHE["D"][name] = Edge(c1.name, c2.name, math.hypot(c1.x - c2.x, c1.y - c2.y))
	
	# Return the calculated cache value
	return CACHE["D"][name].distance

def find_closest_city(city: City, cities: list) -> Edge:
	"""Return the city nearest to the given city from a list of cities"""
	global CACHE
	
	# Loop through all cities in a list and return the edge of two cities with the smallest distance
	result: Edge = None
	for c in cities:
		
		# Pass if the comparison is itself
		if c == city:
			continue
		
		# Store the running minimum
		d: float = get_distance(city, c)
		if result is None or d < result.distance:
			result = Edge(city, c, d)
	
	# Return the grand minimum if there is one, otherwise return the original city
	return city if result is None else result

def fitness_function(cities: list) -> float:

	return 0