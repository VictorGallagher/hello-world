"""Theo Pavlidis Contour Tracing Algorithm."""

import curses
import random
import time
from curses import wrapper
import numpy as np


stdscr = curses.initscr()


def main(stdscr):
    # Clear screen
    stdscr.clear()
    curses.curs_set(0)

(CYAN,BLUE,YELLOW,GREEN,WHITE,RMAGENTA,RYELLOW,MAGENTA,YELLOWRED,RED = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)


if curses.has_colors() is False:
    print("Terminal does not support color\n")
else:
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_YELLOW, curses.COLOR_RED)
    curses.init_pair(10, curses.COLOR_RED, curses.COLOR_BLACK)


'''gernerate a random shape'''


def random_shape(img):
    xr = random.randint(0, 20)
    yr = random.randint(0, 20)
    for x in range(xr, len(img) - xr):
        yr = random.randint(0, 20)
        for y in range(yr, len(img[x]) - yr):
            img[x][y] = 1
            xr = random.randint(0, 20)
    # put some noise in the image %5
    for x in range(xr, len(img)):
        for y in range(yr, len(img[x])):
            xr = random.randint(0, 19)
            if xr == 5:
                img[x][y] = 1
    return img


def showbinimg(a):
    stdscr.refresh()
    stdscr.addstr(0, 0, binimg_to_string(a), curses.color_pair(1))
    stdscr.refresh()
    curses.curs_set(0)


def binimg_to_string(a):
    s = ''
    for x in a:
        s += ''.join(str(y) for y in x)
        s += '\n'
    return s


def find_contour(img):
    global orLog
    orLog = np.array([[0, 0]])

    '''check if pixel possion is in the image'''
    def in_range(x, y, sx, sy):
        return ((x > -1) and (y > -1) and (x < sx) and (y < sy))

        '''is this an isolated pixel'''
    def isolated(img, xy):
        x, y = xy[0], xy[1]
        imgshape = np.shape(img)
        offsets = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]
        for o in offsets:
            xx, yy = o[0], o[1]
            if in_range(x + xx, y + yy, imgshape[0], imgshape[1]) and img[x + xx][y + yy] == 1:
                return False
                break
        return True

        # there must be a better way of doing this than what I came up with
    def omits(cp, bp):
        for i in iter(cp):
            if np.all(bp == i):
                return False
                break
        return True

        '''indexable radial sweep'''
    def next_offset(index):
        # index only -2,1,4,7
        offsets = [([-1, -1], 'w'), ([0, -1], 'w'), ([1, -1], 'w'),
                   ([1, -1], 's'), ([1, 0], 's'), ([1, 1], 's'),
                   ([1, 1], 'e'), ([0, 1], 'e'), ([-1, 1], 'e'),
                   ([-1, 1], 'n'), ([-1, 0], 'n'), ([-1, -1], 'n')]
        while True:
            index += 1
            yield offsets[index % len(offsets)]

    def show_event(x, y, clr, img):  # update image with changes
        stdscr.addch(x, y, ord(str(img)), curses.color_pair(clr) | curses.A_STANDOUT)
        stdscr.refresh()

    def find_start(img):
        img = img.astype(np.uint8)
        breaker = False
        for x in reversed(range(1, random.randint(1, (len(img) - 1)))):
        # for x in range(1,(len(binimg))):
            if breaker is True:
                break
            for y in range(1, len(img[x]) - 1):
                stdscr.addch(x, y, ord(str(img[x][y])), (curses.color_pair(2)))
                stdscr.refresh()
                curses.curs_set(0)
                time.sleep(.001)
                if (img[x][y] == 1):
                    breaker = True
                    break
        show_event(x, y, RED, 'x')
        return [x, y]

    def scan_offsets(img, x, y):
        imgshape = np.shape(img)
        currentpixel = np.array([[1, 1]])
        lastpixel = np.array([0, 0])
        contourpixels = np.array([[0, 0]])
        offset = next_offset(-1)
        startpixel = np.array([[x, y]])
        counter = 0
        iterindex = 0
        index = None
        reset = False
        scanning = True
        pixelbuffer = np.zeros((12, 2), dtype=np.int)
        t = 0

        while scanning:
            counter += 1
            if reset:
                offset = next_offset(index)
                no = offset.next()
                reset = False
            else:
                no = next(offset)
                reset = False
            compass = no[1]
            xy = no[0]
            xx = xy[0]
            yy = xy[1]
            time.sleep(t)

            # check if xy out of range
            if in_range(x + xx, y + yy, imgshape[0], imgshape[1]):
                show_event(x + xx, y + yy, YELLOW, compass)
                time.sleep(t)

                # check for an infinite loop
                if np.all(lastpixel != [[x + xx, y + yy]]):
                    if omits(pixelbuffer, [x + xx, y + yy]):
                        lastpixel = [[x + xx, y + yy]]
                        pixelbuffer = np.concatenate((pixelbuffer, [[x + xx, y + yy]]))
                        pixelbuffer = pixelbuffer[1:]
                        iterindex = 0
                    # if so try again
                    else:
                        iterindex += 1
                        if iterindex > 4:
                            xy = find_start(img)
                            x, y = xy[0], xy[1]
                            startpixel = [x, y]
                            contourpixels = [[0, 0]]

                    np.savetxt('edgDtectLog.txt', orLog, delimiter=',', fmt='%s')
                # check if pixel occupied, if so update current pixel and reset index
                if img[x + xx][y + yy] == 1 and not isolated(binimg, (x + xx, y + yy)):
                    show_event(x + xx, y + yy, YELLOWRED, compass)
                    time.sleep(t)
                    lastpixel = currentpixel
                    currentpixel = [[x + xx, y + yy]]
                    # save pixel location
                    contourpixels = np.concatenate((contourpixels, currentpixel))
                    show_event(x + xx, y + yy, RED, compass)
                    time.sleep(t)
                    x, y = x + xx, y + yy
                    reset = True
                    # update compass direction
                    # index only -2,1,4,7
                    if compass == 'w':
                        index = -2
                    elif compass == 's':
                        index = 1
                    elif compass == 'e':
                        index = 4
                    elif compass == 'n':
                        index = 7

                    # This stops the program from halting if it happens
                    # to double back after just starting
                    if counter > 150:
                        # this provides a larger target than one pixel for halting program
                        if (np.all(currentpixel == startpixel) or
                                (not omits(contourpixels[0:4], currentpixel))):
                            contourpixels = contourpixels[1:]
                            contourpixels = np.unique(contourpixels, axis=0)
                            scanning = False
                            time.sleep(10)
        return contourpixels

    xy = find_start(binimg)
    x = xy[0]
    y = xy[1]
    contours = scan_offsets(binimg, x, y)
    return contours

binimg = np.zeros((45, 45), dtype=np.uint8)
showbinimg(random_shape(binimg))
np.savetxt('edgDtectLog.txt', find_contour(binimg), delimiter=',', fmt='%s')

wrapper(main)
curses.endwin()
#quit()
