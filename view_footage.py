from tkinter import *
from tkinter.ttk import Separator
from calculations import *
from PIL import ImageTk,Image
from os import remove as osremove
from functools import partial


###########################
### Picture class
###########################
class pic:
	def __init__(self, master, image):

		self.master = master

		self.image_cvs = ImageTk.PhotoImage(master=self.master, image=image)#image_canvas
		self.image_lbl = Label(master, image=self.image_cvs)

		self.horiz_sep = Separator(master, orient='horizontal')
		self.verti_sep = Separator(master, orient='vertical')


	### Grid (geometry management)
	def grid(self, **kwargs):
		self.image_lbl.grid(**kwargs)
		self.horiz_sep.grid(**kwargs, sticky='we')
		self.verti_sep.grid(**kwargs, sticky='ns')


	### Update image
	def update(self, image, show_grid):
		self.image_cvs = ImageTk.PhotoImage(master=self.master, image=image)
		self.image_lbl.config(image=self.image_cvs)

		if show_grid:
			self.horiz_sep.grid()
			self.verti_sep.grid()
		else:
			self.horiz_sep.grid_remove()
			self.verti_sep.grid_remove()


###########################
### Main window
###########################
class Main(Tk):
	def __init__(self, filenames):
		super().__init__()

		self.bind('<Escape>', self.destroy)
		self.bind('<Left>', self.prev)
		self.bind('<Right>', self.next)
		self.bind("<MouseWheel>", self.mouse_wheel)

		self.filenames = filenames

		self.i = 0

		self.show_mse  = BooleanVar(); self.show_mse .set(True)
		self.show_grid = BooleanVar(); self.show_grid.set(True)


		self.image_canvas = Canvas(self)

		prev, ltst = self.open_images(self.i) # previous, latest

		self.prev_pic = pic(self.image_canvas, prev)
		self.ltst_pic = pic(self.image_canvas, ltst)



		self.prevbtn = Button(self, text='prev', command=self.prev, state='disabled')
		self.nextbtn = Button(self, text='next', command=self.next)

		self.deletebtn = Button(self, text='delete pics', command=self.delete_pics)
		self.mse_chkbtn = Checkbutton(self, text='Show MSE', variable=self.show_mse)
		self.grid_chkbtn = Checkbutton(self, text='Show grid', variable=self.show_grid)

		self.mse_lbl = Label(self, text='mse')


		#geometry management
		self.mse_lbl.       grid(row=0, column=0, columnspan=2, sticky='nesw')

		self.image_canvas.  grid(row=1, column=0, columnspan=2)
		self.prev_pic.      grid(row=0, column=0)
		self.ltst_pic.      grid(row=0, column=1)

		self.prevbtn.       grid(row=2, column=0, sticky='nesw')
		self.nextbtn.       grid(row=2, column=1, sticky='nesw')
		self.deletebtn.     grid(row=3, column=0, sticky='nesw', rowspan=2)
		self.mse_chkbtn.    grid(row=3, column=1, sticky='nesw')
		self.grid_chkbtn.   grid(row=4, column=1, sticky='nesw')


	### Return filenames in form "pics/%s.jpg"%s
	def get_filenames(self, i):
		now, nxt = self.filenames[i], self.filenames[i+1]
		return 'pics/%s.jpg'%now, 'pics/%s.jpg'%nxt



	### Open images from filename as PIL images
	def open_images(self, i):
		prev, latest = self.get_filenames(i)

		prev = Image.open(prev)
		latest = Image.open(latest)

		return prev, latest



	### Update window labels
	def update_lbls(self, prev, latest, i):
		if self.show_mse.get():
			mse = calc_mse(prev, latest)
			self.mse_lbl.config(text='MSE: {:,.2f}'.format(mse))

		else:
			self.mse_lbl.config(text='MSE disabled')


		prev, ltst = self.open_images(i)
		self.prev_pic.update(prev, self.show_grid.get())
		self.ltst_pic.update(ltst, self.show_grid.get())



	### Update window title
	def update_title(self, prev, latest, i):
		prev, latest = prev.split('/')[1], latest.split('/')[1]
		self.title('%s, %s. (%s/%s)'%(prev, latest, i+1, len(self.filenames)-1))


	### Go to previous frame
	def prev(self, event=None):
		if self.i < 1:return

		self.i -= 1
		i = self.i

		self.nextbtn.config(state='normal')#enable next button
		if i == 0:
			self.prevbtn.config(state='disabled')#disable prev button

		#go to prev frame
		prev, latest = self.get_filenames(i)
		self.update_lbls(prev, latest, i)
		self.update_title(prev, latest, i)


	### Go to next frame
	def next(self, event=None):
		if self.i >= len(self.filenames)-2:return

		self.i += 1
		i = self.i

		self.prevbtn.config(state='normal')#enable prev button
		if i == len(self.filenames)-2:
			self.nextbtn.config(state='disabled')#disable next button

		#go to next frame
		prev, latest = self.get_filenames(i)
		self.update_lbls(prev, latest, i)
		self.update_title(prev, latest, i)


	### Facilitate scrolling to move between frames
	def mouse_wheel(self, event):
		if event.num == 5 or event.delta == -120:
			self.prev()
		if event.num == 4 or event.delta == 120:
			self.next()


	### Delete images and references from motionlog and quit
	def delete_pics(self):
		self.delete_images()
		self.delete_from_motionlog()
		self.destroy()


	### Delete image files
	def delete_images(self):
		print(self.filenames)
		for filename in self.filenames:
			print(filename)
			filename = 'pics/%s.jpg'%filename
			osremove(filename)


	### Delete image references from motionlog
	def delete_from_motionlog(self):
		start_time = self.filenames[0]

		with open('motionlog.txt', 'r') as f:
			motions = f.read()

		motions = motions.split('\n')
		if '' in motions: motions.remove('')

		for index, i in enumerate(motions.copy()):
			if i.startswith(start_time):
				motions.pop(index)
				break

		with open('motionlog.txt', 'w') as f:
			f.write('\n'.join(motions))



###########################
### Setup window
###########################
class setup(Tk):
	def __init__(self, options):
		super().__init__()

		for option in options:
			btn = Button(self, text=option, command=partial(self.choose, option))
			btn.grid()


	def choose(self, option):
		self.choice = option
		self.destroy()



###########################
### Main
###########################
def main():
	with open('motionlog.txt', 'r') as f:
		motions = f.read()

	motions = motions.split('\n')
	if '' in motions: motions.remove('')
	start_times = [i.split(',')[0] for i in motions]

	print('\n'.join(['%s\t%s, %s'%(index, time, motions[index].count(',')+1) for index, time in enumerate(start_times)]))


	#not working
	# setup_win = setup(start_times)
	# setup_win.mainloop()
	# Main(motions[setup_win.choice].split(','))



	# choice = int(input('Select a collection of frames to view.'))
	choice = 1
	Main(motions[choice].split(',')).mainloop()




if __name__ == '__main__':
	main()