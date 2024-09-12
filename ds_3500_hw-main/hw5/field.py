import random as rnd
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.animation as animation


field = (np.random.rand(5,5) < 0.8) * 1


plt.imshow(field, cmap='coolwarm', interpolation=None, vmin=0, vmax=1)
plt.show()
rabbits = [(1,1), (2,3), (4,4)]

rabbits_arr = np.zeros((5,5), dtype=int)

# transposing rabbit positions to the value for rabbits
rabbits_arr[tuple(np.array(rabbits).T)] = 2

# create arrays on the fly 

## notes from class / hints

# size=(10,10)

# field = np.random.randint(0,2, size, dtype=int)
# print(field)
# plt.imshow(field)


# size=(10,10)

    # field = np.random.randint(0,2, size, dtype=int)
    # rabbits = np.random.randint(0,2, size, dtype=int) * 2
    # foxes = np.random.randint(0,2, size, dtype=int) * 3
    # total = np.maximum(np.maximum(field, rabbits), foxes)
    # clist = ['black', 'green', 'blue', 'red']
    # my_cmap = colors.ListedColormap(clist)
    
    # plt.imshow(field, cmap=my_cmap, vmin=0, vmax=3)
    # plt.show()
    
    # plt.imshow(rabbits, cmap=my_cmap, vmin=0, vmax=3)
    # plt.show()
    
    # plt.imshow(foxes, cmap=my_cmap, vmin=0, vmax=3)
    # plt.show()
    
    # plt.imshow(total, cmap=my_cmap, vmin=0, vmax=3)
    # plt.show()


