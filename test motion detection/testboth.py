from tkinter import *
# import tkinter.ttk as ttk
from tkinter.ttk import Separator
from calculations import *
from PIL import ImageTk,Image

NUM_IMAGES = 6
FOLDER = 'testimages/'


# def get_images():
# 	for i in range(1,NUM_IMAGES+1):
# 		yield FOLDER+'testimage%s.jpg'%i


# images = tuple(get_images())


# for i in range(1,len(images)):
# 	prev_image, curr_image = images[i-1], images[i]
# 	mse = calc_mse(prev_image, curr_image)
# 	print(mse)



class Main(Tk):
	def __init__(self):
		super().__init__()

		self.bind('<Escape>', self.destroy)
		self.bind('<Left>', self.prev)
		self.bind('<Right>', self.next)
		self.bind("<MouseWheel>", self.mouse_wheel)

		self.i = 1

		prev, latest = self.open_images(self.i)


		self.image_canvas = Canvas(self)

		self.tkimageprev = ImageTk.PhotoImage(master=self.image_canvas, image=prev)
		self.prevlabel = Label(self.image_canvas, image=self.tkimageprev, bg='black')

		gridlblprev = Separator(self.image_canvas, orient='vertical')

		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel = Label(self.image_canvas, image=self.tkimagelatest, bg='black')

		gridlblnext = Separator(self.image_canvas, orient='vertical')

		gridlblhori = Separator(self.image_canvas, orient='horizontal')




		prevbtn = Button(self, text='prev', command=self.prev)
		nextbtn = Button(self, text='next', command=self.next)

		self.mse_lbl = Label(self, text='mse')
		self.ssim_lbl = Label(self, text='ssim')


		self.mse_lbl.     grid(row=0, column=0, sticky='nesw')
		self.ssim_lbl    .grid(row=0, column=1, sticky='nesw')

		self.image_canvas.grid(row=1, column=0, columnspan=2)
		self.prevlabel.   grid(row=0, column=0)
		gridlblprev.      grid(row=0, column=0, sticky='ns')
		gridlblnext.      grid(row=0, column=1, sticky='ns')
		gridlblhori.      grid(row=0, column=0, columnspan=2, sticky='ew')
		self.latestlabel. grid(row=0, column=1)

		prevbtn.          grid(row=2, column=0, sticky='nesw')
		nextbtn.          grid(row=2, column=1, sticky='nesw')

		self.next()
		self.prev()


	def get_filenames(self, i):
		return FOLDER+'testimage%s.jpg'%i, FOLDER+'testimage%s.jpg'%(i+1)



	def open_images(self, i):
		prev, latest = self.get_filenames(i)
		prev = Image.open(prev)
		latest = Image.open(latest)

		return prev, latest


	def update_lbls(self, mse, ssim):
		self.mse_lbl.config(text='MSE: {:,.2f}'.format(mse))
		self.ssim_lbl.config(text='SSIM: {:,.2f}'.format(ssim))


	def update_lbls(self, prev, latest):
		mse, ssim = calc_mse(prev, latest), calc_ssim(prev, latest)
		self.mse_lbl.config(text='MSE: {:,.2f}'.format(mse))
		self.ssim_lbl.config(text='SSIM: {:,.2f}'.format(ssim))


	def update_title(self, prev, latest):
		prev, latest = prev.split('/')[1], latest.split('/')[1]
		self.title('%s, %s'%(prev, latest))


	def prev(self, event=None):
		if self.i <= 1:return

		self.i -= 1
		i = self.i

		prev, latest = self.open_images(i)

		self.tkimageprev = ImageTk.PhotoImage(master=self.image_canvas, image=prev)
		self.prevlabel.config(image=self.tkimageprev) 

		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel.config(image=self.tkimagelatest) 

		prev, latest = self.get_filenames(i)
		self.update_lbls(prev, latest)
		self.update_title(prev, latest)



	def next(self, event=None):
		if self.i >= NUM_IMAGES-1:return

		self.i += 1
		i = self.i

		prev, latest = self.open_images(i)

		self.tkimageprev = ImageTk.PhotoImage(master=self.image_canvas, image=prev)
		self.prevlabel.config(image=self.tkimageprev) 

		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel.config(image=self.tkimagelatest) 


		prev, latest = self.get_filenames(i)
		self.update_lbls(prev, latest)
		self.update_title(prev, latest)


	def mouse_wheel(self, event):
		if event.num == 5 or event.delta == -120:
			self.prev()
		if event.num == 4 or event.delta == 120:
			self.next()


Main().mainloop()