
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time

FIGSIZE = 8
SIZE = 1000


# class Rabbit:

#     def __init__(self):
#         self.x = rnd.randrange(0, SIZE)
#         self.y = rnd.randrange(0, SIZE)
#         self.eaten = 0

#     def reproduce(self):
#         self.eaten = 0
#         return copy.deepcopy(self)


#     def eat(self, amount):
#         self.eaten += amount


#     def move(self):
#         if WRAP:
#             self.x = (self.x + rnd.choice([-1, 0, 1])) % SIZE
#             self.y = (self.y + rnd.choice([-1, 0, 1])) % SIZE
#         else:
#             self.x = min(SIZE-1, max(0, (self.x + rnd.choice([-1, 0, 1]))))
#             self.y = min(SIZE-1, max(0, (self.y + rnd.choice([-1, 0, 1]))))



def animate_func(i, *fargs):
    """ Update our image / figure
    i = frame number
    args = additional optional arguments assigned in FuncAnimation """

    elapsed = (time.time_ns() - start) / 10 ** 9
    fps = i / elapsed
    plt.title(f"Frame: {i} Elapsed: {elapsed:.2f} FPS: {fps:.1f}")
    im = fargs[0]
    im.set_array(np.random.rand(SIZE, SIZE))
    return [im]





def main():


    global start

    start = time.time_ns()

    fig = plt.figure(figsize=(FIGSIZE,FIGSIZE))
    arr = np.random.rand(SIZE,SIZE)
    im = plt.imshow(arr)


    anim = animation.FuncAnimation(
        fig,
        animate_func,
        fargs = (im,),
        frames = 10 ** 100,
        interval = 1, # time between calls to animate_func in ms
        repeat = True
    )

    plt.show()








main()


