import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.tix as tix
import tkinter.messagebox as msgbox
import tkinter.filedialog as filedialog
from tkcalendar import DateEntry
from file_manager.core import app_config
from file_manager.core.api import make_db, write_new_config, publish_folder, update_config
from file_manager.core.config_manager.fs_operations import has_config
from file_manager.core.config_manager.models import Config
from file_manager.core.config_manager.config_rw import parse_config, get_attributes_only
from .helpers import path_is_parent

attr_vals = {
    'test': ('test1', 'test2', 't3'),
    'year': ('2015', '2016', '2017', '2018'),
    'city': ('MSK', 'SPB', 'SMR', 'EKB'),
    'theatre': ('Durova', 'Stasik', 'Bolshoy'),
    '1': ('2015', '2016', '2017', '2018'),
    '2': ('MSK', 'SPB', 'SMR', 'EKB'),
    '3': ('Durova', 'Stasik', 'Bolshoy'),
    '4': ('2015', '2016', '2017', '2018'),
    '5': ('MSK', 'SPB', 'SMR', 'EKB'),
    '6': ('Durova', 'Stasik', 'Bolshoy'),
    '7': ('2015', '2016', '2017', '2018'),
    '8': ('MSK', 'SPB', 'SMR', 'EKB'),
    '9': ('Durova', 'Stasik', 'Bolshoy'),
    '10': ('2015', '2016', '2017', '2018'),
    '12': ('MSK', 'SPB', 'SMR', 'EKB'),
    '13': ('Durova', 'Stasik', 'Bolshoy'),
}


class GUIApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(MainFrame)
        make_db()

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one"""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(expand=True, fill='both')


class MainFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.geometry('800x800')
        self.master.resizable(False, False)
        self.master.title('File Manager')
        # self.pack(expand=True, fill='both')
        self.create_widgets()

    def create_widgets(self):
        self.grid_rowconfigure(0, weight=33)
        self.grid_rowconfigure(1, weight=33)
        self.grid_rowconfigure(2, weight=33)
        self.grid_columnconfigure(0, weight=50)
        self.grid_columnconfigure(1, weight=50)
        btn_settings = ttk.Button(self, text='Settings',
                                  command=lambda: self.master.switch_frame(SettingsFrame)).\
            grid(row=0, column=0, padx=15, pady=15, sticky='nswe')
        btn_copy = ttk.Button(self, text='Copy To \nFile Manager\n Or Create New Folder',
                              command=lambda: self.master.switch_frame(CopyFrame)).\
            grid(row=0, column=1, padx=15, pady=15, sticky='nswe')
        btn_search = ttk.Button(self, text='Search Folder',
                                command=lambda: self.master.switch_frame(SearchFrame)).\
            grid(row=1, column=0, padx=15, pady=15, sticky='nswe')
        btn_edit = ttk.Button(self, text='   Edit Folder \nConfiguration',
                              command=lambda: self.master.switch_frame(EditFrame)).\
            grid(row=1, column=1, padx=15, pady=15, sticky='nswe')
        btn_quit = ttk.Button(self, text='Quit',
                              command=lambda: sys.exit()).\
            grid(row=2, column=0, columnspan=2,
                 padx=15, pady=15, sticky='nswe')


class SettingsFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.geometry('800x800')
        self.master.resizable(False, False)
        self.master.title('Copy')
        self.pack(expand=True, fill='both')
        self.create_widgets()

    def create_widgets(self):
        pass


class CopyFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.geometry('800x800')
        self.master.resizable(False, False)
        self.master.title('Copy')
        self.set_variables()
        self.create_widgets()

    def set_variables(self):
        # initialize variables
        self.path_from = ''
        self.from_dirname = ''
        self.path_to = ''
        self.rel_path_to = ''
        self.config = None
        self.parent_attrs = {}
        self.parent_chkbtn_vars = {}
        self.folder_attrs = {}

    def create_widgets(self):
        # configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=100)

        # CREATE PATH CONTAINER
        self.path_ct = tk.LabelFrame(self, text='Copy:')
        self.path_ct.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.path_ct.grid_columnconfigure(1, weight=100)
        # create labels
        ttk.Label(self.path_ct, text='From:').\
            grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.path_ct, text='To:').\
            grid(row=1, column=0, padx=5, pady=5, sticky='w')
        # create buttons
        self.btn_from = ttk.Button(self.path_ct, text='Choose Path',
                                   command=self.ask_dir_from)
        self.btn_from.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.btn_to = ttk.Button(self.path_ct, text='Choose Path',
                                 command=self.ask_dir_to)
        self.btn_to.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # CREATE FOLDER INFO CONTAINER
        self.info_ct = tk.LabelFrame(self, text='Folder Information:')
        self.info_ct.grid_columnconfigure(1, weight=100)
        self.info_ct.grid_rowconfigure(6, weight=100)
        self.info_ct.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        # create labels
        ttk.Label(self.info_ct, text='Name:').\
            grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.info_ct, text='Path:').\
            grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.info_ct, text='Date:').\
            grid(row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.info_ct, text='Version:').\
            grid(row=3, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.info_ct, text='Comment:').\
            grid(row=4, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.info_ct, text='Attributes:').\
            grid(row=5, column=0, padx=5, pady=5, sticky='w')
        # create entry fields and dynamic label for path
        self.entry_name = ttk.Entry(self.info_ct)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.lbl_path = ttk.Label(self.info_ct, text='PATH IS NOT SELECTED')
        self.lbl_path.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.entry_date = DateEntry(self.info_ct)
        self.entry_date.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.entry_ver = ttk.Entry(self.info_ct)
        self.entry_ver.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.entry_ver.insert('end', '0')
        self.comment_text = tk.Text(self.info_ct, height=4)
        self.comment_text.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        # create a scrollable frame for attributes
        self.canvas1 = tk.Canvas(self.info_ct)
        self.scrollable_frame1 = tk.Frame(self.canvas1)
        self.vsb1 = tk.Scrollbar(self.info_ct,
                                 orient='vertical', command=self.canvas1.yview)
        self.canvas1.configure(yscrollcommand=self.vsb1.set)

        self.canvas1.grid(row=6, column=0, columnspan=2, sticky='nswe')
        self.vsb1.grid(row=6, column=3, sticky='ns')
        self.canvas1.create_window((0, 0),
                                   window=self.scrollable_frame1, anchor='nw')
        self.scrollable_frame1.bind('<Configure>', self.on_frame_configure1)

        # CREATE ATTRIBUTE CHOOSE CONTAINER
        self.attr_ct = tk.LabelFrame(self, text='Add Attributes:')
        self.attr_ct.grid(row=0, column=1, rowspan=2,
                          padx=5, pady=5, sticky='nsew')
        self.attr_ct.columnconfigure(0, weight=40)
        self.attr_ct.columnconfigure(1, weight=40)
        self.attr_ct.columnconfigure(2, weight=20)
        self.attr_ct.rowconfigure(0, weight=100)
        self.canvas2 = tk.Canvas(self.attr_ct)
        self.scrollable_frame2 = tk.Frame(self.canvas2)
        self.vsb2 = tk.Scrollbar(self.attr_ct,
                                 orient='vertical', command=self.canvas2.yview)
        self.canvas2.configure(yscrollcommand=self.vsb2.set)

        self.canvas2.grid(row=0, column=0, columnspan=3, sticky='nswe')
        self.vsb2.grid(row=0, column=3, sticky='ns')
        self.canvas2.create_window((0, 0),
                                   window=self.scrollable_frame2, anchor='nw')
        self.scrollable_frame2.bind('<Configure>', self.on_frame_configure2)
        self.draw_parent_attrs()
        self.category = tk.StringVar(self)
        self.choose_cat = ttk.OptionMenu(self.attr_ct,
                                         self.category, *attr_vals.keys())
        self.choose_cat.grid(row=1, column=0, pady=5, sticky='ew')
        self.entry_value = ttk.Entry(self.attr_ct)
        self.entry_value.grid(row=1, column=1, pady=5, sticky='ew')
        self.btn_add = ttk.Button(self.attr_ct, text='Add',
                                  command=self.add_attr)
        self.btn_add.grid(row=1, column=2, pady=5, sticky='ew')
        # self.btn_add['command'] = self.add_attr

        # CREATE CONTROL BUTTONS CONTAINER
        self.buttons_ct = tk.Frame(self)
        self.buttons_ct.grid_configure(row=2, column=0, columnspan=2,
                                       padx=5, pady=5, sticky='nsew')
        self.btn_back = ttk.Button(self.buttons_ct, text='Back',
                                   command=lambda: self.master.switch_frame(MainFrame))
        self.btn_back.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.btn_copy = ttk.Button(self.buttons_ct, text='Copy',
                                   command=self.copy_folder)
        self.btn_copy.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.btn_create = ttk.Button(self.buttons_ct, text='Create',
                                     command=self.create_folder_config)
        self.btn_create.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    def on_frame_configure1(self, e):
        self.canvas1.configure(scrollregion=self.canvas1.bbox('all'))

    def on_frame_configure2(self, e):
        self.canvas2.configure(scrollregion=self.canvas2.bbox('all'))

    def draw_parent_attrs(self):
        self.checkbutton_variables = {}
        for child in self.scrollable_frame2.winfo_children():
            child.destroy()
        row = 0
        for attr, values in self.parent_attrs.items():
            ttk.Label(self.scrollable_frame2, text=attr + ":").\
                grid(row=row, column=0, sticky='w')
            row += 1
            if values:
                for v in sorted(values):
                    key = (attr, v)
                    checkVar = tk.IntVar()
                    self.parent_chkbtn_vars[key] = checkVar
                    if v in self.folder_attrs.get(attr, set()):
                        checkVar.set(1)
                    else:
                        checkVar.set(0)
                    chckbtn = ttk.Checkbutton(
                        self.scrollable_frame2, text=v, variable=checkVar)
                    chckbtn['command'] = lambda var = checkVar, attr=attr, val=v: self.parent_attribute_checked(
                        var, attr, val)
                    chckbtn.grid(row=row, column=1, sticky='w')
                    row += 1

    def draw_folder_attrs(self):
        for child in self.scrollable_frame1.winfo_children():
            child.destroy()
        row = 0
        for attr, values in self.folder_attrs.items():
            ttk.Label(self.scrollable_frame1, text=attr + ":", border=4).\
                grid(row=row, column=0, sticky='w')
            row += 1
            if values:
                for v in sorted(values):
                    ttk.Label(self.scrollable_frame1, text=v).\
                        grid(row=row, column=1, sticky='w')
                    remove_btn = tk.Button(self.scrollable_frame1,
                                           text='X', bg='red')
                    remove_btn['command'] = lambda attr=attr, val=v: self.remove_attr(
                        attr, val)
                    remove_btn.grid(row=row, column=0, sticky='e', padx=5)
                    row += 1

    def ask_dir_from(self):
        initial_dir = os.environ['HOMEPATH'] if self.path_from == '' else self.path_from
        path = filedialog.askdirectory(initialdir=initial_dir)
        if path:
            if path_is_parent(app_config.ROOT_PATH, path):
                msgbox.showerror(
                    'ERROR', f'"From:" folder must be outside root directory: {app_config.ROOT_PATH}')
                return
            self.from_dirname = os.path.basename(os.path.normpath(path))
            print('DIRNAME: ' + self.from_dirname)
            self.entry_name.delete(0, 'end')
            self.entry_name.insert('end', self.from_dirname)
            self.path_from = path
            self.btn_from.configure(text=self.path_from)

    def ask_dir_to(self):
        initial_dir = app_config.ROOT_PATH if self.path_to == '' else self.path_to
        path = filedialog.askdirectory(initialdir=initial_dir)
        if path:
            if not path_is_parent(app_config.ROOT_PATH, path):
                msgbox.showerror(
                    'ERROR', f'"To:" folder must be inside root directory: {app_config.ROOT_PATH}')
                return
            self.path_to = path
            self.rel_path_to = os.path.relpath(self.path_to, app_config.ROOT_PATH)
            self.lbl_path.configure(text=self.rel_path_to)
            self.btn_to.configure(text=self.path_to)
            self.parent_attrs = get_attributes_only(self.rel_path_to, {})
            self.draw_parent_attrs()

    def parent_attribute_checked(self, chk, attr, val):
        if chk.get() == 1:
            if attr not in self.folder_attrs:
                self.folder_attrs[attr] = set()
            self.folder_attrs[attr].add(val)
        else:
            self.folder_attrs[attr].discard(val)
            if len(self.folder_attrs[attr]) == 0:
                self.folder_attrs.pop(attr)
        self.draw_folder_attrs()

    def add_attr(self):
        attr = self.category.get()
        val = self.entry_value.get().strip()
        if val == '':
            return
        if attr not in self.folder_attrs:
            self.folder_attrs[attr] = set()
        self.folder_attrs[attr].add(val)
        if (attr, val) in self.parent_chkbtn_vars:
            self.parent_chkbtn_vars[(attr, val)].set(1)
        self.draw_folder_attrs()

    def remove_attr(self, attr, val):
        if (attr, val) in self.parent_chkbtn_vars:
            self.parent_chkbtn_vars[(attr, val)].set(0)
        self.folder_attrs[attr].discard(val)
        if len(self.folder_attrs[attr]) == 0:
            self.folder_attrs.pop(attr)
        self.draw_folder_attrs()

    def create_folder_config(self):
        if self.path_from:
            msgbox.showerror(
                'ERROR', 'You hawe already selected "From" folder. You can only copy this folder now.')
            return
        if has_config(self.rel_path_to):
            msgbox.showerror(
                'ERROR', 'Can not create config file in this directory. It already has one.')
            return
        cfg = self.create_config()
        if cfg == None:
            msgbox.showerror(
                'ERROR', 'Please fill in all fields.')
            return
        write_new_config(cfg)

    def copy_folder(self):
        cfg = self.create_config()
        if cfg == None:
            msgbox.showerror(
                'ERROR', 'Please fill in all fields.')
            return
        try:
            publish_folder(self.path_from, self.path_to, cfg)
        except Exception as err:
            msgbox.showerror('ERROR', err)

    def create_config(self):
        if self.from_dirname:
            self.path_to = os.path.join(
                self.path_to, self.from_dirname)
            self.rel_path_to = os.path.relpath(self.path_to, app_config.ROOT_PATH)
        name = self.entry_name.get().strip()
        date = self.entry_date.get_date()
        ver = self.entry_ver.get().strip()
        path = self.rel_path_to
        attrs = self.folder_attrs
        spec = {'comment': self.comment_text.get('1.0', 'end-1c')}
        if name == '' or ver == '' or path == '':
            return None
        cfg = Config(name, date, ver, path, attributes=attrs, special=spec)
        return cfg

class EditFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.geometry('800x800')
        self.master.resizable(False, False)
        self.master.title('Copy')
        self.set_variables()
        self.create_widgets()

    def set_variables(self):
        # initialize variables
        self.path = ''
        self.rel_path = ''
        self.config = None
        self.parent_attrs = {}
        self.parent_chkbtn_vars = {}
        self.folder_attrs = {}

    def create_widgets(self):
        # configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=100)

        # CREATE PATH CONTAINER
        self.path_ct = tk.LabelFrame(self, text='Copy:')
        self.path_ct.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.path_ct.grid_columnconfigure(1, weight=100)
        # create labels
        ttk.Label(self.path_ct, text='Folder:').\
            grid(row=0, column=0, padx=5, pady=5, sticky='w')
        # create buttons
        self.btn_folder = ttk.Button(self.path_ct, text='Choose Path',
                                   command=self.ask_dir)
        self.btn_folder.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # CREATE FOLDER INFO CONTAINER
        self.info_ct = tk.LabelFrame(self, text='Folder Information:')
        self.info_ct.grid_columnconfigure(1, weight=100)
        self.info_ct.grid_rowconfigure(6, weight=100)
        self.info_ct.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        # create labels
        ttk.Label(self.info_ct, text='Name:').\
            grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.info_ct, text='Path:').\
            grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.info_ct, text='Date:').\
            grid(row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.info_ct, text='Version:').\
            grid(row=3, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.info_ct, text='Comment:').\
            grid(row=4, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self.info_ct, text='Attributes:').\
            grid(row=5, column=0, padx=5, pady=5, sticky='w')
        # create entry fields and dynamic label for path
        self.entry_name = ttk.Entry(self.info_ct)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.lbl_path = ttk.Label(self.info_ct, text='PATH IS NOT SELECTED')
        self.lbl_path.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.entry_date = DateEntry(self.info_ct)
        self.entry_date.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.entry_ver = ttk.Entry(self.info_ct)
        self.entry_ver.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.entry_ver.insert('end', '0')
        self.comment_text = tk.Text(self.info_ct, height=4)
        self.comment_text.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        # create a scrollable frame for attributes
        self.canvas1 = tk.Canvas(self.info_ct)
        self.scrollable_frame1 = tk.Frame(self.canvas1)
        self.vsb1 = tk.Scrollbar(self.info_ct,
                                 orient='vertical', command=self.canvas1.yview)
        self.canvas1.configure(yscrollcommand=self.vsb1.set)

        self.canvas1.grid(row=6, column=0, columnspan=2, sticky='nswe')
        self.vsb1.grid(row=6, column=3, sticky='ns')
        self.canvas1.create_window((0, 0),
                                   window=self.scrollable_frame1, anchor='nw')
        self.scrollable_frame1.bind('<Configure>', self.on_frame_configure1)

        # CREATE ATTRIBUTE CHOOSE CONTAINER
        self.attr_ct = tk.LabelFrame(self, text='Add Attributes:')
        self.attr_ct.grid(row=0, column=1, rowspan=2,
                          padx=5, pady=5, sticky='nsew')
        self.attr_ct.columnconfigure(0, weight=40)
        self.attr_ct.columnconfigure(1, weight=40)
        self.attr_ct.columnconfigure(2, weight=20)
        self.attr_ct.rowconfigure(0, weight=100)
        self.canvas2 = tk.Canvas(self.attr_ct)
        self.scrollable_frame2 = tk.Frame(self.canvas2)
        self.vsb2 = tk.Scrollbar(self.attr_ct,
                                 orient='vertical', command=self.canvas2.yview)
        self.canvas2.configure(yscrollcommand=self.vsb2.set)

        self.canvas2.grid(row=0, column=0, columnspan=3, sticky='nswe')
        self.vsb2.grid(row=0, column=3, sticky='ns')
        self.canvas2.create_window((0, 0),
                                   window=self.scrollable_frame2, anchor='nw')
        self.scrollable_frame2.bind('<Configure>', self.on_frame_configure2)
        self.draw_parent_attrs()
        self.category = tk.StringVar(self)
        self.choose_cat = ttk.OptionMenu(self.attr_ct,
                                         self.category, *attr_vals.keys())
        self.choose_cat.grid(row=1, column=0, pady=5, sticky='ew')
        self.entry_value = ttk.Entry(self.attr_ct)
        self.entry_value.grid(row=1, column=1, pady=5, sticky='ew')
        self.btn_add = ttk.Button(self.attr_ct, text='Add',
                                  command=self.add_attr)
        self.btn_add.grid(row=1, column=2, pady=5, sticky='ew')
        # self.btn_add['command'] = self.add_attr

        # CREATE CONTROL BUTTONS CONTAINER
        self.buttons_ct = tk.Frame(self)
        self.buttons_ct.grid_configure(row=2, column=0, columnspan=2,
                                       padx=5, pady=5, sticky='nsew')
        self.btn_back = ttk.Button(self.buttons_ct, text='Back',
                                   command=lambda: self.master.switch_frame(MainFrame))
        self.btn_back.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.btn_save = ttk.Button(self.buttons_ct, text='Save',
                                   command=self.save_config)
        self.btn_save.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    def on_frame_configure1(self, e):
        self.canvas1.configure(scrollregion=self.canvas1.bbox('all'))

    def on_frame_configure2(self, e):
        self.canvas2.configure(scrollregion=self.canvas2.bbox('all'))

    def draw_parent_attrs(self):
        self.checkbutton_variables = {}
        for child in self.scrollable_frame2.winfo_children():
            child.destroy()
        row = 0
        for attr, values in self.parent_attrs.items():
            ttk.Label(self.scrollable_frame2, text=attr + ":").\
                grid(row=row, column=0, sticky='w')
            row += 1
            if values:
                for v in sorted(values):
                    key = (attr, v)
                    checkVar = tk.IntVar()
                    self.parent_chkbtn_vars[key] = checkVar
                    if v in self.folder_attrs.get(attr, set()):
                        checkVar.set(1)
                    else:
                        checkVar.set(0)
                    chckbtn = ttk.Checkbutton(
                        self.scrollable_frame2, text=v, variable=checkVar)
                    chckbtn['command'] = lambda var = checkVar, attr=attr, val=v: self.parent_attribute_checked(
                        var, attr, val)
                    chckbtn.grid(row=row, column=1, sticky='w')
                    row += 1

    def draw_folder_attrs(self):
        for child in self.scrollable_frame1.winfo_children():
            child.destroy()
        row = 0
        if self.folder_attrs == None:
            return
        for attr, values in self.folder_attrs.items():
            ttk.Label(self.scrollable_frame1, text=attr + ":", border=4).\
                grid(row=row, column=0, sticky='w')
            row += 1
            if values:
                for v in sorted(values):
                    ttk.Label(self.scrollable_frame1, text=v).\
                        grid(row=row, column=1, sticky='w')
                    remove_btn = tk.Button(self.scrollable_frame1,
                                           text='X', bg='red')
                    remove_btn['command'] = lambda attr=attr, val=v: self.remove_attr(
                        attr, val)
                    remove_btn.grid(row=row, column=0, sticky='e', padx=5)
                    row += 1

    def ask_dir(self):
        initial_dir = app_config.ROOT_PATH if self.path == '' else self.path
        path = filedialog.askdirectory(initialdir=initial_dir)
        if path:
            if not path_is_parent(app_config.ROOT_PATH, path):
                msgbox.showerror(
                    'ERROR', f'"Folder must be inside root directory: {app_config.ROOT_PATH}')
                return
            self.path = path
            self.rel_path = os.path.relpath(self.path, app_config.ROOT_PATH)
            self.lbl_path.configure(text=self.rel_path)
            self.btn_folder.configure(text=self.path)
            self.parent_attrs = get_attributes_only(self.rel_path, {})
            self.config = parse_config(self.rel_path)
            print(self.config)
            self.entry_name.delete(0, 'end')
            if self.config.ver:
                self.entry_name.insert('end', self.config.name)
            else:
                self.entry_name.insert('end', os.path.basename(os.path.normpath(path)))
            self.entry_ver.delete(0, 'end')
            if self.config.ver:
                self.entry_ver.insert('end', self.config.ver)
            else:
                self.entry_ver.insert('end', '0')
            self.entry_date.set_date(self.config.date)
            self.folder_attrs = self.config.attributes
            self.draw_folder_attrs()
            self.draw_parent_attrs()

    def parent_attribute_checked(self, chk, attr, val):
        if chk.get() == 1:
            if attr not in self.folder_attrs:
                self.folder_attrs[attr] = set()
            self.folder_attrs[attr].add(val)
        else:
            self.folder_attrs[attr].discard(val)
            if len(self.folder_attrs[attr]) == 0:
                self.folder_attrs.pop(attr)
        self.draw_folder_attrs()

    def add_attr(self):
        if self.config == None or self.folder_attrs == None:
            return
        attr = self.category.get()
        val = self.entry_value.get().strip()
        if val == '':
            return
        if attr not in self.folder_attrs:
            self.folder_attrs[attr] = set()
        self.folder_attrs[attr].add(val)
        if (attr, val) in self.parent_chkbtn_vars:
            self.parent_chkbtn_vars[(attr, val)].set(1)
        self.draw_folder_attrs()

    def remove_attr(self, attr, val):
        if (attr, val) in self.parent_chkbtn_vars:
            self.parent_chkbtn_vars[(attr, val)].set(0)
        self.folder_attrs[attr].discard(val)
        if len(self.folder_attrs[attr]) == 0:
            self.folder_attrs.pop(attr)
        self.draw_folder_attrs()

    def save_config(self):
        if self.config == None:
            msgbox.showerror(
                'ERROR', 'Choose folder first.')
            return
        self.update_config()
        if self.config.name == '' or self.config.ver == '' or self.config.path == '':
            msgbox.showerror(
                'ERROR', 'Fill in all fields first.')
            return
        if self.config.id == None:
            self.config.id = write_new_config(self.config)
        else:
            update_config(self.config)


    def update_config(self):
        self.config.name = self.entry_name.get().strip()
        self.config.date = self.entry_date.get_date()
        self.config.ver = self.entry_ver.get().strip()
        self.config.path = self.rel_path
        self.config.attributes = self.folder_attrs
        self.config.special = {'comment': self.comment_text.get('1.0', 'end-1c')}

class SearchFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.geometry('800x800')
        self.master.resizable(False, False)
        self.master.title('Copy')
        self.pack(expand=True, fill='both')
        self.create_widgets()

    def create_widgets(self):
        pass


def run_app():
    root = tk.Tk()
    app = MainFrame(root)
    root.mainloop()
