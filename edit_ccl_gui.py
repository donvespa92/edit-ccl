import tkinter as tk
from tkinter import filedialog
from tkinter.font import Font
from tkinter import messagebox
import pandas as pd
import math
import os

class MainApplication:
    def __init__(self,master):
        self.obj_types = ['Domain','Boundary','Domain Interface']
        self.font = Font(family="Arial", size=12)
        self.wdir = os.getcwd().replace('\\','/') 
        self.master = master
        self.ccl_orig = 'orig_setup.ccl'
        self.dom_names = []
        self.data = []
        self.fidx = []
        
        self.gui_set_frames()
        self.gui_set_entries()
        self.gui_set_buttons()
        self.gui_set_text()
        self.gui_set_optionmenu()
        self.gui_set_lb()
        self.gui_set_grid()

    def gui_set_frames(self):
        self.mainframe = tk.Frame(self.master)
        self.frame_entries = tk.Frame(self.mainframe,bd=2,relief='groove')
        self.frame_text = tk.Frame(self.mainframe,bd=2,relief='groove')

    def gui_set_entries(self):
        self.entry_inputfile = tk.Entry(self.frame_entries,font=self.font,width=50,state='disabled')
        self.label_filter_dom = tk.Label(
                self.frame_entries,
                text='Filter objects:',
                font=self.font)
        self.label_filter_text = tk.Label(
                self.frame_entries,
                text='Filter text:',
                font=self.font)
        self.label_name = tk.Label(
                self.frame_entries,
                text='Name',
                font=self.font)
        self.entry_search_obj = tk.Entry(self.frame_entries,font=self.font)
        self.entry_search_obj.bind("<KeyRelease>", self.filter_objs)
        self.entry_search_text = tk.Entry(self.frame_entries,font=self.font)
        self.entry_search_text.bind("<KeyRelease>", self.highlight_text)
          
    def gui_set_text(self):
        self.text_output = tk.Text(
                self.frame_text,
                height=20,
                width=60,
                state='disabled')
        self.scrollbar = tk.Scrollbar(self.frame_text)
        self.scrollbar.config(command=self.text_output.yview)
        self.text_output.config(yscrollcommand=self.scrollbar.set)

        
    def gui_set_lb(self):
        self.lb_scrollbar_x = tk.Scrollbar(self.frame_text,orient='horizontal')
        self.lb_scrollbar_y = tk.Scrollbar(self.frame_text)
        self.lb_objects = tk.Listbox(
                self.frame_text,
                height=20,
                width=30,
                selectmode='single',
                exportselection=False)
        self.lb_objects.bind("<<ListboxSelect>>",self.cmd_selection)
        self.lb_objects.config(xscrollcommand=self.lb_scrollbar_x.set)
        self.lb_objects.config(yscrollcommand=self.lb_scrollbar_y.set)
        self.lb_scrollbar_x.config(command=self.lb_objects.xview)
        self.lb_scrollbar_y.config(command=self.lb_objects.yview)
    
    def gui_set_buttons(self):
        self.button_selectfile = tk.Button(
                self.frame_entries,
                text='Select',
                font=self.font,
                command=self.cmd_selectfile)
        self.button_edit = tk.Button(
                self.frame_text,
                text='Edit',
                font=self.font,
                height=2,
                command=self.cmd_edit)
        self.button_save = tk.Button(
                self.frame_text,
                text='Save',
                font=self.font,
                height=2,
                command=self.cmd_save)
    
    def gui_set_optionmenu(self):
        self.label_optionmenu = tk.Label(
                self.frame_entries,
                text='Object type',
                font=self.font)
        self.obj_type = tk.StringVar(self.frame_entries)
        self.obj_type.set(self.obj_types[0])
        self.optionmenu_objects = tk.OptionMenu(
                self.frame_entries,
                self.obj_type,*self.obj_types)
        self.obj_type.trace('w',self.select_object_type)
        
    def gui_set_grid(self):
        self.mainframe.pack(fill='both',expand=1,padx=5,pady=5)
        self.mainframe.columnconfigure(1,weight=1)
        self.mainframe.columnconfigure(2,weight=1)
        
        self.frame_entries.pack(fill='x',padx=5,pady=5)   
        self.frame_entries.columnconfigure(1,weight=1)
        self.frame_entries.columnconfigure(2,weight=0)
        self.entry_inputfile.grid(row=1,column=1,sticky='NSEW',padx=5,pady=5)
        self.button_selectfile.grid(row=1,column=2,sticky='NSEW',padx=5,pady=5)
        self.label_filter_dom.grid(row=2,column=1,sticky='E',padx=5,pady=5)
        self.entry_search_obj.grid(row=2,column=2,sticky='NSEW',padx=5,pady=5)
        self.label_filter_text.grid(row=3,column=1,sticky='E',padx=5,pady=5)
        self.entry_search_text.grid(row=3,column=2,sticky='NSEW',padx=5,pady=5)
        self.label_optionmenu.grid(row=4,column=1,sticky='E',padx=5,pady=5)
        self.optionmenu_objects.grid(row=4,column=2,sticky='NSEW',padx=5,pady=5)
        
        self.frame_text.pack(fill='both',expand=1,padx=5,pady=5)
        self.frame_text.columnconfigure(1,weight=1)
        self.frame_text.columnconfigure(3,weight=1)
        self.frame_text.rowconfigure(1,weight=1)
        self.lb_objects.grid(row=1,column=1,sticky='NSEW')
        self.lb_scrollbar_x.grid(row=2,column=1,sticky='NSEW')
        self.lb_scrollbar_y.grid(row=1,column=2,sticky='NSEW')
        self.text_output.grid(row=1,column=3,sticky='NSEW')
        self.scrollbar.grid(row=1,column=4,sticky='NSEW')
        
        self.button_edit.grid(row=3,columnspan=5,sticky='NSEW',padx=5,pady=5)
        self.button_save.grid(row=4,columnspan=5,sticky='NSEW',padx=5,pady=5)
    
    def insert_text(self,text):
        self.text_output.config(state='normal')
        self.text_output.delete(1.0,'end')       
        for line in text:
            self.text_output.insert('end',line+"\n")
        self.text_output.config(state='disabled')
    
    def cmd_selection(self,event):
        self.filtered = []
        obj_name = self.lb_objects.get(self.lb_objects.curselection()[0])
        self.get_obj_data(name=obj_name,type=self.obj_type.get())
        self.text = self.text_output.get(1.0,'end').split('\n')
        self.filtered.append(obj_name)
                
    def cmd_selectfile(self):
        temp = tk.filedialog.askopenfilename(
                title='Choose a .def file',
                filetypes=(              
                        ("Solver input file", "*.def"),
                        ("All files", "*.*") ) )
        
        if temp:
            self.inputfile_path = temp
            self.inputfile_name = os.path.basename(self.inputfile_path)
            self.inputfile_dir_name = os.path.dirname(self.inputfile_path)
            
            self.entry_inputfile.config(state='normal')
            self.entry_inputfile.delete(0,'end')
            self.entry_inputfile.insert(0,self.inputfile_path)
            self.entry_inputfile.config(state='disabled')
            
            self.exportccl(self.inputfile_path)
            self.search_obj(self.obj_type.get())

    def cmd_edit(self):
        self.text_output.config(state='normal')
        return
    
    def cmd_save(self):
        self.create_new_setup()           
        output = open('D:/TMP/python/new_setup.ccl','w')
        for item in self.new_setup:
            output.write("%s\n" % item)
        output.close()
        self.text_output.config(state='disabled')
    
    def exportccl(self,inputfile):
        self.orig_setup = []
        
        if os.path.exists(self.ccl_orig):
            os.remove(self.ccl_orig)
        os.system('cfx5cmds -read -def '+inputfile+' -ccl '+self.ccl_orig);
        with open(self.ccl_orig) as fp:
            for line in fp:
                self.orig_setup.append(line.rstrip())                
    
    def filter_objs(self,event):
        if self.entry_search_obj.get():
            tag = self.entry_search_obj.get()
            self.lb_objects.delete(0,'end')
            objects = []
            for obj in self.objects:
                if (tag in obj or tag.upper() in obj or tag.lower() in obj):
                    self.lb_objects.insert('end',obj)
                    objects.append(obj)
        else:
            self.search_obj(self.obj_type.get())
        
    def select_object_type(self,*args):
        self.search_obj(self.obj_type.get())
    
    def search_obj(self,obj_type):
        self.objects = []
        if (obj_type=='Boundary'):
            for line in self.orig_setup:
                if (obj_type.upper()+':' in line and 'Side ' not in line):
                    self.objects.append(line.split(':')[1].lstrip(' ').rstrip(' '))
        else:
            for line in self.orig_setup:
                if (obj_type.upper()+':' in line):
                    self.objects.append(line.split(':')[1].lstrip(' ').rstrip(' '))
        self.lb_objects.delete(0,'end')
        for obj in self.objects:
            self.lb_objects.insert('end',obj+"\n")

    def get_obj_data(self,**options):
        obj_name = options.get('name').rstrip()
        obj_type = options.get('type')
        fidx = 0
        idx_parent = 0
        space = 0
        self.selection = []
        
        for idx,line in enumerate(self.orig_setup):
            if (obj_type.upper() in line and obj_name in line):
                fidx = idx+1
                space = len(line) - len(line.lstrip(' '))
                idx_parent = fidx
                self.selection.append('# '+'='*50)
                self.selection.append(line)
                self.filtered.append(line)
                break
 
        for idx,line in enumerate(self.orig_setup[idx_parent:]):
            sp = len(line) - len(line.lstrip(' '))
            if (sp == space and obj_type.upper() not in line):
                self.selection.append(line)
                break
            else:
                self.selection.append(line)
        self.insert_text(self.selection)

    def highlight_text(self,event):
        self.text_output.tag_remove('found', '1.0', 'end')
        tag = self.entry_search_text.get()
        fidx = []
        if tag:
            idx = '1.0'
            while 1:
                idx = self.text_output.search(tag, idx, nocase=1, stopindex='end')
                if not idx: break
                fidx.append(math.floor(float(idx)))
                lastidx = '%s+%dc' % (idx, len(tag))
                self.text_output.tag_add('found', idx, lastidx)
                idx = lastidx
            self.text_output.tag_config(
                    'found',
                    foreground='red',
                    background='yellow',
                    font='Courier 11 bold')
        else:
            self.text_output.yview_moveto(0)
        
        if fidx:
            self.text_output.yview_moveto(0)
            self.text_output.yview_scroll(fidx[0]-1,'units')
                       
def main():
    root = tk.Tk()
    root.title('Edit .ccl file')
    MainApplication(root)
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()
   
if __name__ == '__main__':
    main()