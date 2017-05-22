import mdl
from display import *
from matrix import *
from draw import *

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
def first_pass( commands ):
	f = -1
	b = -1
	v = []
	for i in range(len(commands)):
		if commands[i][0] == "frames":
			f=i
		if commands[i][0] == "basename":
			b=i
		if commands[i][0] == "vary":
			v.append(i)
	#print [f, b, v]

	if f != -1:
		#print commands[f][1]
		num_frames = commands[f][1]
	if b != -1:
		basename = commands[b][1]
	if len(v) != 0 and f == -1:
		print 'your script is bad and you should feel bad'
		exit()
	if f != -1 and b == -1:
		basename = 'pic'
		print 'basename set to pic'
	return [num_frames, basename]

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
def second_pass( commands, num_frames ):
	library = []
	bookshelf = []
	#book = []
	page = []
	v=[]
	for i in range(len(commands)):
		if commands[i][0] == 'vary':
			v.append(i)
	for i in range(len(v)):
		p = v[i]
		book = {'name': commands[p][1], 'fstart': commands[p][2], 'fend': commands[p][3], 'vstart': commands[p][4], 'vend': commands[p][5], commands[p][1]: 1.0}
		#print book
		bookshelf.append(book)
	for j in range(len(bookshelf)):
		ftot = float(bookshelf[j]['fend']) - float(bookshelf[j]['fstart'])
		vtot = float(bookshelf[j]['vend'] )- float(bookshelf[j]['vstart'])
		bookshelf[j]['delta'] = (vtot/ftot)
	for i in range(num_frames):
		knob = {}
		for j in range(len(bookshelf)):
			knob[bookshelf[j]['name']] = 1.0
		for j in range(len(bookshelf)):
			if bookshelf[j]['fstart'] <= i and i <= bookshelf[j]['fend']:
				knob[bookshelf[j]['name']] = (bookshelf[j]['delta'] * (i - bookshelf[j]['fstart'])) + bookshelf[j]['vstart']
		library.append(knob)
	return library





def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    ident(tmp)
    #stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    tmp = []
    step = 0.1

    col = first_pass(commands)
    num_frames = col[0]
    basename = col[1]
    #print [num_frames, basename]
    knobs = second_pass(commands, num_frames)
    #print knobs

	#Do you know how hard it is to enclose everything in a for loop when python hates your tabs?
	#Hint: Very
    if num_frames == -1:
		num_frames = 1
    for framenumber in range(num_frames):
    	clear_screen(screen)
    	tmp = new_matrix()
    	ident(tmp)
    	stack = [ [x[:] for x in tmp] ]
    	for command in commands:

        #print command
        	c = command[0]
        	args = command[1:]

        	knobmult = 1.0
        	if (c == 'move' or c == 'rotate' or c == 'scale'):
				if (c == 'move' or c == 'scale') and len(args) == 4 and args[3] != None:
					#print args
					#print [c,'a',args[2]]
					#print knobs[framenumber][args[3]]
					knobmult = float(knobs[framenumber][args[3]])
				if c == 'rotate' and len(args) == 3 and args[2] != None:
					knobmult = float(knobs[framenumber][args[2]])
				#print knobmult

        	if c == 'box':
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
        		tmp = make_translate(args[0] * knobmult, args[1] * knobmult, args[2] * knobmult)
        		matrix_mult(stack[-1], tmp)
        		stack[-1] = [x[:] for x in tmp]
        		tmp = []
        	elif c == 'scale':
        		#print knobmult
        		tmp = make_scale(args[0] * knobmult, args[1] * knobmult, args[2] * knobmult)
        		#print tmp
        		matrix_mult(stack[-1], tmp)
        		#print tmp
        		stack[-1] = [x[:] for x in tmp]
        		#print [tmp]
        		tmp = []
        	elif c == 'rotate':
        		theta = args[1] * (math.pi/180) * knobmult
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
        		#print [framenumber]
        		threedigit = '%03d' % framenumber
        		savename  = "anim/"+ basename + threedigit + ".png"
        		save_extension(screen, savename)
