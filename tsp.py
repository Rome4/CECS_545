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

def selection(pop: list) -> list:
	parents: list = []
	weight: list = []
	total_fit: float = 0.0
	random_float: float = 0.0
	p1_index: int = 5
	p2_index: int = 10

	# Calculate total distance accross population
	for p in pop:
		fit_cal: float = fitness_function(p)
		total_fit += fit_cal

	# Calculate individual chromosome distance weight
	weight.append(0.0)
	for p in pop:
		fit_calc = fitness_function(p)/total_fit
		weight.append(fit_calc)
	for i in range(1,len(weight),1):
		weight[i] = weight[i] + weight[i-1]

	# Generate random weight and determin parents
	random_float = random.randrange(1,1000,1)
	random_float /= 1000.0
	for i in range(0,len(weight)-1,1):
		if random_float >= weight[i] and random_float < weight[i+1]:
			p1_index: int = i

	random_float = random.randrange(1,1000,1)
	random_float /= 1000.0
	for i in range(0,len(weight)-1,1):
		if random_float >= weight[i] and random_float < weight[i+1]:
			if i != p1_index:
				p2_index: int = i
			elif i == len(weight) - 1:
				p2_index = len(weight) - 2
			elif i == 0:
				p2_index = 1
				
	parents.append(p1_index)
	parents.append(p2_index)

	return parents

def mutate(pop: list) -> list:
	mutated: list = []
	p_size: int = len(pop[1])
	index_mut = random.randrange(0, p_size, 1)
	mutated = pop[index_mut]
	
	# Choose random indexes to swap in radomly chosen mutated chromosome
	index1: int = random.randrange(1, p_size-1, 1)
	index2: int = index1
	while index2 == index1:
		index2 = random.randrange(1, p_size-1, 1)
	mutated[index1], mutated[index2] = mutated[index2], mutated[index1]
	
	return mutated

def crossover(pop: list, parents: list) -> list:
	offspring: list = [[]]
	off1: list = []
	off2: list = []
	p_size: int = len(pop[parents[0]])
	sub_size: int = p_size / 5

    # Offspring 1 takes subsection in position from parent 1 and fills in from parent 2
    # Offspring 2 does the same in reverse
	random_subset: int = random.randrange(4,10,1)
	random_start_index: int = random.randrange(0,p_size - random_subset - 1,1)
	for i in range(p_size):
		if i == random_start_index:
			for j in range(random_subset):
				off1.append(pop[parents[0]][i])
				i += 1
		else:
			off1.append(pop[parents[1]][i])

	for i in range(p_size):
		if i == random_start_index:
			for j in range(random_subset):
				off2.append(pop[parents[1]][i])
				i += 1
		else:
			off2.append(pop[parents[0]][i])
			
	offspring.append(off1)
	offspring.append(off2)
	offspring.pop(0)

	return offspring

def next_gen(pop: list) -> list:

	population_size: int = 25
	carry_over_size: int = 10
	generation: list = []
	parents: list = []
	chromosome: list = []
	elites: list = []

	for i in range(0,population_size,1):
		rand = random.randrange(1,1000,1)
		if rand > 10:
			parents = selection(pop)
			chromosome = crossover(pop, parents)
		else:
			chromosome = mutate(pop)
		generation.append(chromosome)

	# elites = find_elite_chroms(pop,carry_over_size)
	# for j in range(carry_over_size):
	# 	generation.append(elites[j])
	# generation.pop(0)	
	
	return generation

def find_best_path(pop: list) -> list:
	best_fit: float = 99999.9
	best_path: list = []

	for i in pop:
		if fitness_function(i) < best_fit:
			best_fit = fitness_function(i)
			best_path = i

	return best_path

def find_elite_chroms(pop: list, n: int) -> list:
	top_paths: list = [[]]
	tmp: list = pop

	# Create list of all chromosome fitness
	indiv_fit: list = []

	for p in pop:
		c_fit: float = fitness_function(p)
		indiv_fit.append(c_fit)

	# Sort fitness list in ascending order
	indiv_fit.sort()

	for i in range(n):
		for p in pop:
			if fitness_function(p) == indiv_fit[i]:
				top_paths.append(p)
				break

	return top_paths