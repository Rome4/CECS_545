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

def mutate_swap(pop: list) -> list:
	mutated: list = []
	p_size: int = len(pop)
	index_mut = random.randrange(0, p_size-1, 1)
	mutated = pop[index_mut]

	# Choose random indexes to swap in radomly chosen mutated chromosome
	m_size = len(mutated)
	index1: int = random.randrange(1, m_size-1, 1)
	index2: int = index1
	while index2 == index1:
		index2 = random.randrange(1, m_size-1, 1)
	mutated[index1], mutated[index2] = mutated[index2], mutated[index1]

	return mutated

# Front of path manipulation focused mutation
def mutate_front(pop: list) -> list:
	mutated: list = []
	p_end: int = len(pop)-1
	index_mut = random.randrange(0, p_end, 1)
	mutated = pop[index_mut]
	
	m_end: int = len(mutated)-1
	pick:int = random.randrange(int(m_end/2), m_end, 1)

	return mutated

# Modified version of cycle crossover
# credit -> https://www.hindawi.com/journals/cin/2017/7430125/#conclusion
def cycle_cross(parent1: list, parent2: list) -> list:
	off1: list = [None for _ in range(len(parent1))]
	off2: list = [None for _ in range(len(parent2))]
	offspring: list = []

	flag: int = 0
	off1[0] = parent2[0]

	for x in range(len(parent1)):

		if flag == 0:
			for a, city_a in enumerate(parent1):
				if city_a == off1[x]:
					for b, city_b in enumerate(parent1):
						if parent2[a] == city_b:
							off2[x] = parent2[b]
							break
					break
							
			if flag == 0:
				for c, city in enumerate(parent1):
					if city == off2[x]:
						if c == 0:
							flag = 1
							break
						else:
							off1[x+1] = parent2[c]  
							
		else:
			for d, city_d in enumerate(parent2):
				if not city_d in off1:
					off1[x] = city_d
			for e, city_e in enumerate(parent1):
				if not city_e in off2:
					off2[x] = city_e
	
	offspring.append(off1)
	offspring.append(off2)
	return offspring

def subset_cross(parent1: list, parent2: list) -> list:
	p1_size = len(parent1)
	subset: int = int(p1_size / 5)
	random_subset: int = random.randrange(2,subset,1)
	random_start_index = random.randrange(0,p1_size-random_subset,1)
	p1_subset: list = parent1[random_start_index:random_start_index+random_subset]
	p2_subset: list = parent2[random_start_index:random_start_index+random_subset]
	off1: list = []
	off2: list = []

	for x in parent2:
		if x not in p1_subset:
			off1.append(x)
	for x in range(random_subset-1,-1,-1):
		off1.insert(random_start_index,p1_subset[x])

	for x in parent1:
		if x not in p2_subset:
			off2.append(x)
	for x in range(random_subset-1,-1,-1):
		off2.insert(random_start_index,p2_subset[x])

	offspring: list = []
	offspring.append(off1)
	offspring.append(off2)

	return offspring

def crossover(pop: list) -> list:

	# Correcting all mismatched lengths
	for p in pop:
		if p[0] == p[len(p)-1]:
			p.pop(len(p)-1)

	# Tournament Selection
	subset: int = int(len(pop[1]) / 5)
	tournament: list = []
	high: float = 999999.99
	parent1: list = []
	
	while not parent1:
		random_start_index: int = random.randrange(0,len(pop[1])-subset-1,1)
		tournament = pop[random_start_index:random_start_index+subset]
		for t in tournament:
			if fitness_function(t) < high:
				high = fitness_function(t)
				parent1 = t

	high: float = 999999.99
	tournament = []
	parent2: list = parent1
	random_start_index = random.randrange(0,len(pop[1])-subset-1,1)
	tournament = pop[random_start_index:random_start_index+subset]
	for t in tournament:
		if fitness_function(t) < high and t != parent1:
			high = fitness_function(t)
			parent2 = t

	# Crossover

	# Implement multiple crossover methods
	random_cross: int = random.randint(1,5)

	if random_cross < 4:
		offspring: list = subset_cross(parent1,parent2)
	else:
		offspring: list = cycle_cross(parent1,parent2)
	
	return offspring

def next_gen(pop: list) -> list:
	#print(len(pop))
	population_size: int = 25
	generation: list = []
	chromosome: list = []
	mut: list = []

	for i in range(0,population_size,1):
		rand = random.randrange(1,100,1)
		if rand > 10:
			chromosome = crossover(pop)
			for c in chromosome:
				generation.append(c)
		else:
			mut = mutate_swap(pop)
			generation.append(mut)
			mut = mutate_swap(pop)
			generation.append(mut)

	return generation

def find_best_path(pop: list) -> list:
	best_fit: float = 99999.9
	best_path: list = []

	for i in pop:
		path_distance: float = fitness_function(i)
		if  path_distance < best_fit:
			best_fit = fitness_function(i)
			best_path = i

	return best_path