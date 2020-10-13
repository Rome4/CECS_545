#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Script to use the Closest Edge Insertion Heuristic.
Author: Roman Millem
Date: 14 October 2020
"""

##########################
# PROGRAM INITIALIZATION #
##########################

def missing_package(package: str) -> None:
	print("[*] Your system is missing %(0)s. Please run `easy_install %(0)s` or `pip install %(0)s` before executing." % { '0': package })
	exit()

# Begin imports
import argparse
from decimal import Decimal as D
import functools
import inspect
import os
import platform
import sys
import random

try:
	from packaging import version
except ImportError:
	missing_package("packaging")

try:
	import matplotlib.pyplot as plt
except ImportError:
	missing_package("matplotlib")

try:
	import tsp
except ImportError as e:
	print("[*] Your system is missing the included TSP library file. Please find the original source and download before executing.")
	exit()

if version.parse(platform.python_version()) < version.parse("3.6"):
	print("[*] You must run this on Python 3.6!")
	exit()

# Parse applicable command line arguments
cli = argparse.ArgumentParser(description = "Run Closest Edge Insertion to solve a TSP graph.")
cli.add_argument("file", help = "String :: the coordinates input file in TSP-format", type = str, default = "")
ARGS: dict = cli.parse_args()


##########################
#   PROGRAM  FUNCTIONS   #
##########################

def input_error(message: str) -> None:
	"""Send an error message to the user with usage help."""
	
	global cli
	cli.print_usage(sys.stderr)
	print("\n" + os.path.basename(__file__) + ": error: " + message, file=sys.stderr)
	sys.exit(1)

##########################
#    PROGRAM RUNNABLE    #
##########################

def main():
	global ARGS

	# Prepare the data
	try:
		TSP: tsp.TspHandler = tsp.TspHandler(ARGS.file)
		cities: list = TSP.data["NODE_COORD_SECTION"]
	except Exception as e:
		input_error("can't parse TSP file: " + str(e))
	print("Found %i entries." % TSP.data["DIMENSION"])

	# Generate initial population of size = number of cities
	num_of_cities: int = TSP.data["DIMENSION"]
	pop_size: int = 35
	population: list = []
	for i in range(pop_size):
		rand_path: list = random.sample(range(1,num_of_cities+1,1),num_of_cities)
		chromosome: list = []
		for n in rand_path:
			for x in cities:
				if int(x.name) == n:
					chromosome.append(x)
		population.append(chromosome)

	for p in population:
		p.append(p[0])

	generation: list = population
	best_path: list = []
	count: int = 1
	while True:
		generation = tsp.next_gen(generation)
		best_path = tsp.find_best_path(generation)
		print("")
		print("Best path %d" % count,end=" ")
		count += 1
		print(float(str(round(tsp.fitness_function(best_path), 4))), end=": ")	
		if tsp.fitness_function(best_path) < 1750:
			break

	best_path = tsp.find_best_path(generation)	

	fig = plt.figure()
	fig.canvas.set_window_title("TSP Analysis: " + TSP.data["NAME"] + " (" + ARGS.file + ")")
	color: str = "#d08000"
	best_path: list
	best_fit: float = 9999999.0
	for path in population:
		tmp_fit = tsp.fitness_function(path)
		if tmp_fit < best_fit:
			best_fit = tmp_fit
			best_path = path

	for i in range(len(path)-1):
		plt.plot((best_path[i].x, best_path[i+1].x), (best_path[i].y, best_path[i+1].y), "o-", color=color)
		plt.text(best_path[i].x, best_path[i].y, best_path[i].name, fontsize=9)
		color = "#e11f26"
	plt.show()
    
if __name__ == '__main__':
	try:
		if os.path.isfile(ARGS.file):
			main()			
		else:
			input_error("input file not found: \"" + ARGS.file + "\"")
	except KeyboardInterrupt:
		print("\n\nTerminating.")
		sys.exit(0)