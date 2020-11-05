#!/usr/bin/env python3

import os
import sys
from argparse import ArgumentParser
from os import linesep
from random import SystemRandom
# from signal import signal, SIG_DFL  # , SIGPIPE
from time import perf_counter as time
from generators import available_generators, create
from utils.console_tools import query_yes_no_abort

import numpy as np
import matplotlib.pyplot as plt #библиотека для построения графиков

from matplotlib import colors


def main():
    parser = ArgumentParser(description='(Pseudo)Random Number Generators')
    parser.add_argument('-g', '--generator', help='Generator selection.')
    parser.add_argument('-s', '--seed', help='Initial seed.')
    parser.add_argument('-c', '--count', help='Total number of generated numbers.', default='10')
    parser.add_argument('-b', '--binary', help='Binary mode.', action='store_true')
    parser.add_argument('-t', '--timer', help='Timer mode (no output)', action='store_true')
    parser.add_argument('-f', '--file', help='File for output')
    args = parser.parse_args()

    args.count = args.count.lower()
    if args.count == 'inf':
        count = 2 ** 50
    elif args.count.endswith('k'):
        count = 1000 * int(args.count[:-1])
    elif args.count.endswith('m'):
        count = 1000000 * int(args.count[:-1])
    elif args.count.endswith('g'):
        count = 1000000000 * int(args.count[:-1])
    else:
        count = int(args.count)

    if args.seed:
        seed = int(args.seed)
    else:
        seed = SystemRandom().getrandbits(128)

    if args.generator not in available_generators:
        print("Invalid generator. Available values are", available_generators)
        parser.print_usage()
        sys.exit(1)

    generator = create(args.generator, seed)

    title = generator.info()[0] + "\nn=" + '{0:10.2e}'.format(count)
    name = args.generator + "_count" + '{0:10.2e}'.format(count).replace(' ', '_')

    out = None

    if not args.timer:
        if args.file:
            if os.path.isfile(args.file) and not query_yes_no_abort(
                    "Specified file " + args.file + " exists. Overwrite?"):
                print('Aborting')
                sys.exit(0)
            out = open(args.file, mode='wb', buffering=512 * 1024)
        else:
            out = sys.stdout
    random_numbers_array = []
    time_start = time()
    if args.binary:
        if args.timer:
            list(map(lambda j: (generator.random_byte()), range(count)))
        else:
            remaining = count
            while remaining > 0:
                generated_bytes = generator.random_bytes(min(remaining, 1024 * 1024))
                out.write(bytes(generated_bytes)[:min(remaining, len(generated_bytes))])
                remaining -= len(generated_bytes)
                print("Progress:", (count - remaining) / count * 100, "%", flush=True)

    else:  # not args.binary

        if hasattr(generator, 'random_number'):
            random_numbers = map(lambda j: (generator.random_number()), range(count))

        else:
            random_numbers = map(lambda j: (generator.randrange(0, 2 << 32)), range(count))

        if args.timer:
            random_numbers_array = list(random_numbers)
        else:
            out.write(linesep.join(map(str, random_numbers)))

    if args.file or args.timer:
        time_elapsed = time() - time_start
        print("Finished in %.3f seconds" % time_elapsed, end='')
        if args.binary and time_elapsed > 0:
            print(',', 8 * count / time_elapsed / 1024 / 1024, "Mbps", end='')
        print()
    if args.timer:
        buldPlot(arr=random_numbers_array, title=title, name=name, count=count)


def print_progress(perc):
    print(str(perc) + '% ', end='', flush=True)


def buldPlot(arr, title, name, count):
    size_plot = 800
    m = int(max(arr) * 1.001)
    k = float(m / size_plot)
    kc = float(count / (size_plot * 2))

    dat1 = np.zeros((size_plot, size_plot))  # создаём матрицу значений
    dat2 = np.zeros((size_plot, size_plot * 2))

    i = 0
    tmp = 0
    for item in arr:
        dat2[int(item / k)][int(i / kc)] += 1
        item = int(float(item) / k)
        #if i % 2 != 0:
        dat1[tmp][item] += 1
        tmp = item
        i += 1

    fig = plt.figure()
    pc = plt.pcolor(dat1)  # метод псевдографики pcolor
    plt.colorbar(pc)
    plt.title(title)
    save(name=name + "_1", fmt='jpg')
    plt.show()

    fig = plt.figure()
    pc = plt.pcolor(dat2)
    #plt.colorbar(pc)
    plt.title(title)
    save(name=name + "_2", fmt='jpg')
    plt.show()

    # cmap = colors.ListedColormap(['white', 'black', 'black', 'black'])
    # bounds = [0.0, 1.0, 2.0, 3.0]
    # norm = colors.BoundaryNorm(bounds, cmap.N)
    # heatmap = plt.pcolor(np.array(dat), cmap=cmap, norm=norm)
    # plt.colorbar(heatmap, ticks=[0, 1, 2, 3])
    # plt.show()


def save(name='', fmt='jpg'):
    pwd = os.getcwd()
    iPath = 'pictures\{}'.format(fmt)
    if not os.path.exists(iPath):
        os.mkdir(iPath)
    os.chdir(iPath)
    plt.savefig('{}.{}'.format(name, fmt))
    os.chdir(pwd)


if __name__ == '__main__':
    # signal(SIGPIPE, SIG_DFL)

    main()
