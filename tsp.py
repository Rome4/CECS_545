#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Module for TSP utilities.
Author: Roman Millem
Date: 14 October 2020
"""

from collections import namedtuple
import math
import time
import random
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

def print_path(path: list) -> None:
	for i in range(len(path)):
		print(path[i].name, end=", ")

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

def fitness_function(cities: list) -> float:
	"""Calculate fitness score for population"""

	# Paramter weight coefficients
	total_distance: float = 0.0

	for i in range(len(cities)):
		
		distance: float = get_distance(cities[i-1],cities[i])
		total_distance += distance

	return total_distance

def mutate_chromosome(cities: list) -> list:
	mutated = cities
	mutated.pop(len(mutated)-1)

	for i in range(0,5,1):
		mutated.append(mutated[0])
		mutated.pop(0)

	mutated.append(mutated[0])

	return mutated

def crossover(pop: list) -> list:
	fitness: list = []
	weight: list = []
	offspring: list = []
	total_fit: float = 0.0

	for p in pop:
		d: float = float(str(round(fitness_function(p),3)))
		fitness.append(d)
		total_fit += d

	# Create weighted fitness score based on cost difference from the mean
	# The higher the score the better, negative scores are bad
	mean: float = total_fit / len(pop)
	for i in range(len(fitness)):
		w: float = float(str(round((mean - fitness[i]),4)))
		weight.append(w)

	print("Fitness", end=" ")
	print(len(fitness), end=": ")
	print(*fitness, sep=", ")
	print("Weight", end=" ")
	print(len(weight), end=": ")
	print(*weight, sep=", ")

	# Select random parent based on fitness weight
	# Sum all positive weights, generate random number between 1 and sum of pos. weights, pick the highest weight that is < random number
	total_pos_weight: int = 0
	max_weight: float = 0.0
	parent1: list 
	parent2: list
	p1_index: int 
	p2_index: int
	for i in weight:
		if i > 0:
			total_pos_weight += int(i)
	random_weight: int = random.randrange(1,total_pos_weight,1)
	for i in range(len(weight)):
		if weight[i] > 0 and weight[i] < random_weight and weight[i] > max_weight:
			max_weight = weight[i]
			p1_index = i
	parent1 = pop[p1_index]

	max_weight = 0.0
	random_weight: int = random.randrange(1,total_pos_weight,1)
	for i in range(len(weight)):
		if i == p1_index:
			continue
		if weight[i] > 0 and weight[i] < random_weight and weight[i] > max_weight:
			max_weight = weight[i]
			p2_index = i
	parent2 = pop[p2_index]

	print("")
	print("Parent1", end=" ")
	print(len(parent1), end=" ")
	print(float(str(round(fitness_function(parent1), 4))), end=": ")
	print_path(parent1)
	print("")
	print("Parent2", end=" ")
	print(len(parent2), end=" ")
	print(float(str(round(fitness_function(parent2), 4))), end=": ")
	print_path(parent2)

	# Get random subset of parent1, max 25% of total chromosome length
	random_subset: int = random.randrange(2,15,1)
	random_start_index: int = random.randrange(0,len(parent1) - random_subset - 1,1)
	for i in range(1,random_subset,1):
		offspring.append(parent1[random_start_index + i])

	for i in parent2:
		if not i in offspring:
			offspring.append(i)
	offspring.append(offspring[0])

	print("")
	print("Offspring", end=" ")
	print(len(offspring), end=" ")
	print(float(str(round(fitness_function(offspring), 4))), end=": ")
	print_path(offspring)

	print("")
	print(random_subset)
	print(random_start_index)
	
	return offspring
