from tkinter import *
from tkinter import filedialog
import os
import cv2
from PIL import ImageTk, Image
import LPD
import OCR
import sqlite3 as sq
import time
import re


def resize_and_convert(image_path):
    original = cv2.imread(image_path)
    resized = cv2.resize(original, (300, 200))
    color_converted = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    return ImageTk.PhotoImage(Image.fromarray(color_converted))


class GUI:
    def __init__(self, db_connection):
        self.db = db_connection
        self.last_dir = "."
        self.root = Tk()
        self.root.title('ANPR')
        self.root.geometry("700x360")
        self.root.config()

        # Left Frame and its contents
        self.leftFrame = Frame(self.root, width=200, height=400)
        self.leftFrame.grid(row=0, column=0, padx=10, pady=2)

        Label(self.leftFrame, text="Instructions:").grid(row=0, column=0, padx=10, pady=2)
        self.Instruct = Label(self.leftFrame, anchor='w', justify='left', text="""
        1. Click \'Browse\' and select an image file
        2. Click \'Detect\'
        3. Repeat as necessary
        4. Click \'Close\' when finished to make 
           sure changed are committed to the DB
                                                   """)
        self.Instruct.grid(row=1, column=0, padx=10, pady=2)

        self.left_image = resize_and_convert("JPGs\\anpr.jpg")
        self.left_image_label = Label(self.leftFrame, image=self.left_image)
        self.left_image_label.grid(row=2, column=0, padx=10, pady=2)

        # Right Frame and its contents
        self.rightFrame = Frame(self.root, width=200, height=600)
        self.rightFrame.grid(row=0, column=1, padx=10, pady=2)

        self.right_image = resize_and_convert("JPGs\\anpr1.jpg")
        self.right_image_label = Label(self.rightFrame, image=self.right_image)
        self.right_image_label.grid(row=0, column=0, padx=10, pady=2)

        self.btnFrame = Frame(self.rightFrame, width=200, height=200)
        self.btnFrame.grid(row=1, column=0, padx=10, pady=2)

        self.browse_entry = Entry(self.rightFrame, width=40)
        self.browse_entry.grid(row=2, column=0, padx=10, pady=2)

        self.output_number = Text(self.rightFrame, width=30, height=2, takefocus=0)
        self.output_number.grid(row=4, column=0, padx=10, pady=2)

        self.button_detect = Button(self.btnFrame, text="Detect", command=self.detect)
        self.button_detect.grid(row=0, column=0, padx=10, pady=2)

        self.button_explore = Button(self.btnFrame, text="Browse", command=self.browse_files)
        self.button_explore.grid(row=0, column=1, padx=10, pady=2)

        self.button_exit = Button(self.btnFrame, text="Close", command=self.end_mainloop)
        self.button_exit.grid(row=0, column=2, padx=10, pady=2)

        Label(self.rightFrame, text="Result:").grid(row=3, column=0, padx=10, pady=2)

        self.cur_lp = NONE
        self.masked_lp = NONE

        # Root mainloop
        self.root.mainloop()

    def browse_files(self):
        file_types = (("Image files", ".jpeg .jpg .png"), ("All files", "*.*"))
        filename = filedialog.askopenfilename(initialdir=self.last_dir, title="Select a File", filetypes=file_types)
        self.last_dir = os.path.dirname(filename)
        if self.browse_entry.get() != "" and filename != "":
            self.browse_entry.delete(0, END)
        self.browse_entry.insert(0, filename)
        if os.path.exists(filename):
            self.left_image = resize_and_convert(filename)
            self.left_image_label.configure(image=self.left_image)

    def detect(self):
        image_path = self.browse_entry.get()
        self.cur_lp = LP(image_path)
        self.masked_lp = resize_and_convert(self.cur_lp.masked_image)
        self.right_image_label.configure(image=self.masked_lp)
        self.output_number.delete("1.0", END)
        if self.cur_lp.lp_valid:
            decision = self.cur_lp.get_lp_decision()
            self.output_number.insert("1.0", self.cur_lp.lp_num + decision[0])
            self.db.execute("INSERT INTO Decisions VALUES (\"%s\", \"%s\", %f)"
                            % (self.cur_lp.lp_num, decision[0], time.time()))
        else:
            self.output_number.insert("1.0", self.cur_lp.OCR_results['OCRExitMessage'])
            self.db.execute("INSERT INTO Decisions VALUES (\"%s\", \"%s\", %f)"
                            % (self.cur_lp.lp_num, "OCR ERROR", time.time()))

    def end_mainloop(self):
        self.root.destroy()


class LP:
    def __init__(self, path):
        self.image_path = path
        if os.path.isfile(self.image_path) and self.image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.original_image = cv2.imread(self.image_path)
            # self.resized_image = resize_and_convert(self.image_path)
            self.masked_image = LPD.mask_plate(self.image_path)
            self.OCR_results = OCR.get_lp_num(self.masked_image)
            self.lp_num = self.OCR_results['ParsedText'].replace(' ', '')
            self.lp_valid = not self.OCR_results['IsError']
            self.timestamp = time.time()
        else:
            print('File path does not exist or the file is in the wrong format')

    def get_ocr_results(self):
        pass

    def get_lp_decision(self):  # Returns (True if
        if len(self.lp_num) < 5:
            return 'Access Denied', 'Plate number too short'
        if self.lp_num.endswith(('6', 'G')):
            return 'Access Denied', 'Public transportation is unauthorized'
        elif any(c in self.lp_num for c in ['L', 'M']):
            return 'Access Denied', 'Military and law enforcement vehicles prohibited'
        elif not re.search('[a-zA-Z]', self.lp_num):
            return 'Access Denied', 'Plate number does not contain any letters'
        else:
            return 'Access Granted', '-'


def main():
    if os.path.isfile('test.db'):  # Check if previous DB exists and if so delete it
        os.remove('test.db')
    conn = sq.connect('test.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE Decisions (
    license_plate text,
    decision text,
    
    timestamp real
    )""")
    GUI(c)
    print('closing DB connection')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
