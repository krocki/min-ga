#!/usr/bin/env python
# -*- coding: utf-8 -*
# krocki @ 1/12/19
# This is supposed to illustrate how genetic algorithm (GA) works

import random
import argparse
import numpy as np
from scipy import ndimage
from array2gif import write_gif

def random_chromo(length, chars): return ''.join(random.choice(chars) for i in range(length))
def compare(chromo_a, chromo_b): return list(map((lambda x,y: x==y), chromo_a, chromo_b))
def count_chars_matching(chromo_a, chromo_b): return sum(compare(chromo_a,chromo_b))
def fitness(chromosome, target): return count_chars_matching(chromosome, target)
def initial_population(length, chars, N): return [random_chromo(length, chars) for _ in range(N)]

def draw_parent(parents):
    # a very simple selection strategy, parents are sorted in decreasing order accoriding to their fitness
    # we start with parent at index 0, roll the dice, if number is <= 0.5 select this parent, otherwise
    # move to the next parent and so on
    for i in range(len(parents)):
        r = random.uniform(0,1)
        if r < 0.5: return parents[i][0]
    return parents[-1][0]

# a simple mutation strategy, just select a random element and replace with a random symbol
def mutate(chromosome, chars):
    i = random.randint(0, len(chromosome) - 1)

   #          i
   # X = xxxxxxxxxxxxxxxxxxx ( original)
   # ---------|-------------
   # M - xxxxxMxxxxxxxxxxxxx ( mutated )

    mutated=list(chromosome); mutated[i]=random.choice(chars)
    return "".join(mutated)

def crossover(x,y): # x and y are parents

   i = random.randint(1, len(x) - 2) # crossover point 0 (i)
   j = random.randint(1, len(y) - 2) # crossover point 1 (j)
   if i > j: i, j = j, i

   #          i             j
   # X = xxxxx xxxxxxxxxxxxx xxxxxxx ( parent 0)
   # Y = yyyyy yyyyyyyyyyyyy yyyyyyy ( parent 1)
   # -------------------------------
   # p = xxxxx yyyyyyyyyyyyy xxxxxxx ( child 0 )
   # q = yyyyy xxxxxxxxxxxxx yyyyyyy ( child 1 )
   #

   p,q = x[:i] + y[i:j] + x[j:], y[:i] + x[i:j] + y[j:]
   return p, q # 2 children

imgs=[]

if __name__ == "__main__":

  ### parse args
  parser = argparse.ArgumentParser(description='')
  parser.add_argument('--popsize', type=int, default=1000, help='population size')

  parser.add_argument('--target', type=str, default="berry.gif", help='target img')
  parser.add_argument('--max_generations', type=int, default=500, help='maximum number of generations allowed')
  opt = parser.parse_args()

  im_array = (ndimage.imread(opt.target)//128).transpose(2,0,1)
  target = "".join([str(x) for x in im_array.flatten()])

  # this is just a list of chars allowed
  alphabet='01'
  crossover_prob=0.9 # probability of 2 parents breeding
  mutate_prob=0.1 # probability of random mutation

  # initially we create a pool of random guesses of our 'secret' word
  population,generation=initial_population(len(target), alphabet, opt.popsize),0
  # the main loop
  while generation < opt.max_generations:

    # evalulate the population based on similarity to the secret word
    pop_fitness=[(i,fitness(i,target)) for i in population]
    sorted_pop = sorted(pop_fitness, key=lambda x: -x[1])

    new_population=[]

    for i in range(opt.popsize//2): # 1st half of the population is used, 2nd half dies

      # selection
      x,y = draw_parent(sorted_pop), draw_parent(sorted_pop)
      # crossover
      if random.random() < crossover_prob: p,q=crossover(x,y)
      else: p,q=x,y
      # mutate
      p = mutate(p, alphabet) if random.random() < mutate_prob else p
      q = mutate(q, alphabet) if random.random() < mutate_prob else q

      new_population.append(p); new_population.append(q)

    print("generation {:3d}\nfitness {:3d}\n".format(generation, sorted_pop[0][1]))

    # we found a solution
    if sorted_pop[0][0] == target: break

    population=new_population # parents die, children take over
    frame = np.array([255 if x=='1' else 0 for x in list(sorted_pop[0][0])]).reshape(3,im_array.shape[1],im_array.shape[2])
    imgs.append(frame)
    generation += 1

  write_gif(imgs, 'img-ga', fps=25)
