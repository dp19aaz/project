from tkinter import *
from tkinter.ttk import Separator
from calculations import *
from PIL import ImageTk,Image


class Main(Tk):
	def __init__(self, filenames):
		super().__init__()

		self.bind('<Escape>', self.destroy)
		self.bind('<Left>', self.prev)
		self.bind('<Right>', self.next)
		self.bind("<MouseWheel>", self.mouse_wheel)

		self.filenames = filenames
		print(filenames)

		self.i = 0

		prev, latest = self.open_images(self.i)


		self.image_canvas = Canvas(self)

		self.tkimageprev = ImageTk.PhotoImage(master=self.image_canvas, image=prev)
		self.prevlabel = Label(self.image_canvas, image=self.tkimageprev, bg='black')

		gridlblprev = Separator(self.image_canvas, orient='vertical')

		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel = Label(self.image_canvas, image=self.tkimagelatest, bg='black')

		gridlblnext = Separator(self.image_canvas, orient='vertical')

		gridlblhori = Separator(self.image_canvas, orient='horizontal')




		self.prevbtn = Button(self, text='prev', command=self.prev, state='disabled')
		self.nextbtn = Button(self, text='next', command=self.next)

		self.deletebtn = Button(self, text='delete pics', command=self.delete_pics)


		self.mse_lbl = Label(self, text='mse')


		self.mse_lbl.     grid(row=0, column=0, columnspan=2, sticky='nesw')

		self.image_canvas.grid(row=1, column=0, columnspan=2)
		self.prevlabel.   grid(row=0, column=0)
		gridlblprev.      grid(row=0, column=0, sticky='ns')
		gridlblnext.      grid(row=0, column=1, sticky='ns')
		gridlblhori.      grid(row=0, column=0, columnspan=2, sticky='ew')
		self.latestlabel. grid(row=0, column=1)

		self.prevbtn.          grid(row=2, column=0, sticky='nesw')
		self.nextbtn.          grid(row=2, column=1, sticky='nesw')
		self.deletebtn.        grid(row=3, column=0, sticky='nesw')


	def get_filenames(self, i):
		now, nxt = self.filenames[i], self.filenames[i+1]
		return 'pics/%s.jpg'%now, 'pics/%s.jpg'%nxt



	def open_images(self, i):
		prev, latest = self.get_filenames(i)
		prev = Image.open(prev)
		latest = Image.open(latest)

		return prev, latest


	def update_lbls(self, prev, latest, i):
		mse = calc_mse(prev, latest)

		self.mse_lbl.config(text='MSE: {:,.2f}'.format(mse))


		prev, latest = self.open_images(i)

		self.tkimageprev = ImageTk.PhotoImage(master=self.image_canvas, image=prev)
		self.prevlabel.config(image=self.tkimageprev) 

		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel.config(image=self.tkimagelatest) 



	def update_title(self, prev, latest):
		prev, latest = prev.split('/')[1], latest.split('/')[1]
		self.title('%s, %s'%(prev, latest))


	def prev(self, event=None):
		if self.i < 1:return

		self.i -= 1
		i = self.i

		self.nextbtn.config(state='normal')
		if i == 0:self.prevbtn.config(state='disabled')

		prev, latest = self.get_filenames(i)
		self.update_lbls(prev, latest, i)
		self.update_title(prev, latest)



	def next(self, event=None):
		if self.i >= len(self.filenames)-2:return

		self.i += 1
		i = self.i

		print(self.i, len(self.filenames))

		self.prevbtn.config(state='normal')
		if i == len(self.filenames)-2:self.nextbtn.config(state='disabled')


		prev, latest = self.get_filenames(i)
		self.update_lbls(prev, latest, i)
		self.update_title(prev, latest)


	def mouse_wheel(self, event):
		if event.num == 5 or event.delta == -120:
			self.prev()
		if event.num == 4 or event.delta == 120:
			self.next()


	def delete_pics(self):
		...#delete picture files
		self.delete_from_motionlog()



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






def main():
	with open('motionlog.txt', 'r') as f:
		motions = f.read()

	motions = motions.split('\n')
	if '' in motions: motions.remove('')
	start_times = [i.split(',')[0] for i in motions]

	print('\n'.join(['%s\t%s, %s'%(index, time, motions[index].count(',')+1) for index, time in enumerate(start_times)]))

	choice = 2
	Main(motions[choice].split(',')).mainloop()




if __name__ == '__main__':
	main()