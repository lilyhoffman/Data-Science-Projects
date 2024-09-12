"""
File: alife.py
Description: A simple artificial life simulation.

"""
import random as rnd
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.animation as animation
import argparse


class Animal:
    
    def __init__(self, size, type,k, wrap=True):
        """Generates an animal object

        Args:
            size (int): size of the field, to determine where this animal spawns in
            type (string): type of animal; either rabbit or fox
            k (int): number of generations / cycles they can do without eating
        """
        self.x = rnd.randrange(0, size)
        self.y = rnd.randrange(0, size)
        self.size = size
        self.type = type
        self.CYCLES = k
        self.gens_left = k
        self.eaten = 0
        self.wrap = wrap
    
    def reproduce(self):
        if self.eaten == 1:
            self.eaten =  0
            self.gens_left = self.CYCLES
            return copy.deepcopy(self)
    
    def eat(self, amount):
        if amount != 0:
            self.eaten += amount
        else:
            self.gens_left-=1
        
    def move(self):
        m_d = 1
        if type == 'fox':
            m_d = 2

            
        if self.wrap:
            self.x = (self.x + rnd.choice([-m_d, 0, m_d])) % self.size
            self.y = (self.y + rnd.choice([-m_d, 0, m_d])) % self.size
        else:
            self.x = min(self.size-1, max(0, (self.x + rnd.choice([-m_d, 0, m_d]))))
            self.y = min(self.size-1, max(0, (self.y + rnd.choice([-m_d, 0, m_d]))))



class Field:
    """ A field is a patch of grass with 0 or more rabbits hopping around
    in search of grass """

    def __init__(self, size, gr, f_o, r_o):
        self.rabbits = []
        self.foxes = []
        self.field = np.ones(shape=(size, size), dtype=int)
        self.size = size
        self.gr = gr
        self.f_o = f_o
        self.r_o = r_o

    def add_animal(self, animal):
        if animal.type == "rabbit":
            self.rabbits.append(animal)
            
        else:
            self.foxes.append(animal)
            
    

    def move(self):
        for r in self.rabbits:
            r.move()
        for f in self.foxes:
            f.move()

    def eat(self):
        """ 
        All rabbits try to eat grass at their current location\n
        All foxes try to eat a rabbit at their current location
        """
        for r in self.rabbits:
            r.eat(self.field[r.x, r.y])
            self.field[r.x, r.y] = 0
            
        for f in self.foxes:
            rabbits_arr = self.get_rabbits_loc()
            f.eat(rabbits_arr[f.x,f.y])
            self.remove_eaten_rabbit(f.x,f.y)
    
    def remove_eaten_rabbit(self,x,y):
        """removes eaten rabbit from the list of rabbits

        Args:
            x (int): x coord to remove on
            y (int): y coord to remove on
        """
        for r in self.rabbits:
            if r.x == x and r.y == y:
                self.rabbits.remove(r)
                
    def get_rabbits_loc(self):
        rabbits_pos = [(r.x, r.y) for r in self.rabbits]
        
        rabbits_arr = np.zeros((self.size,self.size), dtype=int)
        if len(rabbits_pos) > 0:
            rabbits_arr[tuple(np.array(rabbits_pos).T)] = 1
        return rabbits_arr
    
    def get_fox_location(self):
        fox_loc = [(r.x, r.y) for r in self.foxes]
        foxes_arr = np.zeros((self.size,self.size), dtype=int)
        if len(fox_loc) > 0:
            foxes_arr[tuple(np.array(fox_loc).T)] = 1
        return foxes_arr
            


    def survive(self):
        """ Rabbits that have not eaten die. Otherwise, they live """
        self.rabbits = [r for r in self.rabbits if r.gens_left > 0]
        
        self.foxes = [f for f in self.foxes if f.gens_left > 0]


    def reproduce(self):
        r_born = []
        f_born = []
        for r in self.rabbits:
                for _ in range(rnd.randint(1,self.r_o)):
                    r_born.append(r.reproduce())
        self.rabbits += r_born
        
        for f in self.foxes:
                for _ in range(rnd.randint(1,self.f_o)):
                    f_born.append(f.reproduce())
        self.foxes += f_born
        
        self.rabbits = [r for r in self.rabbits if r is not None]
        self.foxes = [f for f in self.foxes if f is not None]
            




    def grow(self):
        """
        Grows the field of grass
        """
        growloc = (np.random.rand(self.size,self.size) < self.gr) * 1
        self.field = np.maximum(self.field, growloc)

    def generation(self):
        """ Run one generation of rabbit and fox actions """
        self.move()
        self.eat()
        self.survive()
        self.reproduce()
        self.grow()
        
        
        
## Outside Field Class
def animate(i, field, im, speed):
    for _ in range(speed):
        field.generation()
    rabbits = field.get_rabbits_loc() * 2
    foxes = field.get_fox_location() * 3
    total_field = np.maximum(np.maximum(field.field, rabbits), foxes)
    im.set_array(total_field)
    plt.title("Generation: " + str(i * speed) + " Rabbits: " + str(len(field.rabbits)) + " Foxes: " + str(len(field.foxes)))
    
    if i * speed == 1000:
        generate_bar_chart(np.count_nonzero(field.field == 1),len(field.rabbits),len(field.foxes) )
    return im,


def define_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-g", "--grass_rate", help="Probability of grass growing at any given location, e.g., 2%", type=float)
    parser.add_argument("-sp", "--speed", help="Number of generations per frame", type=int)
    parser.add_argument("-f_k", "--fox_k", help="Number of cycles a fox can survive without eating", type=int)
    parser.add_argument("field_size", help="x/y dimensions of the field", type=int)
    parser.add_argument("num_foxes", help="Number of initial foxes", type=int)
    parser.add_argument("num_rabbits", help="Number of initial rabbits", type=int)
    parser.add_argument("-w", "--wrap", help="Whether animal movements can wrap around the field", action="store_true")
    parser.add_argument("-f_o", "--fox_offspring", help="Max number of offspring a fox can produce in one generation", type=int)
    parser.add_argument("-r_o", "--rabbit_offspring", help="Max number of offspring a rabbit can produce in one generation", type=int)
    return parser


def generate_bar_chart(grass, rabbits, foxes):
    types = ["grass", "rabbits", "foxes"]
    values = [grass, rabbits, foxes]
    
    fig = plt.figure(figsize=(10,10))
    
    plt.bar(types, values, width=.4)
    plt.xlabel("Types")
    plt.ylabel("Number in Environment")
    plt.title("Who's around after 1000 Generations")
    for i in range(len(types)):
        plt.text(i, values[i], values[i], ha = 'center')
    plt.savefig("generation_1000_graph.png")
    
    
    


def main():
    
    args = define_parser().parse_args()
    GRASS_RATE = .1
    if args.grass_rate:
        GRASS_RATE = args.grass_rate
    
    SPEED=1
    if args.speed:
        SPEED = args.speed
    
    FOX_K = 10
    if args.fox_k:
        FOX_K = args.fox_k
    
    SIZE = 400
    if args.field_size:
        SIZE = args.field_size
    
    WRAP = True    
    if args.wrap:
        WRAP = args.wrap
        
    
    if args.num_foxes:
        INIT_FOXES = args.num_foxes
    if args.num_rabbits:
        INIT_RABBITS = args.num_rabbits
        
    RABBIT_OFFSPRING = 2
    if args.rabbit_offspring:
        RABBIT_OFFSPRING = args.rabbit_offspring
    
    FOX_OFFSPRING = 1
    if args.fox_offspring:
        FOX_OFFSPRING = args.fox_offspring
        

    # Create the ecosystem
    field = Field(size=SIZE, gr=GRASS_RATE, f_o=FOX_OFFSPRING, r_o=RABBIT_OFFSPRING)

    # Initialize with some rabbits
    for _ in range(INIT_RABBITS):
        field.add_animal(Animal(type="rabbit", k=1, size=SIZE, wrap=WRAP))
        
    for _ in range(INIT_FOXES):
        field.add_animal(Animal(type="fox", k=FOX_K, size=SIZE, wrap=WRAP))
        
    
    

    #Set up the image object
    array = np.ones(shape=(SIZE, SIZE), dtype=int)
    fig = plt.figure(figsize=(10,10))
    col_list = ['black', 'green', 'blue', 'red']
    my_cmap = colors.ListedColormap(col_list)
    im = plt.imshow(array, cmap=my_cmap, interpolation=None, aspect='auto', vmin=0, vmax=3)
    
    anim = animation.FuncAnimation(fig, animate, fargs=(field, im, SPEED), frames=10**100, interval=1, repeat=True)
    plt.show()
    





if __name__ == '__main__':
    main()
    
    



