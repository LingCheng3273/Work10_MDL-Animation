from mdl import *
import mdl
from display import *
from matrix import *
from draw import *
    
global basename
basename = 'base'

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands):
    global basename
    global frames
    global isVary
    global isFrames
    global isName
    isVary = False
    isFrames = False
    isName = False
    for command in commands:
        if command[0] == 'frames':            
            print 'setting frames to ' + str(command[1])
            isFrames = True
            frames = command[1]
        elif command[0] == 'basename':
            print 'setting basename to ' + str(command[1])
            isName = True
            basename = command[1]
        elif command[0] == 'vary':
            if command[3] < command[2]:
                print 'vary parameters are invalid'
                return
            isVary = True
    if isVary and not isFrames:
        "vary was set but frames wasn't"
        return
    if isFrames and not isName:
        print "basename has been set to 'base'"
        basename = 'base'



"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands):
    #command: ['name', 'knob', start_frame, end_fame, start_val, end_val]   
    for command in commands:
        if command[0] == 'vary':
            vary(command[1], command[2], command[3], command[4], command [5])


def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return
    first_pass(commands)
    second_pass(commands)

    for frame in range (frames):
        print "Creating frame: " + str(frame)
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        tmp = []
        step = 0.1

        for command in commands:
            #update symbol table
            for knob in symbols:
                setKnob(symbols, knob, hash_table[knob][frame])
            
            c = command[0]
            args = command[1:]
            if c == 'set':
                setKnob(symbols, ags[0], args[1])
            elif c == 'setknobs':
                setKnobs(symbols, ags[0])
                
            elif c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                if args[3] not in hash_table:
                    arg0 = args[0]
                    arg1 = args[1]
                    arg2 = args[2]
                else:
                    knob_name = args[3]
                    knob_val = symbols[knob_name]
                    arg0 = args[0] * knob_val
                    arg1 = args[1] * knob_val
                    arg2 = args[2] * knob_val
                tmp = make_translate(arg0, arg1, arg2)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if args[3] not in hash_table:
                    arg0 = args[0]
                    arg1 = args[1]
                    arg2 = args[2]
                else:
                    knob_name = args[3]
                    knob_val = symbols[knob_name]
                    arg0 = args[0] * knob_val
                    arg1 = args[1] * knob_val
                    arg2 = args[2] * knob_val
                tmp = make_scale(arg0, arg1, arg2)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if args[2] not in hash_table:
                    arg1 = args[1]
                else: 
                    knob_name = args[2]
                    knob_val = symbols[knob_name]
                    arg1 = args[1] * knob_val
                theta = arg1 * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])

        if frame < 10:
            save_name = basename + '00' + str(frame)
        elif frame < 100:
            save_name = basename + '0' + str(frame)
        else:
            save_name = basename + str(frame)
        save_ppm(screen, save_name)
    make_animation(basename)
