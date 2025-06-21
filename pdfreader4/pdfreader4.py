#!/usr/bin/env python3

# V. 0.3

import os,sys,shutil,time
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, Gio, GLib, GObject, Pango
from gi.repository import GdkPixbuf
gi.require_version('Poppler', '0.18')
from gi.repository import Poppler
import json

CAIRO_AVAILABLE = 0
try:
    import cairo
    CAIRO_AVAILABLE = 1
except:
    CAIRO_AVAILABLE = 0


# this program directory
curr_dir = os.getcwd()

settings_conf_file = os.path.join(curr_dir, "config.json")
settings_conf = None
try:
    _ff = open(settings_conf_file, "r")
    settings_conf = json.load(_ff)
    _ff.close()
except:
    print("Config file error.")
    sys.exit()

# toolbar icon size
ICON_SIZE = settings_conf["iconsize"]
# paper colour - r/g/b range 0 - 65535
PAPER_COLOR = settings_conf["paper_color"]
# text highlight foreground colour
TEXT_HIGHLIGHT_F_COLOR = settings_conf["text_hf_color"]
# text highlight background colour
TEXT_HIGHLIGHT_B_COLOR = settings_conf["text_hb_color"]
# annotation colour
ANNOT_COLOR = settings_conf["annot_color"]
# drawing widget background_colour
DA_BACK_COLOR = settings_conf["da_b_color"]
# window size - empty for automatic measuring and setting
WINDOW_SIZE = settings_conf["window_size"]

## paper color
# default white
_p_r = 1.0
_p_g = 1.0
_p_b = 1.0
#
if PAPER_COLOR:
    _p_r, _p_g, _p_b = [float(el)/65535 for el in PAPER_COLOR.split("/")]
    
## text colour
# default black
_t_hf_r = 0
_t_hf_g = 0
_t_hf_b = 0
if TEXT_HIGHLIGHT_F_COLOR:
    _t_hf_r,_t_hf_g,_t_hf_b = [int(el) for el in TEXT_HIGHLIGHT_F_COLOR.split("/")]

## background_color
# default light green
_t_hb_r = 0
_t_hb_g = 55000
_t_hb_b = 0
if TEXT_HIGHLIGHT_B_COLOR:
    _t_hb_r,_t_hb_g,_t_hb_b = [int(el) for el in TEXT_HIGHLIGHT_B_COLOR.split("/")]

## annotation colour
# default yellowish
_a_c_a = 1.0
_a_c_r = 1.0
_a_c_g = 0.91
_a_c_b = 0.61
if ANNOT_COLOR:
    _a_c_r, _a_c_g, _a_c_b = [float(el)/65535 for el in ANNOT_COLOR.split("/")]

## drawing widget background colour
# default gray
if DA_BACK_COLOR:
    pass

##
WINW = 1000
WINH = 800
_window_size_manual = 0
if WINDOW_SIZE:
    try:
        WINW, WINH = [int(el) for el in WINDOW_SIZE.split("/")]
        _window_size_manual = 1
    except:
        _window_size_manual = 0
        WINW = 1000
        WINH = 800

if _window_size_manual == 0:
    try:
        conf_file = os.path.join(curr_dir, "conf.cfg")
        with open(conf_file, "r") as _f:
            WINW = int(_f.readline().strip("\n"))
            WINH = int(_f.readline().strip("\n"))
    except:
        WINW = 1000
        WINH = 800


def MyDialog(data1, data2, parent):
    dialog = Gtk.AlertDialog()
    dialog.set_message(data1)
    dialog.set_detail(data2)
    dialog.set_modal(True)
    dialog.set_buttons(["Close"])
    dialog.show(parent)

class winInfo(Gtk.Window):
    def __init__(self, _data):
        super().__init__()
        # _data = [_title,_subject,_author,_producer,_pdf_v,_creator,_cdt,_mdt]
        self._data = _data
        #
        self.main_box = Gtk.Box.new(1,0)
        self.set_child(self.main_box)
        #
        self.grid = Gtk.Grid.new()
        self.main_box.append(self.grid)
        #
        _lbl_title = Gtk.Label(label="Title: ")
        _lbl_title.set_halign(Gtk.Align.END)
        self.grid.attach(_lbl_title,0,0,1,1)
        _lbl_title2 = Gtk.Label(label=self._data[0])
        _lbl_title2.set_halign(Gtk.Align.START)
        self.grid.attach_next_to(_lbl_title2,_lbl_title,1,1,1)
        #
        _lbl_subject = Gtk.Label(label="Subject: ")
        _lbl_subject.set_halign(Gtk.Align.END)
        self.grid.attach(_lbl_subject,0,1,1,1)
        _lbl_subject2 = Gtk.Label(label=self._data[1])
        _lbl_subject2.set_halign(Gtk.Align.START)
        self.grid.attach_next_to(_lbl_subject2,_lbl_subject,1,1,1)
        #
        _lbl_author = Gtk.Label(label="Author: ")
        _lbl_author.set_halign(Gtk.Align.END)
        self.grid.attach(_lbl_author,0,2,1,1)
        _lbl_author2 = Gtk.Label(label=self._data[2])
        _lbl_author2.set_halign(Gtk.Align.START)
        self.grid.attach_next_to(_lbl_author2,_lbl_author,1,1,1)
        #
        _lbl_producer = Gtk.Label(label="Producer: ")
        _lbl_producer.set_halign(Gtk.Align.END)
        self.grid.attach(_lbl_producer,0,3,1,1)
        _lbl_producer2 = Gtk.Label(label=self._data[3])
        _lbl_producer2.set_halign(Gtk.Align.START)
        self.grid.attach_next_to(_lbl_producer2,_lbl_producer,1,1,1)
        #
        _lbl_pdfv = Gtk.Label(label="Pdf version: ")
        _lbl_pdfv.set_halign(Gtk.Align.END)
        self.grid.attach(_lbl_pdfv,0,4,1,1)
        _lbl_pdfv2 = Gtk.Label(label=self._data[4])
        _lbl_pdfv2.set_halign(Gtk.Align.START)
        self.grid.attach_next_to(_lbl_pdfv2,_lbl_pdfv,1,1,1)
        #
        _lbl_creator = Gtk.Label(label="Pdf creator: ")
        _lbl_creator.set_halign(Gtk.Align.END)
        self.grid.attach(_lbl_creator,0,5,1,1)
        _lbl_creator2 = Gtk.Label(label=self._data[5])
        _lbl_creator2.set_halign(Gtk.Align.START)
        self.grid.attach_next_to(_lbl_creator2,_lbl_creator,1,1,1)
        #
        _lbl_cd = Gtk.Label(label="Creation date: ")
        _lbl_cd.set_halign(Gtk.Align.END)
        self.grid.attach(_lbl_cd,0,6,1,1)
        _lbl_cd2 = Gtk.Label(label=self._data[6])
        _lbl_cd2.set_halign(Gtk.Align.START)
        self.grid.attach_next_to(_lbl_cd2,_lbl_cd,1,1,1)
        #
        _lbl_md = Gtk.Label(label="Modification date: ")
        _lbl_md.set_halign(Gtk.Align.END)
        self.grid.attach(_lbl_md,0,7,1,1)
        _lbl_md2 = Gtk.Label(label=self._data[7])
        _lbl_md2.set_halign(Gtk.Align.START)
        self.grid.attach_next_to(_lbl_md2,_lbl_md,1,1,1)
        #
        _btn_close = Gtk.Button(label="Close")
        _btn_close.connect("clicked", lambda w:self.close())
        self.main_box.append(_btn_close)
        #
        self.present()


QUIT = 1
class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_title("Pdf Reader")
        #
        self.connect("destroy", self._to_close)
        self.connect("close-request", self._to_close)
        self.set_default_size(WINW, WINH)
        #
        self.main_box = Gtk.Box.new(1,0)
        self.set_child(self.main_box)
        #
        # tool box
        self.tbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.tbox.set_homogeneous(True)
        self.main_box.append(self.tbox)
        #
        _display = Gdk.Display.get_default()
        self._clipboard = _display.get_clipboard()
        # 
        self.start_left_paned_size = 200
        try:
            with open(os.path.join(curr_dir, "paned_size.cfg") , "r") as _f:
                self.start_left_paned_size = int(_f.read().strip("\n"))
        except:
            self.start_left_paned_size = 200
        #
        self.left_paned_size = 0
        #
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.main_box.append(self.notebook)
        #
        if len(sys.argv) > 1:
            _file = os.path.realpath(sys.argv[1])
            if os.path.exists(_file) and os.access(_file, os.R_OK):
                self.add_new_page(_file)
                
    def add_new_page(self, _file):
        pageBox = NewPage(_file, self)
        # the page label
        page_box = Gtk.Box.new(0,0)
        page_label = Gtk.Label(label=os.path.basename(_file))
        page_label.set_tooltip_text(_file)
        page_box.append(page_label)
        close_btn = Gtk.Button()
        close_btn.set_icon_name("close")
        close_btn.connect("clicked", self.on_close_btn)
        page_box.append(close_btn)
        self.notebook.append_page(pageBox, page_box)
        self.notebook.set_tab_reorderable(pageBox, True)
    
    def on_close_btn(self, btn):
        curr_page = self.notebook.get_current_page()
        if self.notebook.get_n_pages() > 1:
            self.notebook.remove_page(curr_page)
        elif self.notebook.get_n_pages() == 1:
            self._to_close()
    
    def _to_close(self, w=None, e=None):
        if self.left_paned_size > 10 and self.start_left_paned_size != self.left_paned_size:
            try:
                with open(os.path.join(curr_dir, "paned_size.cfg"), "w") as _f:
                    _f.write(str(self.left_paned_size))
            except:
                pass
        #
        try:
            if self.get_surface() != None:
                _W = self.get_surface().get_width()
                _H = self.get_surface().get_height()
                if _W != WINW or _H != WINH:
                    try:
                        with open(conf_file, "w") as _f:
                            _f.write("{}\n{}".format(_W,_H))
                    except:
                        pass
        except:
            pass
        #
        global QUIT
        QUIT = 0
        self.close()
    

class NewPage(Gtk.Box):
    def __init__(self, _file, window):
        super().__init__()
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._file = _file
        self.window = window
        #
        self.starting_zoom = 1.0
        self._zoom = 1.0
        self._zoom_has_been_rectified = 0
        # list [drawing_widget, cairo_context]
        self.list_cr = []
        # list [drawing_widget, page_height_of_all_pages]
        # each page width must multiply self._zoom_has_been_rectified
        self.list_da = []
        
        # text got from dragging to highlight the text
        self.dradding_text = ""
        # list of annotations found during dragging - list of gdk.rectangle
        self.list_r = []
        # the poppler render selection object
        self.render_selection = None
        # old selection - poppler rectangle
        self.old_selection = None
        # the selected text
        self.selected_text = ""
        
        # list of annotations: [page, list]
        self.list_annotations = []
        # annotation to remove
        self.annot_to_remove = None
        
        # list of the page text in form of poppler rectangles
        # one rectangle is one character
        self.list_page_text_rectangles = []
        
        self.paned_min_pos = 60
        self.paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.paned.connect("notify::position", self.on_paned_handle_moved)
        self.paned.set_wide_handle(False)
        
        self.add_index_section()
        
        # links mapping list - [poppler.page, [list of linkMapping]]
        self.list_links = []
        
        self.notebook_add_new_page(os.path.basename(self._file))
        self.add_page(self._file)
    
    def on_paned_handle_moved(self, paned, gparam):
        if self.paned.get_position() > WINW-self.paned_min_pos:
            self.paned.set_position(WINW-self.paned_min_pos)
            return
        elif self.paned.get_position() < self.paned_min_pos:
            self.paned.set_position(self.paned_min_pos)
            return
        self.window.left_paned_size = self.index_box.get_width()
    
    # paned left
    def add_index_section(self):
        self.index_box = Gtk.Box.new(1,0)
        self.paned.set_start_child(self.index_box)
        self.paned.set_position(self.window.start_left_paned_size)
        #
        _lbl_index = Gtk.Label(label="Index")
        self.index_box.append(_lbl_index)
        #
        self.index_scrollarea = Gtk.ScrolledWindow()
        self.index_box.append(self.index_scrollarea)
        self.index_scrollarea.set_hexpand(False)
        self.index_scrollarea.set_vexpand(True)
        self.index_scrollarea.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        self.index_scrollarea.set_placement(Gtk.CornerType.TOP_LEFT)
        #
        self.tree_view = Gtk.TreeView.new()
        self.tree_view.set_activate_on_single_click(True)
        self.tree_view.connect("row-activated", self.on_treeview_activated)
        self.tree_view.set_focusable(False)
        self.index_scrollarea.set_focusable(False)
        self.index_scrollarea.set_child(self.tree_view)
        #
        self.index_box.hide()
        #
        # index name - page number - index left position and index top position
        self.model = Gtk.TreeStore(str, int, int, int)
        self.tree_view.set_model(self.model)
        #
        column_index = Gtk.TreeViewColumn("Index")
        self.tree_view.append_column(column_index)
        renderer_text = Gtk.CellRendererText()
        column_index.pack_start(renderer_text, True)
        column_index.add_attribute(renderer_text, "text", 0)
        #
        column_page = Gtk.TreeViewColumn("Page")
        self.tree_view.append_column(column_page)
        renderer_text = Gtk.CellRendererText()
        column_page.pack_start(renderer_text, False)
        column_page.add_attribute(renderer_text, "text", 1)
        
    # scroll to the selected page or section
    def on_treeview_activated(self, tv, path, column):
        treeiter = self.model.get_iter(path)
        name = self.model.get_value(treeiter, 0)
        page = self.model.get_value(treeiter, 1)
        pos_left = self.model.get_value(treeiter, 2)
        pos_top = self.model.get_value(treeiter, 3)
        #
        ### find the page
        page_num = None
        page_left = 0
        page_top = 0
        for row in self.model:
            if row[1] == page:
                page_num = row[1]-1 # self.list_da indexes start from 0 
                page_left = row[2]
                page_top = row[3]
                break
        #
        if page_num != None:
            da_tmp = self.list_da[page_num]
            da = da_tmp[0]
            # the total height up to this page
            da_total_height = da_tmp[1]*self._zoom_has_been_rectified
            # this page drawing area height
            da_heigth = da.get_height()
            vadjustment = self.scrolledwindow.get_vadjustment()
            scroll_y = da_total_height-da_heigth+(self._pad_around_page*page_num)
            ret = 0
            if pos_top > 0:
                ret = self.calculate_pos_in_page(pos_top, da_heigth)
                vadjustment.set_value((scroll_y+ret))
            else:
                vadjustment.set_value((scroll_y))
        
    def on_change_page(self, btn, _p):
        adj = self.scrolledwindow.get_vadjustment()
        _value = adj.get_value()
        #
        curr_page = 0
        total_da_h = 0
        for i,el in enumerate(self.list_da):
            total_da_h += el[0].get_height()
            if total_da_h > _value:
                curr_page = i
                break
        #
        if 0 <= curr_page < self.doc.get_n_pages():
            if _p > 0:
                page_num = curr_page+1
            elif _p < 0:
                page_num = curr_page-1
            if page_num < 0:
                return
            if page_num == self.doc.get_n_pages():
                return
            da_tmp = self.list_da[page_num]
            da = da_tmp[0]
            # the total height up to this page
            da_total_height = da_tmp[1]*self._zoom_has_been_rectified
            # this page drawing area height
            da_heigth = da.get_height()
            vadjustment = self.scrolledwindow.get_vadjustment()
            scroll_y = da_total_height-da_heigth+(self._pad_around_page*page_num)
            vadjustment.set_value((scroll_y))
        
    # return the position in the page calculated from bottom
    def calculate_pos_in_page(self, _pos, da_heigth):
        return (da_heigth-_pos*self._zoom_has_been_rectified)
        
    def find_current_page(self):
        curr_page = 0
        curr_vscrollvalue = self.scrolledwindow.get_vadjustment().get_value()
        _prev_page = 0
        for el in self.list_da:
            if el[1] > curr_vscrollvalue:
                curr_page = _prev_page
                break
            else:
                _prev_page = el[0].n_page
        return curr_page
    
    def add_btn_image(self, btn, _name):
        btn_i = Gtk.Image.new_from_icon_name(_name)
        btn.set_child(btn_i)
        btn_i.set_pixel_size(ICON_SIZE)
    
    def notebook_add_new_page(self, _label):
        #### the pages
        # the box for the doc pages
        self.notebook_page_box = Gtk.Box.new(1,0)
        self.append(self.notebook_page_box)
        # the paned
        self.notebook_page_box.append(self.paned)
        #
        self.buttons_box = Gtk.Box.new(0,0)
        self.notebook_page_box.prepend(self.buttons_box)
        #
        ### infobar for removing annotations
        self.infobar_annot = Gtk.InfoBar.new()
        self.infobar_annot.set_show_close_button(True)
        _btn_annot = self.infobar_annot.add_button("Accept", 123)
        self.infobar_annot_lbl = Gtk.Label(label="")
        self.infobar_annot.add_child(self.infobar_annot_lbl)
        self.infobar_annot.connect("response", self.on_infobar_annot_btn)
        self.window.main_box.append(self.infobar_annot)
        self.infobar_annot.hide()
        #
        self.lateral_panel_btn = Gtk.ToggleButton()
        self.add_btn_image(self.lateral_panel_btn, "bookmark-new")
        self.lateral_panel_btn.set_active(False)
        self.lateral_panel_btn.connect("clicked", self.on_lateral_panel_btn)
        self.buttons_box.append(self.lateral_panel_btn)
        #
        self.open_btn = Gtk.Button.new()
        self.add_btn_image(self.open_btn, "document-open")
        self.open_btn.set_tooltip_text("Load a new document")
        self.open_btn.connect("clicked", self.on_open_document)
        self.buttons_box.append(self.open_btn)
        #
        self.reset_zoom_btn = Gtk.Button()
        self.add_btn_image(self.reset_zoom_btn, "zoom-fit-best")
        self.reset_zoom_btn.set_tooltip_text("Fit to window width")
        self.reset_zoom_btn.connect("clicked", self.on_reset_zoom_btn)
        self.buttons_box.append(self.reset_zoom_btn)
        #
        self.zoom_btn_p = Gtk.Button()
        self.add_btn_image(self.zoom_btn_p, "zoom-in")
        self.zoom_btn_p.set_tooltip_text("Zoom in")
        self.zoom_btn_p.connect("clicked", self.on_zoom_button, 0.2)
        self.buttons_box.append(self.zoom_btn_p)
        #
        self.zoom_btn_m = Gtk.Button()
        self.add_btn_image(self.zoom_btn_m, "zoom-out")
        self.zoom_btn_m.set_tooltip_text("Zoom out")
        self.zoom_btn_m.connect("clicked", self.on_zoom_button, -0.2)
        self.buttons_box.append(self.zoom_btn_m)
        #
        self.prev_page = Gtk.Button()
        self.add_btn_image(self.prev_page, "go-previous")
        self.prev_page.set_tooltip_text("Previous page")
        self.prev_page.connect("clicked", self.on_change_page, -1)
        self.buttons_box.append(self.prev_page)
        #
        self.next_page = Gtk.Button()
        self.add_btn_image(self.next_page, "go-next")
        self.next_page.set_tooltip_text("Next page")
        self.next_page.connect("clicked", self.on_change_page, 1)
        self.buttons_box.append(self.next_page)
        #
        # whether the cursor has changed
        self.cursor_changed_annot = False
        # annotation type
        self.annot_type = 0
        #
        self.annot_btn = Gtk.MenuButton()
        self.add_btn_image(self.annot_btn, "document-edit")
        self.annot_btn.set_tooltip_text("Annotations")
        self.buttons_box.append(self.annot_btn)
        # annotation colour dialog
        self.dlg_color = Gtk.ColorDialog.new()
        self.dlg_color.set_modal(self.window)
        self.dlg_color.set_with_alpha(True)
        self.color_btn = Gtk.ColorDialogButton.new(self.dlg_color)
        _rgba = Gdk.RGBA()
        _rgba.alpha = _a_c_a
        _rgba.red = _a_c_r
        _rgba.green = _a_c_g
        _rgba.blue = _a_c_b
        self.color_btn.set_rgba(_rgba)
        self.buttons_box.append(self.color_btn)
        #
        # text annotation
        self.menu_pop = Gtk.PopoverMenu()
        self.annot_btn.set_popover(self.menu_pop)
        #
        self._mmenu = Gio.Menu.new()
        self.menu_pop.set_menu_model(self._mmenu)
        #
        action_group = Gio.SimpleActionGroup()
        self.annot_btn.insert_action_group('menu', action_group)
        #
        item_t = Gio.MenuItem.new('Text annotation', 'menu.text')
        text_action = Gio.SimpleAction.new('text', None)
        text_action.set_enabled(True)
        text_action.activate(None)
        text_action.connect('activate', self.on_btn_annot_text, 1)
        self._mmenu.append_item(item_t)
        action_group.add_action(text_action)
        #
        # ["Text", "Highlight", "Strike", "Underline", "Squiggly"]
        # item_hl = Gio.MenuItem.new('Highlight', 'menu.highlight')
        # highlight_action = Gio.SimpleAction.new('highlight', None)
        # highlight_action.set_enabled(True)
        # highlight_action.activate(None)
        # highlight_action.connect('activate', self.on_btn_annot_text, 2)
        # self._mmenu.append_item(item_hl)
        # action_group.add_action(highlight_action)
        #
        item_sq = Gio.MenuItem.new('Square', 'menu.square')
        sq_action = Gio.SimpleAction.new('square', None)
        sq_action.set_enabled(True)
        sq_action.activate(None)
        sq_action.connect('activate', self.on_btn_annot_text, 3)
        self._mmenu.append_item(item_sq)
        action_group.add_action(sq_action)
        #
        item_cl = Gio.MenuItem.new('Cirlce', 'menu.circle')
        cl_action = Gio.SimpleAction.new('circle', None)
        cl_action.set_enabled(True)
        cl_action.activate(None)
        cl_action.connect('activate', self.on_btn_annot_text, 4)
        self._mmenu.append_item(item_cl)
        action_group.add_action(cl_action)
        #
        # item_ar = Gio.MenuItem.new('Arrow', 'menu.arrow')
        # ar_action = Gio.SimpleAction.new('arrow', None)
        # ar_action.set_enabled(True)
        # ar_action.activate(None)
        # ar_action.connect('activate', self.on_btn_annot_text, 6)
        # self._mmenu.append_item(item_ar)
        # action_group.add_action(ar_action)
        #
        item_ft = Gio.MenuItem.new('Free text', 'menu.ftext')
        ft_action = Gio.SimpleAction.new('ftext', None)
        ft_action.set_enabled(True)
        ft_action.activate(None)
        ft_action.connect('activate', self.on_btn_annot_text, 7)
        self._mmenu.append_item(item_ft)
        action_group.add_action(ft_action)
        #
        self.bmenu = Gio.Menu.new()
        self._mmenu.append_submenu("Stamp", self.bmenu)
        #
        item_st0 = Gio.MenuItem.new('Unknown', 'menu.stamp0')
        st_action0 = Gio.SimpleAction.new('stamp0', None)
        st_action0.set_enabled(True)
        st_action0.activate(None)
        st_action0.connect('activate', self.on_btn_annot_text, 50)
        self.bmenu.append_item(item_st0)
        action_group.add_action(st_action0)
        #
        item_st1 = Gio.MenuItem.new('Approved', 'menu.stamp1')
        st_action1 = Gio.SimpleAction.new('stamp1', None)
        st_action1.set_enabled(True)
        st_action1.activate(None)
        st_action1.connect('activate', self.on_btn_annot_text, 51)
        self.bmenu.append_item(item_st1)
        action_group.add_action(st_action1)
        #
        item_st2 = Gio.MenuItem.new('Departmental', 'menu.stamp2')
        st_action2 = Gio.SimpleAction.new('stamp2', None)
        st_action2.set_enabled(True)
        st_action2.activate(None)
        st_action2.connect('activate', self.on_btn_annot_text, 52)
        self.bmenu.append_item(item_st2)
        action_group.add_action(st_action2)
        #
        item_st3 = Gio.MenuItem.new('For comment', 'menu.stamp3')
        st_action3 = Gio.SimpleAction.new('stamp3', None)
        st_action3.set_enabled(True)
        st_action3.activate(None)
        st_action3.connect('activate', self.on_btn_annot_text, 53)
        self.bmenu.append_item(item_st3)
        action_group.add_action(st_action3)
        #
        item_st4 = Gio.MenuItem.new('For pubblic release', 'menu.stamp4')
        st_action4 = Gio.SimpleAction.new('stamp4', None)
        st_action4.set_enabled(True)
        st_action4.activate(None)
        st_action4.connect('activate', self.on_btn_annot_text, 54)
        self.bmenu.append_item(item_st4)
        action_group.add_action(st_action4)
        #
        item_st5 = Gio.MenuItem.new('Top secret', 'menu.stamp5')
        st_action5 = Gio.SimpleAction.new('stamp5', None)
        st_action5.set_enabled(True)
        st_action5.activate(None)
        st_action5.connect('activate', self.on_btn_annot_text, 55)
        self.bmenu.append_item(item_st5)
        action_group.add_action(st_action5)
        #
        item_st6 = Gio.MenuItem.new('None', 'menu.stamp6')
        st_action6 = Gio.SimpleAction.new('stamp6', None)
        st_action6.set_enabled(True)
        st_action6.activate(None)
        st_action6.connect('activate', self.on_btn_annot_text, 56)
        self.bmenu.append_item(item_st6)
        action_group.add_action(st_action6)
        #
        item_st7 = Gio.MenuItem.new('As is', 'menu.stamp7')
        st_action7 = Gio.SimpleAction.new('stamp7', None)
        st_action7.set_enabled(True)
        st_action7.activate(None)
        st_action7.connect('activate', self.on_btn_annot_text, 57)
        self.bmenu.append_item(item_st7)
        action_group.add_action(st_action7)
        #
        item_st8 = Gio.MenuItem.new('Confidential', 'menu.stamp8')
        st_action8 = Gio.SimpleAction.new('stamp8', None)
        st_action8.set_enabled(True)
        st_action8.activate(None)
        st_action8.connect('activate', self.on_btn_annot_text, 58)
        self.bmenu.append_item(item_st8)
        action_group.add_action(st_action8)
        #
        item_st9 = Gio.MenuItem.new('Final', 'menu.stamp9')
        st_action9 = Gio.SimpleAction.new('stamp9', None)
        st_action9.set_enabled(True)
        st_action9.activate(None)
        st_action9.connect('activate', self.on_btn_annot_text, 59)
        self.bmenu.append_item(item_st9)
        action_group.add_action(st_action9)
        #
        item_st10 = Gio.MenuItem.new('Experimental', 'menu.stamp10')
        st_action10 = Gio.SimpleAction.new('stamp10', None)
        st_action10.set_enabled(True)
        st_action10.activate(None)
        st_action10.connect('activate', self.on_btn_annot_text, 60)
        self.bmenu.append_item(item_st10)
        action_group.add_action(st_action10)
        #
        item_st11 = Gio.MenuItem.new('Expired', 'menu.stamp11')
        st_action11 = Gio.SimpleAction.new('stamp11', None)
        st_action11.set_enabled(True)
        st_action11.activate(None)
        st_action11.connect('activate', self.on_btn_annot_text, 61)
        self.bmenu.append_item(item_st11)
        action_group.add_action(st_action11)
        #
        item_st12 = Gio.MenuItem.new('Not approved', 'menu.stamp12')
        st_action12 = Gio.SimpleAction.new('stamp12', None)
        st_action12.set_enabled(True)
        st_action12.activate(None)
        st_action12.connect('activate', self.on_btn_annot_text, 62)
        self.bmenu.append_item(item_st12)
        action_group.add_action(st_action12)
        #
        item_st13 = Gio.MenuItem.new('Not for pubblic release', 'menu.stamp13')
        st_action13 = Gio.SimpleAction.new('stamp13', None)
        st_action13.set_enabled(True)
        st_action13.activate(None)
        st_action13.connect('activate', self.on_btn_annot_text, 63)
        self.bmenu.append_item(item_st13)
        action_group.add_action(st_action13)
        #
        item_st14 = Gio.MenuItem.new('Sold', 'menu.stamp14')
        st_action14 = Gio.SimpleAction.new('stamp14', None)
        st_action14.set_enabled(True)
        st_action14.activate(None)
        st_action14.connect('activate', self.on_btn_annot_text, 64)
        self.bmenu.append_item(item_st14)
        action_group.add_action(st_action14)
        #
        #
        if CAIRO_AVAILABLE == 1:
            item_st15 = Gio.MenuItem.new('Custom image', 'menu.stamp15')
            st_action15 = Gio.SimpleAction.new('stamp15', None)
            st_action15.set_enabled(True)
            st_action15.activate(None)
            st_action15.connect('activate', self.on_btn_annot_text, 65)
            self.bmenu.append_item(item_st15)
            action_group.add_action(st_action15)
        #
        self.border_width_cb = Gtk.ComboBoxText()
        self.border_width_cb.set_tooltip_text("Annotation border width")
        for el in ["1","2","3","4","5","6"]:
            self.border_width_cb.append_text(el)
        self.border_width_cb.set_active(0)
        self.buttons_box.append(self.border_width_cb)
        #
        self.search_entry = Gtk.SearchEntry()
        self.buttons_box.append(self.search_entry)
        # the text to search
        self.search_text = ""
        # [n_page , [_rects of the n_page]]
        self.search_in_page = []
        # the current rect in searching action
        self.current_rect = -1
        # the current page while searching
        self.current_page = -1
        # the rectangle of the word found
        self.search_rect = None
        #
        self.btn_search_p = Gtk.Button()
        self.add_btn_image(self.btn_search_p, "go-previous")
        self.btn_search_p.set_tooltip_text("Previous")
        self.btn_search_p.connect("clicked", self.on_search_btn, -1)
        self.buttons_box.append(self.btn_search_p)
        #
        self.btn_search_n = Gtk.Button()
        self.add_btn_image(self.btn_search_n, "go-next")
        self.btn_search_n.set_tooltip_text("Next")
        self.btn_search_n.connect("clicked", self.on_search_btn, 1)
        self.buttons_box.append(self.btn_search_n)
        #
        self.info_btn = Gtk.Button()
        self.add_btn_image(self.info_btn, "help")
        self.info_btn.set_tooltip_text("Document info")
        self.info_btn.connect("clicked", self.on_info)
        self.buttons_box.append(self.info_btn)
        #
        self.print_btn = Gtk.Button()
        self.add_btn_image(self.print_btn, "document-print")
        self.print_btn.set_tooltip_text("Print this document")
        self.print_btn.connect("clicked", self.on_print)
        self.buttons_box.append(self.print_btn)
        #
        self.save_btn = Gtk.Button()
        self.add_btn_image(self.save_btn, "document-save")
        self.save_btn.set_tooltip_text("Save this document")
        self.save_btn.connect("clicked", self.on_doc_save)
        self.buttons_box.append(self.save_btn)
        #
        self.save_as_btn = Gtk.Button()
        self.add_btn_image(self.save_as_btn, "document-save-as")
        self.save_as_btn.set_tooltip_text("Save this documet with a new name")
        self.save_as_btn.connect("clicked", self.on_save_as)
        self.buttons_box.append(self.save_as_btn)
        #
        self.exit_btn = Gtk.Button()
        self.add_btn_image(self.exit_btn, "window-close")
        self.exit_btn.set_tooltip_text("Close this program")
        self.exit_btn.connect("clicked", self.on_exit)
        self.buttons_box.append(self.exit_btn)
        #
        # scrolled window
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)
        self.scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.set_placement(Gtk.CornerType.TOP_LEFT)
        self.paned.set_end_child(self.scrolledwindow)
        self.hscrollbar = self.scrolledwindow.get_hscrollbar()
        self.vscrollbar = self.scrolledwindow.get_vscrollbar()
        #
        self.right_click_setted = 0
        ########
        # drawing area from which remove the annotation
        self.da_to_remove_from = None
        #
        ### infobar for password
        self.infobar_pw = Gtk.InfoBar.new()
        _btnpw = self.infobar_pw.add_button("Accept", 456)
        _btnpw2 = self.infobar_pw.add_button("Close", -1)
        self.infobar_pw_lbl = Gtk.Label(label="Password: ")
        self.infobar_pw.add_child(self.infobar_pw_lbl)
        self.infobar_pw_entry = Gtk.PasswordEntry()
        self.infobar_pw_entry.set_show_peek_icon(True)
        self.infobar_pw_entry.set_hexpand(True)
        self.infobar_pw.add_child(self.infobar_pw_entry)
        #
        self.infobar_pw.connect("response", self.on_infobar_pw_btn)
        self.window.main_box.append(self.infobar_pw)
        self.infobar_pw.hide()
        
    # _p : -1 previous 1 next
    def on_search_btn(self, btn, _p):
        # 
        if self.current_rect == -99:
            self.current_rect = -1
        #
        _text = self.search_entry.get_text()
        # minimum three characters to perform a query
        if len(_text) < 3:
            return
        #
        if _text != self.search_text:
            # the text to search
            self.search_text = _text
            # [n_page , [_rects]]
            self.search_in_page = []
            # the current rect in searching action: index
            self.current_rect = -1
            # the current page while searching
            self.current_page = -1
        #
        if _text == "":
            return
        # check if has been reached the end of the beginning of the document
        # _page = 0
        if self.current_page == -1:
            if _p == 1:
                # MyDialog("Info", "End of the searching.", self.window)
                _page = 0
                self.current_page = _page
            elif _p == -1:
                # MyDialog("Info", "End of the document.", self.window)
                _page = self.doc.get_n_pages()-1
                self.current_page = _page
        else:
            _page = self.current_page
        #
        self.search_in_page = []
        #
        page = self.doc.get_page(_page)
        #
        _rects2 = page.find_text(_text)
        #
        # options = Poppler.FindFlags.DEFAULT
        # _rects2 = page.find_text_with_options(_text, options)
        #
        # if _p == 1:
            # _rects = _rects2[::-1]
        # elif _p == -1:
            # _rects = _rects2[::-1]
        _rects = _rects2
        #
        if self.search_in_page == []:
            self.search_in_page = [_page,_rects]
            self.current_page = _page
        #
        # skip the page without the searching text in it
        if _rects == []:
            if _p == 1:
                n_pages = self.doc.get_n_pages()
                if self.current_page+1 < n_pages and n_pages > 1:
                    self.current_page += 1
                    self.search_in_page = []
                    self.current_rect = -1
                    self.on_search_btn(btn, _p)
                else:
                    if self.current_rect == -1:
                        MyDialog("Searching", "Nothing found", self.window)
                    self.current_page = 0
                    self.search_in_page = []
                    self.current_rect = -99
                    return
            elif _p == -1:
                n_pages = self.doc.get_n_pages()
                # if self.current_page == 0 and self.doc.get_n_pages() > 1:
                if self.current_page-1 < 0 and n_pages > 1:
                    self.current_page = self.doc.get_n_pages() - 1
                    self.search_in_page = []
                    self.current_rect = -1
                    self.on_search_btn(btn, _p)
                else:
                    if self.current_rect == -1:
                        MyDialog("Searching", "Nothing found", self.window)
                    self.current_page = 0
                    self.search_in_page = []
                    self.current_rect = -99
                    return
        #
        if self.current_rect == -99:
            return
        # scroll to top
        vadjustment = self.scrolledwindow.get_vadjustment()
        vadjustment.set_value(0)
        #
        if self.current_rect == -1:
            if _p == 1:
                _r = _rects[0]
                self.current_rect = 0
            elif _p == -1:
                _r = _rects[-1]
                self.current_rect = len(_rects)-1
        else:
            _r = _rects[self.current_rect]
        #
        y1 = _r.y1
        self.search_rect = _r
        #
        page_num = self.search_in_page[0]
        da_tmp = self.list_da[page_num]
        da = da_tmp[0]
        # the total height up to this page
        da_total_height = da_tmp[1]*self._zoom_has_been_rectified
        # this page drawing area height
        da_heigth = da.get_height()
        scroll_y = da_total_height-da_heigth+(self._pad_around_page*page_num)
        ret = da_heigth/self._zoom_has_been_rectified-y1
        vadjustment.set_value((scroll_y+ret))
        #
        ###
        # finding the new page and the new rectangle
        if _p == 1:
            if self.current_rect < len(_rects)-1:
                self.current_page = _page
                self.current_rect += 1
            else:
                n_pages = self.doc.get_n_pages()
                if n_pages-1 > _page:
                    self.current_page += 1
                else:
                    self.current_page = 0
                    self.search_in_page = []
                self.current_rect = -1
        elif _p == -1:
            if self.current_rect > 0:
                self.current_rect -= 1
                self.current_page = _page
            else:
                n_pages = self.doc.get_n_pages()
                if _page > 0:
                    self.current_page -= 1
                else:
                    self.current_page = n_pages-1
                    self.search_in_page = []
                self.current_rect = -1
        # apdate
        da.queue_draw()
        
    def on_exit(self, btn):
        self.window._to_close()
        
    def on_open_document(self, btn):
        file_dialog = Gtk.FileDialog()
        file_dialog.set_title("Choose a pdf file...")
        file_dialog.set_modal(True)
        file_dialog.set_initial_folder(Gio.File.new_for_path(os.path.expanduser("~")))
        file_dialog.open(self.window, None, self.on_document_get, None)
        
    def on_document_get(self, source_object, res, data):
        try:
            gfile = source_object.open_finish(res)
            _file = gfile.get_path()
            if os.path.exists(_file) and os.access(_file, os.R_OK):
                self.window.add_new_page(_file)
                self.window.notebook.set_current_page(self.window.notebook.get_n_pages()-1)
        except Exception as E:
            MyDialog("Error", str(E), self.window)
            
    def on_info(self, btn):
        _title = self.doc.get_title() or " "
        _subject = self.doc.get_subject() or " "
        _author = self.doc.get_author() or " "
        _producer = self.doc.get_producer() or " "
        _pdf_v = self.doc.get_pdf_version_string() or " "
        _creator = self.doc.get_creator() or " "
        #
        months = ["gen","feb","mar","apr","may","jun","jul","ago","sep","oct","nov","dec"]
        _date_time_o = self.doc.get_creation_date_time()
        _cdt = " "
        if _date_time_o:
            _Y,_M1,_D = _date_time_o.get_ymd() or (" "," "," ")
            _M = months[_M1-1] or " "
            _h = _date_time_o.get_hour() or " "
            _m = _date_time_o.get_minute() or " "
            _s = _date_time_o.get_second() or " "
            _cdt = "{} - {}".format("{}/{}/{}".format(_Y,_M,_D),"{}:{}:{}".format(_h,_m,_s))
        #
        _date_time_o2 = self.doc.get_modification_date_time()
        _mdt = " "
        if _date_time_o2:
            _Y2,_M12,_D2 = _date_time_o2.get_ymd() or (" "," "," ")
            _M2 = months[_M12-1] or " "
            _h2 = _date_time_o2.get_hour() or " "
            _m2 = _date_time_o2.get_minute() or " "
            _s2 = _date_time_o2.get_second() or " "
            _mdt = "{} - {}".format("{}/{}/{}".format(_Y2,_M2,_D2),"{}:{}:{}".format(_h2,_m2,_s2))
        #
        _data = [_title,_subject,_author,_producer,_pdf_v,_creator,_cdt,_mdt]
        winInfo(_data)
        
    def on_print(self, btn):
        try:
            # save the temporary file
            _sfx = str(time.time())
            _file = "/tmp/{}{}".format(os.path.basename(self._file),_sfx)
            ret = self.doc.save("file://{}".format(_file))
            if not ret:
                os.remove(_file)
                MyDialog("Error", "Cannot print: /tmp directory error.", self.window)
                return
            #
            print_dlg = Gtk.PrintDialog.new()
            print_dlg.set_modal(True)
            gfile = Gio.File.new_for_path(_file)
            print_dlg.print_file(None, None, gfile, None, None,None)
            os.remove(_file)
        except Exception as E:
            MyDialog("Error", str(E), self.window)
        
    def on_doc_save(self, btn):
        dialog = Gtk.AlertDialog()
        dialog.set_message("Info")
        dialog.set_detail("Do you want to save this file?")
        dialog.set_modal(True)
        dialog.set_buttons(["Cancel", "OK"])
        dialog.choose(self.window, None, self.on_doc_save_f)
        
    def on_doc_save_f(self, source_obj, async_res):
        result = source_obj.choose_finish(async_res)
        if result == 1:
            os.rename(self._file, self._file+"pdfreader4_bk")
            ret = self.doc.save("file://{}".format(self._file))
            if ret:
                MyDialog("Info", "File saved.\nThe previous file has been renamed:\n{}".format(os.path.basename(self._file))+"pdfreader4_bk", self.window)
            else:
                MyDialog("Error", "Error while saving the file.", self.window)
        elif result == 0:
            pass
        
    def on_save_as(self, btn):
        file_dialog = Gtk.FileDialog()
        file_dialog.set_title("Choose a pdf file...")
        file_dialog.set_modal(True)
        file_dialog.set_initial_folder(Gio.File.new_for_path(os.path.expanduser("~")))
        file_dialog.save(self.window, None, self.on_save_dlg_callback)
 
    def on_save_dlg_callback(self, dlg, res):
        try:
            gfile = dlg.save_finish(res)
            _file = gfile.get_path()
            if _file.split(".")[-1] != "pdf":
                _file += ".pdf"
            ret = self.doc.save("file://{}".format(_file))
            if ret:
                MyDialog("Info", "File saved.", self.window)
            else:
                MyDialog("Error", "Error while saving the file.", self.window)
        except Exception as E:
            MyDialog("Error", str(E), self.window)
        
    def on_infobar_annot_btn(self, ib, _id):
        if _id == 123:
            page = self.doc.get_page(self.da_to_remove_from.n_page)
            page.remove_annot(self.annot_to_remove)
            self.da_to_remove_from.queue_draw()
            MyDialog("Info", "Save this document.", self.window)
            # reset
            self.annot_to_remove = None
            self.da_to_remove_from = None
            self.set_sensitive(True)
            ib.hide()
        elif _id == Gtk.ResponseType.CLOSE:
            self.set_sensitive(True)
            ib.hide()
    
    def on_remove_annot(self, da, _annot):
        self.annot_to_remove = _annot
        self.da_to_remove_from = da
        self.infobar_annot_lbl.set_text("Do you want to remove this annotation?")
        self.infobar_annot.show()
        self.set_sensitive(False)
    
    def on_infobar_pw_btn(self, ib, _id):
        if _id == 456:
            _pw = self.infobar_pw_entry.get_text()
            if _pw or _pw == "":
                self.set_sensitive(True)
                self.add_page(self._file, _pw)
            #
        elif _id == -1:
            n_pages = self.window.notebook.get_n_pages()
            if n_pages == 1:
                self.window._to_close()
            else:
                curr_page = self.window.notebook.get_current_page()
                self.window.notebook.remove_page(curr_page)
                ib.hide()
    
    def on_btn_annot_text(self, _action, _data, _t):
        self.annot_type = _t
        if _t == 1: # text
            self.cursor_changed_annot = True
            default = Gdk.Cursor.new_from_name("default")
            pointer = Gdk.Cursor.new_from_name("pointer", default)
            self.scrolledwindow.set_cursor(pointer)
            self.annot_btn.popdown()
        # square - circle
        elif _t == 3 or _t == 4:
            self.cursor_changed_annot = True
            default = Gdk.Cursor.new_from_name("default")
            pointer = Gdk.Cursor.new_from_name("pointer", default)
            self.scrolledwindow.set_cursor(pointer)
            self.annot_btn.popdown()
        # stamp
        elif _t in [50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65]:
            self.cursor_changed_annot = True
            default = Gdk.Cursor.new_from_name("default")
            pointer = Gdk.Cursor.new_from_name("pointer", default)
            self.scrolledwindow.set_cursor(pointer)
            self.annot_btn.popdown()
        # arrow
        elif _t == 6:
            self.cursor_changed_annot = True
            default = Gdk.Cursor.new_from_name("default")
            pointer = Gdk.Cursor.new_from_name("pointer", default)
            self.scrolledwindow.set_cursor(pointer)
            self.annot_btn.popdown()
        # free text
        elif _t == 7:
            self.cursor_changed_annot = True
            default = Gdk.Cursor.new_from_name("default")
            pointer = Gdk.Cursor.new_from_name("pointer", default)
            self.scrolledwindow.set_cursor(pointer)
            self.annot_btn.popdown()
        # markup
        elif _t == 2:
            if self.old_selection == None:
                return
            if self.old_selection:
                # self.old_selection is a poppler.rectangle
                self.annot_btn.popdown()
                ##########
                # TO DO
                da = self.list_da[0][0]
                page = self.doc.get_page(0)#(da.n_page))
                #
                ###################
                _rect = Poppler.Rectangle.new()
                _rect.x1 = 0
                _rect.y1 = da.get_height()/self._zoom_has_been_rectified-0
                _rect.x2 = 100
                _rect.y2 = da.get_height()/self._zoom_has_been_rectified-100
                #
                _quad = Poppler.Quadrilateral.new()
                # point.p1 - where?
                _quad.p1.x = 0
                _quad.p1.y = da.get_height()/self._zoom_has_been_rectified-100
                # point.p2
                _quad.p2.x = 100
                _quad.p2.y = da.get_height()/self._zoom_has_been_rectified-100
                # point.p3
                _quad.p3.x = 100
                _quad.p3.y = da.get_height()/self._zoom_has_been_rectified-0
                # point.p4
                _quad.p4.x = 0
                _quad.p4.y = da.get_height()/self._zoom_has_been_rectified-0
                #
                quads = [_quad]
                annot_mkup_h = Poppler.AnnotTextMarkup.new_highlight(self.doc, _rect, quads)
                annot_mkup_h.set_contents("test")
                #
                _c = Poppler.Color.new()
                _c.red = 60000
                _c.green = 1
                _c.blue = 1
                annot_mkup_h.set_color(_c)
                #
                annot_mkup_h.set_quadrilaterals(quads)
                #
                page.add_annot(annot_mkup_h)
                #
                da.queue_draw()
                #
                return
    
    def on_lateral_panel_btn(self, btn):
        if btn.get_active():
            self.index_box.show()
        else:
            self.index_box.hide()
        
    def add_page(self, _file, _password=None):
        self._gfile = Gio.File.new_for_path(_file)
        try:
            self.doc = Poppler.Document.new_from_gfile(self._gfile, _password, None)
        except GLib.GError as E:
            if E.code == 1:
                self.infobar_pw.show()
                self.infobar_pw_entry.set_text("")
                self.set_sensitive(False)
                return
            else:
                MyDialog("Error", "An error occoured: {}".format(str(E)), self.window)
                return
        except Exception as E:
            MyDialog("Error", str(E), self.window)
            return
        #
        if self.infobar_pw.get_visible():
            self.infobar_pw.hide()
        # toc
        self.create_index(self.doc)
        #
        self._pad_around_page = 10
        self.da_box = Gtk.Box.new(1,self._pad_around_page)
        self.scrolledwindow.set_child(self.da_box)
        #
        # maximum drawing area width
        self.p_width = 0
        self.p_height = 0
        for i in range(self.doc.get_n_pages()):
            self.p_width = max(self.p_width, self.doc.get_page(i).get_size().width)
            self.p_height += self.doc.get_page(i).get_size().height
        #
        self.on_add_page()
        #
        self._control_pressed = 0
        self.event_controller_key = Gtk.EventControllerKey.new()
        # key-pressed key-released
        self.event_controller_key.connect('modifiers', self.on_da_modifier_pressed)
        #
        self.event_controller_key.connect('key-pressed', self.on_da_key_pressed, 1)
        self.event_controller_key.connect('key-released', self.on_da_key_pressed, 0)
        self.window.add_controller(self.event_controller_key)
        
    # def creare_links(self, page, _n):
        # self.list_links.append([page, page.get_link_mapping()])
    
    def populate_annotation_list(self):
        self.list_annotations = []
        for i in range(self.doc.get_n_pages()):
            page = self.doc.get_page(i)
            page_list_annotations = page.get_annot_mapping()
            self.list_annotations.append([i, page_list_annotations])
        
    def on_add_page(self):
        for i in range(self.doc.get_n_pages()):
            page = self.doc.get_page(i)
            #
            # # links
            # self.creare_links(page, i)
            #
            self.populate_annotation_list()
            #
            da = Gtk.DrawingArea()
            # property: number of the page
            da.n_page = i
            # self.da.set_content_width(page.get_size().width)
            # self.da.set_content_height(page.get_size().height)
            # # self.da.set_size_request(page_size.width,page_size.height)
            da.set_halign(Gtk.Align.CENTER)
            da.set_valign(Gtk.Align.CENTER)
            da.set_hexpand(True)
            da.set_vexpand(True)
            self.da_box.append(da)
            # left button
            self.da_gesture_l = Gtk.GestureClick.new()
            self.da_gesture_l.set_button(1)
            da.add_controller(self.da_gesture_l)
            self.da_gesture_l.connect('pressed', self.on_da_gesture_l, da, 1)
            self.da_gesture_l.connect('released', self.on_da_gesture_l, da, 0)
            self.left_click_setted = 0
            # center button
            self.da_gesture_c = Gtk.GestureClick.new()
            self.da_gesture_c.set_button(2)
            da.add_controller(self.da_gesture_c)
            self.da_gesture_c.connect('pressed', self.on_da_gesture_c, da)
            self.center_click_setted = 0
            # right button
            self.da_gesture_r = Gtk.GestureClick.new()
            self.da_gesture_r.set_button(3)
            da.add_controller(self.da_gesture_r)
            self.da_gesture_r.connect('pressed', self.on_da_gesture_r, da)
            self.right_click_setted = 0
            #
            da.set_focusable(True)
            da.set_focus_on_click(True)
            #
            da.set_content_width(self.p_width*self._zoom)
            #
            # self.has_been_drawn = 0
            da.set_draw_func(self.on_draw, page, 0)
            #
            ## dragging
            self.da_gesture_d = Gtk.GestureDrag.new()
            self.da_gesture_d.set_button(1)
            da.add_controller(self.da_gesture_d)
            self.da_gesture_d.connect('drag-begin', self.on_da_gesture_d_b, da)
            self.da_gesture_d.connect('drag-update', self.on_da_gesture_d_u, da)
            self.da_gesture_d.connect('drag-end', self.on_da_gesture_d_e, da)
            #
            # initial values
            self.start_x = 0
            self.start_y = 0
            self.end_x = 0
            self.end_y = 0
            #
        # the width of the scrollingwindow widget
        self.scrolledwindow_width = 0
    
    def create_index(self, doc):
        ######
        # how to check if any or none?
        try:
            iterp = Poppler.IndexIter.new(doc)
        except:
            self.create_index2()
            return
        link = iterp.get_action()
        if link.any.type == Poppler.ActionType.GOTO_DEST:
            link_title = link.any.title
            link_page_num = int(link.goto_dest.dest.page_num)
            link_pos_left = int(link.goto_dest.dest.left)
            link_pos_top = int(link.goto_dest.dest.top)
            # 
            treeiter = self.model.append(None, [link_title, link_page_num, link_pos_left,link_pos_top])
            self.walk_index1(iterp, doc, treeiter)
            
    # no indexes, adding page numbers
    def create_index2(self):
        doc_len = self.doc.get_n_pages()
        for i in range(doc_len):
            _page = "Page {}".format(i+1)
            _page_n = i+1
            treeiter = self.model.append(None, [_page, _page_n, 0,0])
            
    
    def walk_index1(self, iterp, doc, treeiter):
        if iterp == False:
            return
            
        if iterp == None:
            return
            
        child = iterp.get_child()
        if child:
            self.walk_index2(child, doc, treeiter)
        #
        while 1:
            if iterp.next() == False:
                break
            #
            link=iterp.get_action()
            # .URI .GOTO_DEST
            if link.any.type == Poppler.ActionType.GOTO_DEST:
                link_page_num = link.goto_dest.dest.page_num
                link_title = link.any.title
                link_pos_left = link.goto_dest.dest.left
                link_pos_top = link.goto_dest.dest.top
                treeiter = self.model.append(None, [link_title, link_page_num, link_pos_left,link_pos_top])
            else:
                continue
            #
            child = iterp.get_child()
            if child:
                self.walk_index2(child, doc, treeiter)
    
    # child
    def walk_index2(self, iterp, doc, treeiter):
        while 1:
            link=iterp.get_action()
            if link.any.type == Poppler.ActionType.GOTO_DEST:
                link_page_num = link.goto_dest.dest.page_num
                link_title = link.any.title
                link_pos_left = link.goto_dest.dest.left
                link_pos_top = link.goto_dest.dest.top
                treeiter_ch = self.model.append(treeiter, [link_title, link_page_num, link_pos_left,link_pos_top])
            child = iterp.get_child()
            if child:
                self.walk_index2(child, doc, treeiter_ch)
            #
            if iterp.next() == False:
                break
    
    def on_da_modifier_pressed(self, event_controller_key, state):
        ctrl = (state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl:
            self._control_pressed = 0
    
    def on_da_key_pressed(self, event_controller_key, keyval, keycode, state, _t):
        if keyval == Gdk.KEY_Escape:
            if self.cursor_changed_annot == True:
                default = Gdk.Cursor.new_from_name("default")
                self.scrolledwindow.set_cursor(default)
                self.cursor_changed_annot = False
                self.annot_type = 0
        elif keyval == Gdk.KEY_Control_L and _t:
            self._control_pressed = 1
        ctrl = (state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and _t:
            pass
        
        if keyval and ctrl and _t:
            pass
        
    def empty_box(self):
        while 1:
            cc = self.da_box.get_last_child()
            if cc != None:
                self.da_box.remove(cc)
            else:
                break
    
    def on_draw(self, da, cr, width, height, page, _type):
        if self._control_pressed == 0 and self.annot_type == 0:
            self.scrolledwindow_width = self.scrolledwindow.get_width()
        #
        _zoom_to_fit = (self.scrolledwindow_width/self.p_width)
        _pad_to_fit = int((self.p_width-page.get_size().width)/2)
        #
        _zoom = self._zoom * _zoom_to_fit
        self._zoom_has_been_rectified = _zoom
        #
        self.list_cr.append([da, cr])
        #
        if len(self.list_da) == 0:
            self.list_da.append([da, page.get_size().height])
        else:
            last_el = self.list_da[-1]
            self.list_da.append([da, last_el[1]+page.get_size().height])
        #
        da.set_content_width(page.get_size().width*_zoom)
        da.set_content_height(page.get_size().height*_zoom)
        #
        cr.scale(_zoom, _zoom)
        # paper colour
        cr.set_source_rgb(_p_r, _p_g, _p_b)
        y = 0
        x = 0
        #
        cr.rectangle (x,y,page.get_size().width,page.get_size().height)
        cr.fill()
        # border around the page
        cr.set_source_rgb(0.5,0.5,0.5)
        cr.rectangle (x,y,page.get_size().width,page.get_size().height)
        cr.stroke()
        #
        # page.render(cr)
        page.render_full(cr,False,Poppler.RenderAnnotsFlags.PRINT_ALL)
        #
        cr.set_line_width(4)
        cr.set_source_rgb(1.0,0.5,0.5)
        #
        if self.search_rect:
            x1 = self.search_rect.x1
            y1 = self.search_rect.y1
            x2 = self.search_rect.x2
            y2 = self.search_rect.y2
            x = x1
            y = page.get_size().height-y1
            w = x2-x1
            h = y1-y2
            cr.rectangle(x,y,w,h)
            cr.stroke()
        #
        # # links
        # page_link_list = page.get_link_mapping()
        # for ll in page_link_list:
            # x1 = ll.area.x1
            # x2 = ll.area.x2
            # y1 = ll.area.y1
            # y2 = ll.area.y2
            # x = x1
            # y = page.get_size().height-y1
            # w = (x2-x1)
            # h = (y1-y2)
            # cr.rectangle (x,y,w,h)
            # cr.stroke()
        #
        ########## text hightlight
        if self._control_pressed == 1 and self.annot_type == 0:
            # selection style: GLYPH WORD LINE
            _style = Poppler.SelectionStyle.GLYPH
            # text colour
            _g = Poppler.Color.new()
            _g.red = _t_hf_r
            _g.green = _t_hf_g
            _g.blue = _t_hf_b
            # background_color
            _b = Poppler.Color.new()
            _b.red = _t_hb_r
            _b.green = _t_hb_g
            _b.blue = _t_hb_b
            #
            _selection = Poppler.Rectangle.new()
            # lower left
            x1 = (self.start_x)/self._zoom_has_been_rectified
            # upper right
            x2 = (self.start_x+self.end_x)/self._zoom_has_been_rectified
            # lower left
            y1 = (self.start_y)/self._zoom_has_been_rectified
            # upper right
            y2 = (self.start_y+self.end_y)/self._zoom_has_been_rectified
            _selection.x1 = x1
            _selection.x2 = x2
            _selection.y1 = y1
            _selection.y2 = y2
            
            self.render_selection = page.render_selection(cr, _selection, _selection, _style, _g, _b)
            self.old_selection = _selection
        ########## end text hightlight
        ##########
        ### rubberband for annotations
        elif self.annot_type in [3,4,6,7,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65]:
            w = self.end_x/self._zoom_has_been_rectified
            h = self.end_y/self._zoom_has_been_rectified
            # adding a border
            cr.set_source_rgba(0, 0, 0, 0.5)
            cr.set_line_width(1.0)
            cr.rectangle(self.start_x/self._zoom_has_been_rectified,self.start_y/self._zoom_has_been_rectified,w,h)
            cr.stroke()
            #
            cr.set_source_rgba(1.0, 0.0, 0.0, 0.2)
            cr.rectangle(self.start_x/self._zoom_has_been_rectified,self.start_y/self._zoom_has_been_rectified,w,h)
            cr.fill()
        
    # show dialog after load
    def showDialog(self, title,x,y,da, _text):
        dialog = MessageBox(title, self.window, x,y,da, _text)
        dialog.connect("response", self.on_dialog_response)

    # for both options in Window class
    def on_dialog_response (self, widget, response_id, _annot=None, _page=None):
        match response_id:
            case Gtk.ResponseType.OK:
                if _annot == None:
                    self.add_annotation(widget.get_text(), widget.data)
                # modify the annotation text - useless
                else:
                    _annot_text = _annot.annot.get_contents()
                    _annot.annot.set_contents(_annot_text)
                    # repopulate the list
                    self.populate_annotation_list()
                widget.destroy()
            #
            case Gtk.ResponseType.CANCEL:
                widget.destroy()
            #
            case Gtk.ResponseType.DELETE_EVENT:
                widget.destroy()
    
    def add_annotation(self, _txt, data):
        if self._control_pressed == 1:
            return
        x = data[0]
        y = data[1]
        da = data[2]
        #
        if self.annot_type == 1:
            rect = Poppler.Rectangle.new()
            # lower left
            x1 = x/self._zoom_has_been_rectified
            # upper right
            x2 = x/self._zoom_has_been_rectified
            # lower left
            y1 = (da.get_height()-y)/self._zoom_has_been_rectified
            # upper right
            y2 = (da.get_height()-y)/self._zoom_has_been_rectified
            rect.x1 = x1
            rect.x2 = x2+24
            rect.y1 = y2-24
            rect.y2 = y1
            annot_text = Poppler.AnnotText.new(self.doc, rect)
            annot_text.set_contents(_txt)
            #
            _color = self.color_btn.get_rgba()
            _c = Poppler.Color.new()
            _c.red = _color.red*65535
            _c.green = _color.green*65535
            _c.blue = _color.blue*65535
            annot_text.set_color(_c)
            annot_text.set_opacity(_color.alpha)
            #
            annot_text.set_flags(Poppler.AnnotFlag.PRINT|Poppler.AnnotFlag.NO_ZOOM|Poppler.AnnotFlag.NO_ROTATE)
            #
            page = self.doc.get_page((da.n_page))
            page.add_annot(annot_text)
            #
            self.cursor_changed_annot = False
            del annot_text
            #
            da.queue_draw()
            # repopulate the list
            self.populate_annotation_list()
        # square - circle
        elif self.annot_type in [3,4,7]:
            page = self.doc.get_page((da.n_page))
            rect = Poppler.Rectangle.new()
            x1 = self.start_x/self._zoom_has_been_rectified
            y1 = (da.get_height()-self.start_y)/self._zoom_has_been_rectified
            x2 = (self.start_x+self.end_x)/self._zoom_has_been_rectified
            y2 = (da.get_height()-self.start_y-self.end_y)/self._zoom_has_been_rectified
            #
            rect.x1 = x1
            rect.x2 = x2
            rect.y1 = y1
            rect.y2 = y2
            # square - circle
            if self.annot_type == 3 or self.annot_type == 4 or self.annot_type == 7:
                if self.annot_type == 3: # square
                    _annot = Poppler.AnnotSquare.new(self.doc, rect)
                elif self.annot_type == 4: # circle
                    _annot = Poppler.AnnotCircle.new(self.doc, rect)
                elif self.annot_type == 7: # free text
                    _annot = Poppler.AnnotFreeText.new(self.doc, rect)
                # 
                _color = self.color_btn.get_rgba()
                _c = Poppler.Color.new()
                _c.red = _color.red*65535
                _c.green = _color.green*65535
                _c.blue = _color.blue*65535
                if self.annot_type != 7:
                    _annot.set_interior_color(_c)
                    #
                    _c = Poppler.Color.new()
                    _c.red = 15000
                    _c.green = 15000
                    _c.blue = 15000
                    _annot.set_color(_c)
                else:
                    _annot.set_color(_c)
                #
                _annot.set_flags(Poppler.AnnotFlag.PRINT|Poppler.AnnotFlag.NO_ZOOM|Poppler.AnnotFlag.NO_ROTATE)
                if self.annot_type != 7:
                    _annot.set_opacity(_color.alpha)
            # 
            _annot.set_border_width(self.border_width_cb.get_active()+1)
            page.add_annot(_annot)
            # set the content
            _annot.set_contents(_txt)
            #
            da.queue_draw()
            # repopulate the list
            self.populate_annotation_list()
            ### reset
            self.cursor_changed_annot = False
            #
            self.start_x = 0
            self.start_y = 0
            self.end_x = 0
            self.end_y = 0
            #
            self.annot_type = 0
        elif self.annot_type in [50,51,52,53,54,55,56,57,58,59,60,61,62,63,64]:
            page = self.doc.get_page(da.n_page)
            #
            rect = Poppler.Rectangle.new()
            x1 = self.start_x/self._zoom_has_been_rectified
            y1 = (da.get_height()-self.start_y)/self._zoom_has_been_rectified
            x2 = (self.start_x+self.end_x)/self._zoom_has_been_rectified
            y2 = (da.get_height()-self.start_y-self.end_y)/self._zoom_has_been_rectified
            #
            rect.x1 = x1
            rect.x2 = x2
            rect.y1 = y1
            rect.y2 = y2
            # 
            annot_stamp = Poppler.AnnotStamp.new(self.doc, rect)
            #
            _stamp_code_list = [0,1,10,11,12,13,14,2,3,4,5,6,7,8,9]
            _stamp_list = [50,51,52,53,54,55,56,57,58,59,60,61,62,63,64]
            _code = _stamp_code_list[_stamp_list.index(self.annot_type)]
            #
            annot_stamp.set_icon(_code)
            #
            # icons:
            # Poppler.AnnotStampIcon.
            # UNKNOWN= 0
            # APPROVED= 1
            # DEPARTMENTAL= 10
            # FOR_COMMENT= 11
            # FOR_PUBLIC_RELEASE= 12
            # TOP_SECRET= 13
            # NONE= 14
            # AS_IS= 2
            # CONFIDENTIAL= 3
            # FINAL= 4
            # EXPERIMENTAL= 5
            # EXPIRED= 6
            # NOT_APPROVED= 7
            # NOT_FOR_PUBLIC_RELEASE= 8
            # SOLD= 9
            annot_stamp.set_contents(_txt)
            #
            _color = self.color_btn.get_rgba()
            _c = Poppler.Color.new()
            _c.red = _color.red*65535
            _c.green = _color.green*65535
            _c.blue = _color.blue*65535
            annot_stamp.set_color(_c)
            annot_stamp.set_opacity(_color.alpha)
            #
            page.add_annot(annot_stamp)
            #
            da.queue_draw()
            # repopulate the list
            self.populate_annotation_list()
            ### reset
            self.cursor_changed_annot = False
            #
            self.start_x = 0
            self.start_y = 0
            self.end_x = 0
            self.end_y = 0
            #
            self.annot_type = 0
        # stamp custom image
        elif self.annot_type == 65:
                file_dialog = Gtk.FileDialog()
                file_dialog.set_title("Choose a png file...")
                file_dialog.set_modal(True)
                file_dialog.set_initial_folder(Gio.File.new_for_path(os.path.expanduser("~")))
                ret=file_dialog.open(self.window, None, self.on_add_custom_image, [_txt,da])
        # arrow
        elif self.annot_type == 6:
            rect = Poppler.Rectangle.new()
            # top to bottom
            if self.start_x <= (self.start_x+self.end_x) and self.start_y <= (self.start_y+self.end_y):
                x1 = self.start_x/self._zoom_has_been_rectified
                y1 = (da.get_height()-self.start_y)/self._zoom_has_been_rectified
                x2 = (self.start_x+self.end_x)/self._zoom_has_been_rectified
                y2 = (da.get_height()-self.start_y-self.end_y)/self._zoom_has_been_rectified
            elif self.start_x > (self.start_x+self.end_x) and self.start_y > (self.start_y+self.end_y):
                return
            #
            rect.x1 = x1
            rect.x2 = x2
            rect.y1 = y1
            rect.y2 = y2
            #
            starting_point = Poppler.Point.new()
            ending_point = Poppler.Point.new()
            # top to bottom
            if self.start_x<=(self.start_x+self.end_x) and self.start_y<=(self.start_y+self.end_y):
                starting_point.x = self.start_x/self._zoom_has_been_rectified
                starting_point.y = self.start_y/self._zoom_has_been_rectified
                #
                ending_point.x = (self.start_x+self.end_y)/self._zoom_has_been_rectified
                ending_point.y = (self.start_y+self.end_y)/self._zoom_has_been_rectified
            elif self.start_x > (self.start_x+self.end_x) and self.start_y > (self.start_y+self.end_y):
                pass
            #
            _annot = Poppler.AnnotLine.new(self.doc,rect,starting_point,ending_point)
            _annot.set_vertices(starting_point,ending_point)
            _color = self.color_btn.get_rgba()
            _c = Poppler.Color.new()
            _c.red = _color.red*65535
            _c.green = _color.green*65535
            _c.blue = _color.blue*65535
            _annot.set_color(_c)
            #
            _annot.set_flags(Poppler.AnnotFlag.PRINT|Poppler.AnnotFlag.NO_ZOOM|Poppler.AnnotFlag.NO_ROTATE)
            _annot.set_opacity(_color.alpha)
            #
            page = self.doc.get_page((da.n_page))
            page.add_annot(_annot)
            # set the content
            _annot.set_contents(_txt)
            #
            da.queue_draw()
            # repopulate the list
            self.populate_annotation_list()
            ### reset
            self.cursor_changed_annot = False
            #
            self.start_x = 0
            self.start_y = 0
            self.end_x = 0
            self.end_y = 0
            #
            self.annot_type = 0
    
    # stamp custom image
    def on_add_custom_image(self, source_object, res, data):
        try:
            _txt = data[0]
            da = data[1]
            #
            gfile = source_object.open_finish(res)
            _file = gfile.get_path()
            if os.path.exists(_file) and os.access(_file, os.R_OK):
                page = self.doc.get_page(da.n_page)
                #
                _image = _file
                _img = GdkPixbuf.Pixbuf.new_from_file(_image)
                _img_w = _img.get_width()
                _img_h = _img.get_height()
                #
                rect = Poppler.Rectangle.new()
                if _img_w > 0 and _img_h > 0:
                    x1 = self.start_x/self._zoom_has_been_rectified
                    y1 = (da.get_height()-self.start_y)/self._zoom_has_been_rectified
                    x2 = (self.start_x+self.end_x)/self._zoom_has_been_rectified
                    yy = _img_h/(_img_w/self.end_x)
                    y2 = (da.get_height()-self.start_y-yy)/self._zoom_has_been_rectified
                else:
                    x1 = self.start_x/self._zoom_has_been_rectified
                    y1 = (da.get_height()-self.start_y)/self._zoom_has_been_rectified
                    x2 = (self.start_x+self.end_x)/self._zoom_has_been_rectified
                    y2 = (da.get_height()-self.start_y-self.end_y)/self._zoom_has_been_rectified
                #
                rect.x1 = x1
                rect.x2 = x2
                rect.y1 = y1
                rect.y2 = y2
                # 
                annot_stamp = Poppler.AnnotStamp.new(self.doc, rect)
                #
                custom_image = cairo.ImageSurface.create_from_png(_image)
                annot_stamp.set_custom_image(custom_image)
                #
                annot_stamp.set_contents(_txt)
                #
                _color = self.color_btn.get_rgba()
                _c = Poppler.Color.new()
                _c.red = _color.red*65535
                _c.green = _color.green*65535
                _c.blue = _color.blue*65535
                annot_stamp.set_color(_c)
                annot_stamp.set_opacity(_color.alpha)
                #
                page.add_annot(annot_stamp)
                #
                da.queue_draw()
                # repopulate the list
                self.populate_annotation_list()
                ### reset
                self.cursor_changed_annot = False
                #
                self.start_x = 0
                self.start_y = 0
                self.end_x = 0
                self.end_y = 0
                #
                self.annot_type = 0
        except Exception as E:
            MyDialog("Error", str(E), self.window)
    
    def find_annot(self, da, x , y):
        # el = [n_page, [list of annotations]]
        page = da.n_page
        x = x/self._zoom_has_been_rectified
        y = y/self._zoom_has_been_rectified
        i = 0
        # _annot_text = ""
        _annot = None
        for el in self.list_annotations:
            if el[0] == page:
                for annot in el[1]:
                    if annot.area.x1 < x < annot.area.x2:
                        if annot.area.y1 < self.calculate_pos_in_page(y, self.list_da[0][0].get_height())/self._zoom_has_been_rectified < annot.area.y2:
                            _annot = annot
                            break
        #
        return _annot
    
    # _t: 1 pressed 0 released
    def on_da_gesture_l(self, o,n,x,y, da, _t):
        if _t == 1:
            self.left_click_setted = 1
            if self.cursor_changed_annot == True:
                # reset the cursor
                self.cursor_changed = False
                default = Gdk.Cursor.new_from_name("default")
                self.scrolledwindow.set_cursor(default)
                #
                if self.annot_type == 1:
                    self.showDialog("Add the annotation",x,y,da,None)
                return
            else:
                if self._control_pressed == 0:
                    # old selection - poppler rectangle
                    self.old_selection = None
                    #
                    self.left_click_setted = 1
                    # reset
                    self.selected_text = ""
                    self.search_rect = None
                    # remove the selection on the text
                    da.queue_draw()
                return
        else:
            ## draw the annotations
            # type square
            if self.annot_type in [3,4,6,7,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65]:
                self.showDialog("Add the annotation",x,y,da,None)
            #
            # reset
            self.left_click_setted = 0
        #
        #####
        _annot = self.find_annot(da, x , y)
        _annot_text = None
        if _annot:
            _annot_text = _annot.annot.get_contents()
        #
        if _annot_text == None:
            return
            # if _annot:
                # if _annot.annot.get_annot_type() == Poppler.AnnotType.LINK:
                    # _rect = _annot.annot.get_rectangle()
                    # page = self.doc.get_page(_annot.annot.get_page_index())
                    # _list = page.get_link_mapping()
                    # for el in _list:
                        # if (el.area.x1==_annot.annot.get_rectangle().x1) and \
                        # (el.area.x2==_annot.annot.get_rectangle().x2) and \
                        # (el.area.y1==_annot.annot.get_rectangle().y1) and \
                        # (el.area.y2==_annot.annot.get_rectangle().y2):
                            # if el.action.type == Poppler.ActionType.GOTO_DEST:
                                # page_num = el.action.goto_dest.dest.page_num
                                # print("1769 page num", el.action.goto_dest.dest.page_num)#, el.action.goto_dest.title)
                                # print("1769", el.action.goto_dest.dest.type)
                                # print("1769 top", el.action.goto_dest.dest.top)
                                # print("1769 bottom", el.action.goto_dest.dest.bottom)
                                # print("1769 left", el.action.goto_dest.dest.left)
                                # print("1769 right", el.action.goto_dest.dest.right)
                                # print("1769 named", el.action.goto_dest.dest.named_dest)
                            # break
            # return
        if _annot_text == "" or _annot_text != None:
        # else:
            MyDialog("Annotation", _annot_text, self.window)
    
    def on_da_gesture_c(self, o,n,x,y,da):
        page = da.n_page
        _adjh = self.hscrollbar.get_adjustment()
        _adjv = self.vscrollbar.get_adjustment()
        
    def on_da_gesture_r(self, o,n,x,y,da):
        page = da.n_page
        if isinstance(o.get_widget(), Gtk.DrawingArea):
            da = o.get_widget()
            page = da.n_page
            x = x/self._zoom_has_been_rectified
            y = y/self._zoom_has_been_rectified
            i = 0
            _annot_text = ""
            for el in self.list_annotations:
                if el[0] == page:
                    for annot in el[1]:
                        # 
                        if annot.area.x1 < x < annot.area.x2:
                            if annot.area.y1 < self.calculate_pos_in_page(y, self.list_da[0][0].get_height())/self._zoom_has_been_rectified < annot.area.y2:
                                self.on_remove_annot(da, annot.annot)
                                break
            
            ### funziona
            if self.selected_text != "":
                self.popover = Gtk.PopoverMenu()
                btn_01 = Gtk.Button(label="Copy to clipboard")
                btn_01.connect("clicked", self.on_btn_popover, "clipboard")
                self.popover.set_child(btn_01)
                self.popover.set_parent(o.get_widget())
                rect = Gdk.Rectangle()
                # because already divided early
                rect.x = x*self._zoom_has_been_rectified
                rect.y = y*self._zoom_has_been_rectified
                rect.width = 1
                rect.height = 1
                self.popover.set_pointing_to(rect)
                self.popover.popup()
    
    def on_btn_popover(self, btn, _type):
        if _type == "clipboard":
            self.window._clipboard.set(self.selected_text)
            self.selected_text = ""
        self.popover.popdown()
        
    def on_reset_zoom_btn(self, btn):
        self.empty_box()
        self.list_da = []
        self._zoom = self.starting_zoom
        self.on_add_page()
        
    def on_zoom_button(self, btn, _step):
        self._zoom += _step
        self.empty_box()
        self.list_da = []
        self.on_add_page()
        
    # drag begin
    def on_da_gesture_d_b(self, gesture_drag, start_x, start_y, da):
        self.start_x = start_x
        self.start_y = start_y
        
    # drag update
    def on_da_gesture_d_u(self, gesture_drag, offset_x, offset_y, da):
        # reset
        self.list_r = []
        self.dradding_text = ""
        #
        if (self._control_pressed == 1 or self.annot_type != 0):# and offset_x > 0 and offset_y > 0:
            self.end_x = offset_x
            self.end_y = offset_y
            da.queue_draw()
    
    def poprect_to_gdkrect(self, prect):
        x1 = prect.x1*self._zoom
        x2 = prect.x2*self._zoom
        y1 = prect.y1*self._zoom
        y2 = prect.y2*self._zoom
        #
        x = x1
        y = y1
        w = x2-x1
        h = y2-y1
        #
        rect = Gdk.Rectangle()
        rect.x = x
        rect.y = y
        rect.width = w
        rect.height = h
        return rect
        
    # drag end - drawing area
    def on_da_gesture_d_e(self, gesture_drag, offset_x, offset_y, da):
        # getting the selected text - e.g. clipboard
        if self.old_selection:
            n_page = da.n_page
            page = self.doc.get_page(n_page)
            self.selected_text = page.get_selected_text(Poppler.SelectionStyle.GLYPH, self.old_selection)
        #
        # reset
        if self.annot_type == 0:
            self.start_x = 0
            self.start_y = 0
            self.end_x = 0
            self.end_y = 0
        self.list_page_text_rectangles = []
        self.list_r = []
        #
        # the poppler render selection object
        self.render_selection = None


class MessageBox(Gtk.Dialog):
    def __init__ (self, text, parent,x,y,da,_text):
        super ().__init__()
        #
        self._parent = parent
        self.set_transient_for(self._parent)
        self.set_modal(True)
        #
        self._text = _text
        #
        self.set_default_size(400,400)
        #
        self.data = [x,y,da]
        #
        self.area = self.get_content_area()
        message= Gtk.Label()
        message.set_text(text)
        self.area.append(message)
        #
        self.textview = Gtk.TextView()
        self.textview.set_vexpand(True)
        self.area.append(self.textview)
        self.buffer = Gtk.TextBuffer()
        self.textview.set_buffer(self.buffer)
        if self._text:
            self.buffer.insert_at_cursor(self._text, len(self._text))
        #
        self.add_button ("OK", Gtk.ResponseType.OK)
        self.add_button ("Cancel", Gtk.ResponseType.CANCEL)
        self.show()
    
    def get_text(self):
        _iter1 = self.buffer.get_start_iter()
        _iter2 = self.buffer.get_end_iter()
        _txt = self.buffer.get_text(_iter1,_iter2,True)
        return _txt


def main():
    win = MyWindow()
    win.present()
    loop = GLib.MainContext().default()
    while QUIT:
        loop.iteration(True)

if __name__ == '__main__':
    main()

