#!/usr/bin/python

"""
MiniNDNEdit: a simple network editor for MiniNDN

Based on miniedit by:
Bob Lantz, April 2010
Gregory Gee, July 2013

Carlos Cabral, Jan 2013
Caio Elias, Nov 2014

"""

MINIEDIT_VERSION = '2.2.0.1'

from optparse import OptionParser
from Tkinter import *
from ttk import Notebook
from tkMessageBox import showinfo, showerror, showwarning
from subprocess import call, Popen
import tkFont
import csv
import tkFileDialog
import tkSimpleDialog
import re
import json
from distutils.version import StrictVersion
import os
import sys
import threading
from functools import partial

import pdb

if 'PYTHONPATH' in os.environ:
    sys.path = os.environ[ 'PYTHONPATH' ].split( ':' ) + sys.path

# someday: from ttk import *

from mininet.log import info, error, debug, output, setLogLevel
from mininet.net import Mininet, VERSION
from mininet.util import ipStr, netParse, ipAdd, quietRun
from mininet.util import buildTopo
from mininet.util import custom
from mininet.term import makeTerm, cleanUpScreens
from mininet.node import Controller, RemoteController, NOX, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, OVSSwitch, UserSwitch
from mininet.link import TCLink, Intf, Link
from mininet.cli import CLI
from mininet.moduledeps import moduleDeps, pathCheck
from mininet.topo import SingleSwitchTopo, LinearTopo, SingleSwitchReversedTopo
from mininet.topolib import TreeTopo

print 'MiniNDNEdit running...' #+VERSION
MININET_VERSION = re.sub(r'[^\d\.]', '', VERSION)
if StrictVersion(MININET_VERSION) > StrictVersion('2.0'):
    from mininet.node import IVSSwitch


from ndn.gui import NfdFrame, NlsrFrame

TOPODEF = 'none'
TOPOS = { 'minimal': lambda: SingleSwitchTopo( k=2 ),
          'linear': LinearTopo,
          'reversed': SingleSwitchReversedTopo,
          'single': SingleSwitchTopo,
          'none': None,
          'tree': TreeTopo }
LINKDEF = 'default'
LINKS = { 'default': Link,
          'tc': TCLink }
HOSTDEF = 'proc'
HOSTS = { 'proc': Host,
          'rt': custom( CPULimitedHost, sched='rt' ),
          'cfs': custom( CPULimitedHost, sched='cfs' ) }

def runMiniNdn(window, template):
    # Hide window
    window.withdraw()

    proc = Popen("sudo minindn %s" % template, shell=True)
    proc.wait()

    # Restore window
    window.deiconify()

class LegacyRouter( Node ):

    def __init__( self, name, inNamespace=True, **params ):
        Node.__init__( self, name, inNamespace, **params )

    def config( self, **_params ):
        if self.intfs:
            self.setParam( _params, 'setIP', ip='0.0.0.0' )
        r = Node.config( self, **_params )
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        return r

class CustomDialog(object):

        # TODO: Fix button placement and Title and window focus lock
        def __init__(self, master, title):
            self.top=Toplevel(master)

            self.bodyFrame = Frame(self.top)
            self.bodyFrame.grid(row=0, column=0, sticky='nswe')
            self.body(self.bodyFrame)

            #return self.b # initial focus
            buttonFrame = Frame(self.top, relief='ridge', bd=3, bg='lightgrey')
            buttonFrame.grid(row=1 , column=0, sticky='nswe')

            okButton = Button(buttonFrame, width=8, text='OK', relief='groove',
                       bd=4, command=self.okAction)
            okButton.grid(row=1, column=0, sticky=E)

            canlceButton = Button(buttonFrame, width=8, text='Cancel', relief='groove',
                        bd=4, command=self.cancelAction)
            canlceButton.grid(row=1, column=1, sticky=W)

        def body(self, master):
            self.rootFrame = master

        def apply(self):
            self.top.destroy()

        def cancelAction(self):
            self.top.destroy()

        def okAction(self):
            self.apply()
            self.top.destroy()

class HostDialog(CustomDialog):

        def __init__(self, master, title, prefDefaults, isRouter):

            self.prefValues = prefDefaults
            self.result = None
            self.isRouter = isRouter
            self.title = title

            CustomDialog.__init__(self, master, title)

        def body(self, master):
            self.rootFrame = master
            n = Notebook(self.rootFrame)
            self.propFrame = Frame(n)
            self.fibFrame = Frame(n)

            # NDN
            self.nfdFrame = NfdFrame(n)
            self.nlsrFrame = NlsrFrame(n)

            n.add(self.propFrame, text='Properties')
            n.add(self.fibFrame, text='FIB Entries')

            n.add(self.nfdFrame, text=self.nfdFrame.frameLabel)
            n.add(self.nlsrFrame, text=self.nlsrFrame.frameLabel)

            n.pack()

            ### TAB 1
            # Field for Hostname
            Label(self.propFrame, text="Hostname:").grid(row=0, sticky=E)
            self.hostnameEntry = Entry(self.propFrame)
            self.hostnameEntry.grid(row=0, column=1)
            if 'hostname' in self.prefValues:
                self.hostnameEntry.insert(0, self.prefValues['hostname'])

            # Field for CPU
            Label(self.propFrame, text="Amount CPU:").grid(row=2, sticky=E)
            self.cpuEntry = Entry(self.propFrame)
            self.cpuEntry.grid(row=2, column=1)
            Label(self.propFrame, text="%").grid(row=2, column=2, sticky=W)
            if 'cpu' in self.prefValues:
                self.cpuEntry.insert(0, str(self.prefValues['cpu']))

            # Field for Memory
            Label(self.propFrame, text="Amount MEM:").grid(row=3, sticky=E)
            self.memEntry = Entry(self.propFrame)
            self.memEntry.grid(row=3, column=1)
            Label(self.propFrame, text="%").grid(row=3, column=2, sticky=W)
            if 'mem' in self.prefValues:
                self.memEntry.insert(0, str(self.prefValues['mem']))

            # Field for Cache
            Label(self.propFrame, text="Amount CACHE:").grid(row=4, sticky=E)
            self.cacheEntry = Entry(self.propFrame)
            self.cacheEntry.grid(row=4, column=1)
            Label(self.propFrame, text="KBytes").grid(row=4, column=2, sticky=W)
            if 'cache' in self.prefValues:
                self.cacheEntry.insert(0, str(self.prefValues['cache']))

            # Start command
            #print self.isRouter
            if self.isRouter == 'False':
                    Label(self.propFrame, text="Start Command:").grid(row=5, sticky=E)
                    self.startEntry = Entry(self.propFrame)
                    self.startEntry.grid(row=5, column=1, sticky='nswe', columnspan=3)
                    Label(self.propFrame, text="[full path]").grid(row=5, column=2, sticky=W)
                    if 'startCommand' in self.prefValues:
                        self.startEntry.insert(0, str(self.prefValues['startCommand']))
            else:
                self.startEntry= Entry(self.propFrame)

            ### TAB 2
            # FIB Entries
            self.fibEntries = 0
            Label(self.fibFrame, text="FIB Entry:").grid(row=0, column=0, sticky=E)
            self.fibButton = Button( self.fibFrame, text='Add', command=self.addEntry)
            self.fibButton.grid(row=0, column=1)

            self.fibFrame = VerticalScrolledTable(self.fibFrame, rows=0, columns=2, title='FIB Entries')
            self.fibFrame.grid(row=1, column=0, sticky='nswe', columnspan=2)
            self.fibTableFrame = self.fibFrame.interior
            self.fibTableFrame.addRow(value=['Prefix','Next Hop'], readonly=True)

            fibList = []
            if 'fibEntries' in self.prefValues:
                fibList = self.prefValues['fibEntries']
            for fibEntr in fibList:
                if isinstance( fibEntr, tuple ):
                    self.fibTableFrame.addRow(value=fibEntr)
                else:
                    self.fibTableFrame.addRow(value=[fibEntr,''])

        def addEntry( self ):
            self.fibTableFrame.addRow()

        def apply(self):
            fibEntries = []
            for row in range(self.fibTableFrame.rows):
                if (len(self.fibTableFrame.get(row, 0)) > 0 and row > 0):
                    if(len(self.fibTableFrame.get(row, 1)) > 0):
                        fibEntries.append((self.fibTableFrame.get(row, 0), self.fibTableFrame.get(row, 1)))
                    else:
                        fibEntries.append(self.fibTableFrame.get(row, 0))

            results = {'cpu': self.cpuEntry.get(),
                       'cache': self.cacheEntry.get(),
                       'mem': self.memEntry.get(),
                       'hostname':self.hostnameEntry.get(),
                       'startCommand':self.startEntry.get(),
                       'fibEntries':fibEntries,
                       'nlsr': self.nlsrFrame.getValues()
            }

            self.result = results

class VerticalScrolledTable(LabelFrame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, rows=2, columns=2, title=None, *args, **kw):
        LabelFrame.__init__(self, parent, text=title, padx=5, pady=5, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = TableFrame(canvas, rows=rows, columns=columns)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        return

class TableFrame(Frame):
    def __init__(self, parent, rows=2, columns=2):

        Frame.__init__(self, parent, background="black")
        self._widgets = []
        self.rows = rows
        self.columns = columns
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = Entry(self, borderwidth=0)
                label.grid(row=row, column=column, sticky="wens", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.insert(0, value)

    def get(self, row, column):
        widget = self._widgets[row][column]
        return widget.get()

    def addRow( self, value=None, readonly=False ):
        #print "Adding row " + str(self.rows +1)
        current_row = []
        for column in range(self.columns):
            label = Entry(self, borderwidth=0)
            label.grid(row=self.rows, column=column, sticky="wens", padx=1, pady=1)
            if value is not None:
                label.insert(0, value[column])
            if (readonly == True):
                label.configure(state='readonly')
            current_row.append(label)
        self._widgets.append(current_row)
        self.update_idletasks()
        self.rows += 1

class LinkDialog(tkSimpleDialog.Dialog):

        def __init__(self, parent, title, linkDefaults):

            self.linkValues = linkDefaults

            tkSimpleDialog.Dialog.__init__(self, parent, title)

        def body(self, master):

            self.var = StringVar(master)
            Label(master, text="Bandwidth:").grid(row=0, sticky=E)
            self.e1 = Entry(master)
            self.e1.grid(row=0, column=1)
            Label(master, text="[1-1000] Mbps").grid(row=0, column=2, sticky=W)
            if 'bw' in self.linkValues:
                self.e1.insert(0,str(self.linkValues['bw']))

            Label(master, text="Delay:").grid(row=1, sticky=E)
            self.e2 = Entry(master)
            self.e2.grid(row=1, column=1)
            Label(master, text="[0-1000] ms").grid(row=1, column=2, sticky=W)
            if 'delay' in self.linkValues:
                self.e2.insert(0, self.linkValues['delay'])

            Label(master, text="Loss:").grid(row=2, sticky=E)
            self.e3 = Entry(master)
            self.e3.grid(row=2, column=1)
            Label(master, text="%").grid(row=2, column=2, sticky=W)
            if 'loss' in self.linkValues:
                self.e3.insert(0, str(self.linkValues['loss']))

            return self.e1 # initial focus

        def apply(self):
            self.result = {}
            if (len(self.e1.get()) > 0):
                self.result['bw'] = int(self.e1.get())
            if (len(self.e2.get()) > 0):
                self.result['delay'] = self.e2.get()
            if (len(self.e3.get()) > 0):
                self.result['loss'] = int(self.e3.get())

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class MiniEdit( Frame ):

    "A simple network editor for MiniNDN."

    def __init__( self, parent=None, cheight=600, cwidth=1000, template_file='minindn.conf' ):

        self.template_file = template_file

        Frame.__init__( self, parent )
        self.action = None
        self.appName = 'MiniNDNEdit'
        self.fixedFont = tkFont.Font ( family="DejaVu Sans Mono", size="14" )

        # Style
        self.font = ( 'Geneva', 9 )
        self.smallFont = ( 'Geneva', 7 )
        self.bg = 'white'

        # Title
        self.top = self.winfo_toplevel()
        self.top.title( self.appName )

        # Menu bar
        self.createMenubar()

        # Editing canvas
        self.cheight, self.cwidth = cheight, cwidth
        self.cframe, self.canvas = self.createCanvas()

        # Toolbar
        self.controllers = {}

        # Toolbar
        self.images = miniEditImages()
        self.buttons = {}
        self.active = None
        self.tools = ( 'Select', 'Host', 'NetLink' )
        #self.customColors = { 'LegacyRouter': 'darkGreen', 'Host': 'blue' }
        self.toolbar = self.createToolbar()

        # Layout
        self.toolbar.grid( column=0, row=0, sticky='nsew')
        self.cframe.grid( column=1, row=0 )
        self.columnconfigure( 1, weight=1 )
        self.rowconfigure( 0, weight=1 )
        self.pack( expand=True, fill='both' )

        # About box
        self.aboutBox = None

        # Initialize node data
        self.nodeBindings = self.createNodeBindings()
        self.nodePrefixes = { 'LegacyRouter': 'r', 'Host': 'h'}
        self.widgetToItem = {}
        self.itemToWidget = {}

        # Initialize link tool
        self.link = self.linkWidget = None

        # Selection support
        self.selection = None

        # Keyboard bindings
        self.bind( '<Control-q>', lambda event: self.quit() )
        self.bind( '<KeyPress-Delete>', self.deleteSelection )
        self.bind( '<KeyPress-BackSpace>', self.deleteSelection )
        self.focus()

        #Mouse bindings
        self.bind( '<Button-1>', lambda event: self.clearPopups )

        self.hostPopup = Menu(self.top, tearoff=0)
        self.hostPopup.add_command(label='Host Options', font=self.font, command=self.hostDetails)
        #self.hostPopup.add_separator()
        #self.hostPopup.add_command(label='Properties', font=self.font, command=self.hostDetails )

        self.legacyRouterPopup = Menu(self.top, tearoff=0)
        self.legacyRouterPopup.add_command(label='Router Options', font=self.font, command=self.hostDetails)

        self.linkPopup = Menu(self.top, tearoff=0)
        self.linkPopup.add_command(label='Link Options', font=self.font, command=self.linkDetails)
        #self.linkPopup.add_separator()
        #self.linkPopup.add_command(label='Properties', font=self.font, command=self.linkDetails )

        # Event handling initalization
        self.linkx = self.linky = self.linkItem = None
        self.lastSelection = None

        # Model initialization
        self.links = {}
        self.hostOpts = {}
        self.switchOpts = {}
        self.routerOpts = {}
        self.hostCount = 0
        self.routerCount = 0
        self.net = None

        # Close window gracefully
        Wm.wm_protocol( self.top, name='WM_DELETE_WINDOW', func=self.quit )

    def quit( self ):
        "Stop our network, if any, then quit."
        #sself.stop()
        Frame.quit( self )

    def createMenubar( self ): # MODIFICADO - OK
        "Create our menu bar."

        font = self.font

        mbar = Menu( self.top, font=font )
        self.top.configure( menu=mbar )

        fileMenu = Menu( mbar, tearoff=False )
        mbar.add_cascade( label="File", font=font, menu=fileMenu )
        fileMenu.add_command( label="New", font=font, command=self.newTopology )
        fileMenu.add_command( label="Open", font=font, command=self.loadTopology )
        fileMenu.add_command( label="Save", font=font, command=self.saveTopology )
        fileMenu.add_command( label="Generate", font=font, command=self.doGenerate )
        fileMenu.add_command( label="Run", font=font, command=self.doRun )
        fileMenu.add_separator()
        fileMenu.add_command( label='Quit', command=self.quit, font=font )

        editMenu = Menu( mbar, tearoff=False )
        mbar.add_cascade( label="Edit", font=font, menu=editMenu )
        editMenu.add_command( label="Cut", font=font,
                              command=lambda: self.deleteSelection( None ) )

        # Application menu
        appMenu = Menu( mbar, tearoff=False )
        mbar.add_cascade( label=self.appName, font=font, menu=appMenu )
        appMenu.add_command( label='About Mini-NDN', command=self.about,
                             font=font)
        #appMenu.add_separator()
        #appMenu.add_command( label='Quit', command=self.quit, font=font )

    # Canvas - TUDO IGUAL - OK

    def createCanvas( self ):
        "Create and return our scrolling canvas frame."
        f = Frame( self )

        canvas = Canvas( f, width=self.cwidth, height=self.cheight,
                         bg=self.bg )

        # Scroll bars
        xbar = Scrollbar( f, orient='horizontal', command=canvas.xview )
        ybar = Scrollbar( f, orient='vertical', command=canvas.yview )
        canvas.configure( xscrollcommand=xbar.set, yscrollcommand=ybar.set )

        # Resize box
        resize = Label( f, bg='white' )

        # Layout
        canvas.grid( row=0, column=1, sticky='nsew')
        ybar.grid( row=0, column=2, sticky='ns')
        xbar.grid( row=1, column=1, sticky='ew' )
        resize.grid( row=1, column=2, sticky='nsew' )

        # Resize behavior
        f.rowconfigure( 0, weight=1 )
        f.columnconfigure( 1, weight=1 )
        f.grid( row=0, column=0, sticky='nsew' )
        f.bind( '<Configure>', lambda event: self.updateScrollRegion() )

        # Mouse bindings
        canvas.bind( '<ButtonPress-1>', self.clickCanvas )
        canvas.bind( '<B1-Motion>', self.dragCanvas )
        canvas.bind( '<ButtonRelease-1>', self.releaseCanvas )

        return f, canvas

    def updateScrollRegion( self ):
        "Update canvas scroll region to hold everything."
        bbox = self.canvas.bbox( 'all' )
        if bbox is not None:
            self.canvas.configure( scrollregion=( 0, 0, bbox[ 2 ],
                                   bbox[ 3 ] ) )

    def canvasx( self, x_root ):
        "Convert root x coordinate to canvas coordinate."
        c = self.canvas
        return c.canvasx( x_root ) - c.winfo_rootx()

    def canvasy( self, y_root ):
        "Convert root y coordinate to canvas coordinate."
        c = self.canvas
        return c.canvasy( y_root ) - c.winfo_rooty()

    # Toolbar

    def activate( self, toolName ): #IGUAL - OK
        "Activate a tool and press its button."
        # Adjust button appearance
        if self.active:
            self.buttons[ self.active ].configure( relief='raised' )
        self.buttons[ toolName ].configure( relief='sunken' )
        # Activate dynamic bindings
        self.active = toolName


    def createToolTip(self, widget, text): #NOVA - CRIA HINTS E TIPS
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def createToolbar( self ): #MODIFICADO - OK
        "Create and return our toolbar frame."

        toolbar = Frame( self )

        # Tools
        for tool in self.tools:
            cmd = ( lambda t=tool: self.activate( t ) )
            b = Button( toolbar, text=tool, font=self.smallFont, command=cmd)
            if tool in self.images:
                b.config( height=35, image=self.images[ tool ] )
                self.createToolTip(b, str(tool))
                # b.config( compound='top' )
            b.pack( fill='x' )
            self.buttons[ tool ] = b
        self.activate( self.tools[ 0 ] )

        # Spacer
        Label( toolbar, text='' ).pack()

        # abaixo copiado Mini-NDN para criar botao Generate

        for cmd, color in [ ( 'Generate', 'darkGreen' ) ]:
            doCmd = getattr( self, 'do' + cmd )
            b = Button( toolbar, text=cmd, font=self.smallFont,
                        fg=color, command=doCmd )
            b.pack( fill='x', side='bottom' )

        return toolbar

    def doGenerate( self ): #COPIA Mini-NDN - GERA TEMPLATE
        "Generate template."
        self.activate( 'Select' )
        for tool in self.tools:
            self.buttons[ tool ].config( state='disabled' )

        self.buildTemplate()

        for tool in self.tools:
            self.buttons[ tool ].config( state='normal' )

        toplevel = Toplevel()
        label1 = Label(toplevel, text="Template file generated successfully", height=0, width=30)
        label1.pack()
        b=Button(toplevel, text="Ok", width=5, command=toplevel.destroy)
        b.pack(side='bottom', padx=0,pady=0)

    def doRun( self ):
        "Use current configuration to generate a template and run the topology"

        # Generate temporary template file
        old_template_file = self.template_file
        self.template_file = "/tmp/tmp.conf"
        self.doGenerate()

        thread = threading.Thread(target=runMiniNdn, args=(self.master, self.template_file))
        thread.start()

        self.template_file = old_template_file

    def parseFibEntries ( self, fibEntries ):
        "Parse FIB Entries for write"
        result=''

        for fibEntry in fibEntries:
                entry = ','.join(map(str, fibEntry))
                result += entry + ' '

        return result

    def buildTemplate( self ): #COPIA Mini-NDN para criar Template
        "Generate template"

        template = open(self.template_file, 'w')

        # hosts
        template.write('[nodes]\n')
        for widget in self.widgetToItem:
            name = widget[ 'text' ]
            tags = self.canvas.gettags( self.widgetToItem[ widget ] )
            print self.hostOpts[name]
            if 'Host' in tags:
                hOpts=self.hostOpts[name]
                template.write(name + ': ')
                if 'startCommand' in hOpts:
                        template.write(hOpts['startCommand'] + ' ')
                else:
                        template.write('_ ')
                if 'cache' in hOpts:
                        template.write('cache=' + hOpts['cache'] + ' ')
                if 'cpu' in hOpts:
                        cpu=float(hOpts['cpu'])/100
                        template.write('cpu=' + repr(cpu) + ' ')
                if 'mem' in hOpts:
                        mem=float(hOpts['mem'])/100
                        template.write('mem=' + repr(mem) + ' ')
                if 'fibEntries' in hOpts:
                        customFib = self.parseFibEntries(hOpts['fibEntries'])
                        template.write(customFib)
                if 'nlsr' in hOpts:
                        values = hOpts['nlsr']

                        template.write('hyperbolic-state=' + values['hyperbolic-state'] + ' ')
                        template.write('radius=' + values['radius'] + ' ')
                        template.write('angle=' + values['angle'] + ' ')
                        template.write('network=' + values['network'] + ' ')
                        template.write('router=' + values['router'] + ' ')
                        template.write('site=' + values['site'] + ' ')
                        template.write('log-level=' + values['log-level'] + ' ')
                        template.write('max-faces-per-prefix=' + values['max-faces-per-prefix'] + ' ')

                template.write('\n')

        # switches/routers
        #template.write('[routers]\n')

        for router in self.routerOpts.values():

            hasOpt='False'
            routerName=router['hostname']
            #nodetype=router['nodetype']
            #nodenum=router['nodenum']

            rOpts=self.routerOpts[routerName]

            template.write(routerName + ': ')

            if 'cpu' in rOpts:
                cpu=float(rOpts['cpu'])/100
                template.write('cpu=' + repr(cpu) + ' ')
                hasOpt='True'
            if 'mem' in rOpts:
                mem=float(rOpts['mem'])/100
                template.write('mem=' + repr(mem) + ' ')
                hasOpt='True'
            if 'cache' in rOpts:
                template.write('cache=' + rOpts['cache'] + ' ')
                hasOpt='True'
            if 'fibEntries' in rOpts:
                customFib = self.parseFibEntries(rOpts['fibEntries'])
                template.write(customFib)
                hasOpt='True'
            if hasOpt == 'False':
                template.write('_')

            template.write('\n')

        # Make links
        template.write('[links]\n')
        for link in self.links.values():
             dst=link['dest']
             src=link['src']
             linkopts=link['linkOpts']
             linktype=link['type']

             srcName, dstName = src[ 'text' ], dst[ 'text' ]
             template.write(srcName + ':' + dstName + ' ')
             if 'bw' in linkopts:
                     template.write('bw=' + str(linkopts['bw']) + ' ' )
             if 'loss' in linkopts:
                     template.write('loss=' + repr(linkopts['loss']) + ' ' )
             if 'delay' in linkopts:
                     template.write('delay=' + str(linkopts['delay'])+ 'ms' )

             template.write('\n')

        template.close()

    def addNode( self, node, nodeNum, x, y, name=None):
        "Add a new node to our canvas."

        if 'LegacyRouter' == node:
            self.routerCount += 1
        if 'Host' == node:
            self.hostCount += 1
        if name is None:
            name = self.nodePrefixes[ node ] + nodeNum
        self.addNamedNode(node, name, x, y)

    def addNamedNode( self, node, name, x, y):
        "Add a new node to our canvas."
        c = self.canvas
        icon = self.nodeIcon( node, name )
        item = self.canvas.create_window( x, y, anchor='c', window=icon,
                                          tags=node )
        self.widgetToItem[ icon ] = item
        self.itemToWidget[ item ] = icon
        icon.links = {}

    def convertJsonUnicode(self, input):
        "Some part of Mininet don't like Unicode"
        if isinstance(input, dict):
            return {self.convertJsonUnicode(key): self.convertJsonUnicode(value) for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [self.convertJsonUnicode(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

    def loadTopology( self ):
        "Load command."
        c = self.canvas

        myFormats = [
            ('MiniNDN Topology','*.mnndn'),
            ('All Files','*'),
        ]
        f = tkFileDialog.askopenfile(filetypes=myFormats, mode='rb')
        if f == None:
            return
        self.newTopology()
        loadedTopology = self.convertJsonUnicode(json.load(f))

        # Load hosts
        hosts = loadedTopology['nodes']
        for host in hosts:
            nodeNum = host['number']
            hostname = 'h'+nodeNum
            if 'hostname' in host['opts']:
                hostname = host['opts']['hostname']
            else:
                host['opts']['hostname'] = hostname
            if 'nodeNum' not in host['opts']:
                host['opts']['nodeNum'] = int(nodeNum)
            x = host['x']
            y = host['y']

            self.addNode('Host', nodeNum, float(x), float(y), name=hostname)

            # Fix JSON converting tuple to list when saving
            if 'privateDirectory' in host['opts']:
                newDirList = []
                for privateDir in host['opts']['privateDirectory']:
                    if isinstance( privateDir, list ):
                        newDirList.append((privateDir[0],privateDir[1]))
                    else:
                        newDirList.append(privateDir)
                host['opts']['privateDirectory'] = newDirList
            self.hostOpts[hostname] = host['opts']
            icon = self.findWidgetByName(hostname)
            icon.bind('<Button-3>', self.do_hostPopup )

        # Load routers
        routers = loadedTopology['routers']
        for router in routers:
            nodeNum = router['number']
            hostname = 'r'+nodeNum
            #print router
            if 'nodeType' not in router['opts']:
                router['opts']['nodeType'] = 'legacyRouter'
            if 'hostname' in router['opts']:
                hostname = router['opts']['hostname']
            else:
                router['opts']['hostname'] = hostname
            if 'nodeNum' not in router['opts']:
                router['opts']['nodeNum'] = int(nodeNum)
            x = router['x']
            y = router['y']
            if router['opts']['nodeType'] == "legacyRouter":
                self.addNode('LegacyRouter', nodeNum, float(x), float(y), name=hostname)
                icon = self.findWidgetByName(hostname)
                icon.bind('<Button-3>', self.do_legacyRouterPopup )
            self.routerOpts[hostname] = router['opts']

        # Load links
        links = loadedTopology['links']
        for link in links:
            srcNode = link['src']
            src = self.findWidgetByName(srcNode)
            sx, sy = self.canvas.coords( self.widgetToItem[ src ] )

            destNode = link['dest']
            dest = self.findWidgetByName(destNode)
            dx, dy = self.canvas.coords( self.widgetToItem[ dest ]  )

            self.link = self.canvas.create_line( sx, sy, dx, dy, width=4,
                                             fill='blue', tag='link' )
            c.itemconfig(self.link, tags=c.gettags(self.link)+('data',))
            self.addLink( src, dest, linkopts=link['opts'] )
            self.createDataLinkBindings()
            self.link = self.linkWidget = None

        f.close

    def findWidgetByName( self, name ):
        for widget in self.widgetToItem:
            if name ==  widget[ 'text' ]:
                return widget

    def newTopology( self ):
        "New command."
        for widget in self.widgetToItem.keys():
            self.deleteItem( self.widgetToItem[ widget ] )
        self.hostCount = 0
        self.routerCount = 0
        self.links = {}
        self.hostOpts = {}
        self.routerOpts = {}

    def saveTopology( self ):
        "Save command."
        myFormats = [
            ('MiniNDN Topology','*.mnndn'),
            ('All Files','*'),
        ]

        savingDictionary = {}
        fileName = tkFileDialog.asksaveasfilename(filetypes=myFormats ,title="Save the topology as...")
        if len(fileName ) > 0:
            # Save Application preferences
            savingDictionary['version'] = '2'

            # Save routers and Hosts
            hostsToSave = []
            routersToSave = []

            for widget in self.widgetToItem:
                name = widget[ 'text' ]
                tags = self.canvas.gettags( self.widgetToItem[ widget ] )
                x1, y1 = self.canvas.coords( self.widgetToItem[ widget ] )
                if 'LegacyRouter' in tags:
                    nodeNum = self.routerOpts[name]['nodeNum']
                    nodeToSave = {'number':str(nodeNum),
                                  'x':str(x1),
                                  'y':str(y1),
                                  'opts':self.routerOpts[name] }
                    routersToSave.append(nodeToSave)
                elif 'Host' in tags:
                    nodeNum = self.hostOpts[name]['nodeNum']
                    nodeToSave = {'number':str(nodeNum),
                                  'x':str(x1),
                                  'y':str(y1),
                                  'opts':self.hostOpts[name] }
                    hostsToSave.append(nodeToSave)
                else:
                    raise Exception( "Cannot create mystery node: " + name )
            savingDictionary['hosts'] = hostsToSave
            savingDictionary['routers'] = routersToSave

            # Save Links
            linksToSave = []
            for link in self.links.values():
                src = link['src']
                dst = link['dest']
                linkopts = link['linkOpts']

                srcName, dstName = src[ 'text' ], dst[ 'text' ]
                linkToSave = {'src':srcName,
                              'dest':dstName,
                              'opts':linkopts}
                if link['type'] == 'data':
                    linksToSave.append(linkToSave)
            savingDictionary['links'] = linksToSave

            # Save Application preferences
            #savingDictionary['application'] = self.appPrefs

            try:
                f = open(fileName, 'wb')
                f.write(json.dumps(savingDictionary, sort_keys=True, indent=4, separators=(',', ': ')))
            except Exception as er:
                print er
            finally:
                f.close()

    # Generic canvas handler
    #
    # We could have used bindtags, as in nodeIcon, but
    # the dynamic approach used here
    # may actually require less code. In any case, it's an
    # interesting introspection-based alternative to bindtags.

    def canvasHandle( self, eventName, event ):
        "Generic canvas event handler"
        if self.active is None:
            return
        toolName = self.active
        handler = getattr( self, eventName + toolName, None )
        if handler is not None:
            handler( event )

    def clickCanvas( self, event ):
        "Canvas click handler."
        self.canvasHandle( 'click', event )

    def dragCanvas( self, event ):
        "Canvas drag handler."
        self.canvasHandle( 'drag', event )

    def releaseCanvas( self, event ):
        "Canvas mouse up handler."
        self.canvasHandle( 'release', event )

    # Currently the only items we can select directly are
    # links. Nodes are handled by bindings in the node icon.

    def findItem( self, x, y ):
        "Find items at a location in our canvas."
        items = self.canvas.find_overlapping( x, y, x, y )
        if len( items ) == 0:
            return None
        else:
            return items[ 0 ]

    # Canvas bindings for Select, Host, Router and Link tools

    def clickSelect( self, event ):
        "Select an item."
        self.selectItem( self.findItem( event.x, event.y ) )

    def deleteItem( self, item ):
        "Delete an item."
        # Don't delete while network is running
        if self.buttons[ 'Select' ][ 'state' ] == 'disabled':
            return
        # Delete from model
        if item in self.links:
            self.deleteLink( item )
        if item in self.itemToWidget:
            self.deleteNode( item )
        # Delete from view
        self.canvas.delete( item )

    def deleteSelection( self, _event ):
        "Delete the selected item."
        if self.selection is not None:
            self.deleteItem( self.selection )
        self.selectItem( None )

    def clearPopups(self):
        print 'Entrou funcao clear_popups'
        if isHostPopup == True:
            print 'Hostpopup = true'
            self.hostPopup.unpost
            isHostPopup = False
        #if isRouterPopup == True
        #if isLinkPopup == True

    def nodeIcon( self, node, name ):
        "Create a new node icon."
        icon = Button( self.canvas, image=self.images[ node ],
                       text=name, compound='top' )
        # Unfortunately bindtags wants a tuple
        bindtags = [ str( self.nodeBindings ) ]
        bindtags += list( icon.bindtags() )
        icon.bindtags( tuple( bindtags ) )
        return icon

    def newNode( self, node, event ):
        "Add a new node to our canvas."
        c = self.canvas
        x, y = c.canvasx( event.x ), c.canvasy( event.y )
        name = self.nodePrefixes[ node ]

        if 'LegacyRouter' == node:
            self.routerCount += 1
            name = self.nodePrefixes[ node ] + str( self.routerCount )
            self.routerOpts[name] = {}
            self.routerOpts[name]['nodeNum']=self.routerCount
            self.routerOpts[name]['hostname']=name
            self.routerOpts[name]['nodeType']='legacyRouter'

        if 'Host' == node:
            self.hostCount += 1
            name = self.nodePrefixes[ node ] + str( self.hostCount )
            self.hostOpts[name] = {'sched':'host'}
            self.hostOpts[name]['nodeNum']=self.hostCount
            self.hostOpts[name]['hostname']=name

        icon = self.nodeIcon( node, name )
        item = self.canvas.create_window( x, y, anchor='c', window=icon,
                                          tags=node )
        self.widgetToItem[ icon ] = item
        self.itemToWidget[ item ] = icon
        self.selectItem( item )
        icon.links = {}
        if 'LegacyRouter' == node:
            icon.bind('<Button-3>', self.do_legacyRouterPopup )
        if 'Host' == node:
            icon.bind('<Button-3>', self.do_hostPopup )

    def clickHost( self, event ):
        "Add a new host to our canvas."
        self.newNode( 'Host', event )

    def clickLegacyRouter( self, event ):
        "Add a new router to our canvas."
        self.newNode( 'LegacyRouter', event )

    def dragNetLink( self, event ):
        "Drag a link's endpoint to another node."
        if self.link is None:
            return
        # Since drag starts in widget, we use root coords
        x = self.canvasx( event.x_root )
        y = self.canvasy( event.y_root )
        c = self.canvas
        c.coords( self.link, self.linkx, self.linky, x, y )

    def releaseNetLink( self, _event ):
        "Give up on the current link."
        if self.link is not None:
            self.canvas.delete( self.link )
        self.linkWidget = self.linkItem = self.link = None

    # Generic node handlers

    def createNodeBindings( self ):
        "Create a set of bindings for nodes."
        bindings = {
            '<ButtonPress-1>': self.clickNode,
            '<B1-Motion>': self.dragNode,
            '<ButtonRelease-1>': self.releaseNode,
            '<Enter>': self.enterNode,
            '<Leave>': self.leaveNode
        }
        l = Label()  # lightweight-ish owner for bindings
        for event, binding in bindings.items():
            l.bind( event, binding )
        return l

    def selectItem( self, item ):
        "Select an item and remember old selection."
        self.lastSelection = self.selection
        self.selection = item

    def enterNode( self, event ):
        "Select node on entry."
        self.selectNode( event )

    def leaveNode( self, _event ):
        "Restore old selection on exit."
        self.selectItem( self.lastSelection )

    def clickNode( self, event ):
        "Node click handler."
        if self.active is 'NetLink':
            self.startLink( event )
        else:
            self.selectNode( event )
        return 'break'

    def dragNode( self, event ):
        "Node drag handler."
        if self.active is 'NetLink':
            self.dragNetLink( event )
        else:
            self.dragNodeAround( event )

    def releaseNode( self, event ):
        "Node release handler."
        if self.active is 'NetLink':
            self.finishLink( event )

    # Specific node handlers

    def selectNode( self, event ):
        "Select the node that was clicked on."
        item = self.widgetToItem.get( event.widget, None )
        self.selectItem( item )

    def dragNodeAround( self, event ):
        "Drag a node around on the canvas."
        c = self.canvas
        # Convert global to local coordinates;
        # Necessary since x, y are widget-relative
        x = self.canvasx( event.x_root )
        y = self.canvasy( event.y_root )
        w = event.widget
        # Adjust node position
        item = self.widgetToItem[ w ]
        c.coords( item, x, y )
        # Adjust link positions
        for dest in w.links:
            link = w.links[ dest ]
            item = self.widgetToItem[ dest ]
            x1, y1 = c.coords( item )
            c.coords( link, x, y, x1, y1 )
        self.updateScrollRegion()

    def createDataLinkBindings( self ):
        "Create a set of bindings for nodes."
        # Link bindings
        # Selection still needs a bit of work overall
        # Callbacks ignore event

        def select( _event, link=self.link ):
            "Select item on mouse entry."
            self.selectItem( link )

        def highlight( _event, link=self.link ):
            "Highlight item on mouse entry."
            self.selectItem( link )
            self.canvas.itemconfig( link, fill='green' )

        def unhighlight( _event, link=self.link ):
            "Unhighlight item on mouse exit."
            self.canvas.itemconfig( link, fill='blue' )
            #self.selectItem( None )

        self.canvas.tag_bind( self.link, '<Enter>', highlight )
        self.canvas.tag_bind( self.link, '<Leave>', unhighlight )
        self.canvas.tag_bind( self.link, '<ButtonPress-1>', select )
        self.canvas.tag_bind( self.link, '<Button-3>', self.do_linkPopup )

    def startLink( self, event ):
        "Start a new link."
        if event.widget not in self.widgetToItem:
            # Didn't click on a node
            return

        w = event.widget
        item = self.widgetToItem[ w ]
        x, y = self.canvas.coords( item )
        self.link = self.canvas.create_line( x, y, x, y, width=4,
                                             fill='blue', tag='link' )
        self.linkx, self.linky = x, y
        self.linkWidget = w
        self.linkItem = item

    def finishLink( self, event ):
        "Finish creating a link"
        if self.link is None:
            return
        source = self.linkWidget
        c = self.canvas
        # Since we dragged from the widget, use root coords
        x, y = self.canvasx( event.x_root ), self.canvasy( event.y_root )
        target = self.findItem( x, y )
        dest = self.itemToWidget.get( target, None )
        if ( source is None or dest is None or source == dest
                or dest in source.links or source in dest.links ):
            self.releaseNetLink( event )
            return
        # For now, don't allow hosts to be directly linked
        stags = self.canvas.gettags( self.widgetToItem[ source ] )
        dtags = self.canvas.gettags( target )
        #if (('Host' in stags and 'Host' in dtags)):
            #self.releaseNetLink( event )
            #return

        # Set link type
        linkType='data'

        self.createDataLinkBindings()
        c.itemconfig(self.link, tags=c.gettags(self.link)+(linkType,))

        x, y = c.coords( target )
        c.coords( self.link, self.linkx, self.linky, x, y )
        self.addLink( source, dest, linktype=linkType )

        # We're done
        self.link = self.linkWidget = None

    # Menu handlers

    def about( self ):
        "Display about box."
        about = self.aboutBox
        if about is None:
            bg = 'white'
            about = Toplevel( bg='white' )
            about.title( 'About' )
            info = self.appName + ': a simple network editor for MiniNDN - based on Miniedit'
            warning = 'Development version - not entirely functional!'
            #version = 'MiniEdit '+MINIEDIT_VERSION
            author = 'Vince Lehman, Jan 2015'
            author2 = 'Ashlesh Gawande, Jan 2015'
            author3 = 'Carlos Cabral, Jan 2013'
            author4 = 'Caio Elias, Nov 2014'
            author5 = 'Originally by: Bob Lantz <rlantz@cs>, April 2010'
            enhancements = 'Enhancements by: Gregory Gee, Since July 2013'
            www = 'http://gregorygee.wordpress.com/category/miniedit/'
            line1 = Label( about, text=info, font='Helvetica 10 bold', bg=bg )
            line2 = Label( about, text=warning, font='Helvetica 9', bg=bg )
            line3 = Label( about, text=author, font='Helvetica 9', bg=bg )
            line4 = Label( about, text=author2, font='Helvetica 9', bg=bg )
            line5 = Label( about, text=author3, font='Helvetica 9', bg=bg )
            line6 = Label( about, text=author4, font='Helvetica 9', bg=bg )
            line7 = Label( about, text=author5, font='Helvetica 9', bg=bg )
            line8 = Label( about, text=enhancements, font='Helvetica 9', bg=bg )
            line9 = Entry( about, font='Helvetica 9', bg=bg, width=len(www), justify=CENTER )


            line9.insert(0, www)
            line9.configure(state='readonly')
            line1.pack( padx=20, pady=10 )
            line2.pack(pady=10 )
            line3.pack(pady=10 )
            line4.pack(pady=10 )
            line5.pack(pady=10 )
            line6.pack(pady=10 )
            line7.pack(pady=10 )
            line8.pack(pady=10 )
            line9.pack(pady=10 )
            hide = ( lambda about=about: about.withdraw() )
            self.aboutBox = about
            # Hide on close rather than destroying window
            Wm.wm_protocol( about, name='WM_DELETE_WINDOW', func=hide )
        # Show (existing) window
        about.deiconify()

    def createToolImages( self ):
        "Create toolbar (and icon) images."

    def hostDetails( self, _ignore=None ):
        if ( self.selection is None or
             self.net is not None or
             self.selection not in self.itemToWidget ):
            return
        widget = self.itemToWidget[ self.selection ]
        name = widget[ 'text' ]
        tags = self.canvas.gettags( self.selection )

        #print tags
        if 'Host' in tags:

                prefDefaults = self.hostOpts[name]
                hostBox = HostDialog(self, title='Host Details', prefDefaults=prefDefaults, isRouter='False')
                self.master.wait_window(hostBox.top)
                if hostBox.result:
                    newHostOpts = {'nodeNum':self.hostOpts[name]['nodeNum']}

                    if len(hostBox.result['startCommand']) > 0:
                        newHostOpts['startCommand'] = hostBox.result['startCommand']
                    if hostBox.result['cpu']:
                        newHostOpts['cpu'] = hostBox.result['cpu']
                    if hostBox.result['mem']:
                        newHostOpts['mem'] = hostBox.result['mem']
                    if len(hostBox.result['hostname']) > 0:
                        newHostOpts['hostname'] = hostBox.result['hostname']
                        name = hostBox.result['hostname']
                        widget[ 'text' ] = name
                    if len(hostBox.result['cache']) > 0:
                        newHostOpts['cache'] = hostBox.result['cache']
                    if len(hostBox.result['fibEntries']) > 0:
                        newHostOpts['fibEntries'] = hostBox.result['fibEntries']

                    newHostOpts['nlsr'] = hostBox.nlsrFrame.getValues()

                    self.hostOpts[name] = newHostOpts

                    print 'New host details for ' + name + ' = ' + str(newHostOpts)

        elif 'LegacyRouter' in tags:

                prefDefaults = self.routerOpts[name]
                hostBox = HostDialog(self, title='Router Details', prefDefaults=prefDefaults, isRouter='True')
                self.master.wait_window(hostBox.top)
                if hostBox.result:
                    newRouterOpts = {'nodeNum':self.routerOpts[name]['nodeNum']}

                    if hostBox.result['cpu']:
                        newRouterOpts['cpu'] = hostBox.result['cpu']
                    if hostBox.result['mem']:
                        newRouterOpts['mem'] = hostBox.result['mem']
                    if len(hostBox.result['hostname']) > 0:
                        newRouterOpts['hostname'] = hostBox.result['hostname']
                        name = hostBox.result['hostname']
                        widget[ 'text' ] = name
                    if len(hostBox.result['cache']) > 0:
                        newRouterOpts['cache'] = hostBox.result['cache']
                    if len(hostBox.result['fibEntries']) > 0:
                        newRouterOpts['fibEntries'] = hostBox.result['fibEntries']
                    self.routerOpts[name] = newRouterOpts

                    print 'New host details for ' + name + ' = ' + str(newRouterOpts)

    def linkDetails( self, _ignore=None ):
        if ( self.selection is None or
             self.net is not None):
            return
        link = self.selection

        linkDetail =  self.links[link]
        src = linkDetail['src']
        dest = linkDetail['dest']
        linkopts = linkDetail['linkOpts']
        linkBox = LinkDialog(self, title='Link Details', linkDefaults=linkopts)
        if linkBox.result is not None:
            linkDetail['linkOpts'] = linkBox.result
            print 'New link details = ' + str(linkBox.result)

    # Model interface
    #
    # Ultimately we will either want to use a topo or
    # mininet object here, probably.

    def addLink( self, source, dest, linktype='data', linkopts={} ):
        "Add link to model."
        source.links[ dest ] = self.link
        dest.links[ source ] = self.link
        self.links[ self.link ] = {'type' :linktype,
                                   'src':source,
                                   'dest':dest,
                                   'linkOpts':linkopts}

    def deleteLink( self, link ):
        "Delete link from model."
        pair = self.links.get( link, None )
        if pair is not None:
            source=pair['src']
            dest=pair['dest']
            del source.links[ dest ]
            del dest.links[ source ]
            stags = self.canvas.gettags( self.widgetToItem[ source ] )
            dtags = self.canvas.gettags( self.widgetToItem[ dest ] )
            ltags = self.canvas.gettags( link )

        if link is not None:
            del self.links[ link ]

    def deleteNode( self, item ):
        "Delete node (and its links) from model."

        widget = self.itemToWidget[ item ]
        tags = self.canvas.gettags(item)

        for link in widget.links.values():
            # Delete from view and model
            self.deleteItem( link )
        del self.itemToWidget[ item ]
        del self.widgetToItem[ widget ]

    def do_linkPopup(self, event):
        # display the popup menu
        if ( self.net is None ):
            try:
                self.linkPopup.tk_popup(event.x_root, event.y_root)
            finally:
                # make sure to release the grab (Tk 8.0a1 only)
                self.linkPopup.grab_release()

    def do_legacyRouterPopup(self, event):
        # display the popup menu
        if ( self.net is None ):
            try:
                self.legacyRouterPopup.tk_popup(event.x_root, event.y_root)
            finally:
                # make sure to release the grab (Tk 8.0a1 only)
                self.legacyRouterPopup.grab_release()

    def do_hostPopup(self, event):
        # display the popup menu
        if ( self.net is None ):
                try:
                    self.hostPopup.tk_popup(event.x_root, event.y_root)
                    isHostPopup = True
                finally:
                    # make sure to release the grab (Tk 8.0a1 only)
                    self.hostPopup.grab_release()

    def xterm( self, _ignore=None ):
        "Make an xterm when a button is pressed."
        if ( self.selection is None or
             self.net is None or
             self.selection not in self.itemToWidget ):
            return
        name = self.itemToWidget[ self.selection ][ 'text' ]
        if name not in self.net.nameToNode:
            return
        term = makeTerm( self.net.nameToNode[ name ], 'Host', term=self.appPrefs['terminalType'] )
        if StrictVersion(MININET_VERSION) > StrictVersion('2.0'):
            self.net.terms += term
        else:
            self.net.terms.append(term)

    def iperf( self, _ignore=None ):
        "Make an xterm when a button is pressed."
        if ( self.selection is None or
             self.net is None or
             self.selection not in self.itemToWidget ):
            return
        name = self.itemToWidget[ self.selection ][ 'text' ]
        if name not in self.net.nameToNode:
            return
        self.net.nameToNode[ name ].cmd( 'iperf -s -p 5001 &' )

    """ BELOW HERE IS THE TOPOLOGY IMPORT CODE """

    def parseArgs( self ):
        """Parse command-line args and return options object.
           returns: opts parse options dict"""

        if '--custom' in sys.argv:
            index = sys.argv.index( '--custom' )
            if len( sys.argv ) > index + 1:
                filename = sys.argv[ index + 1 ]
                self.parseCustomFile( filename )
            else:
                raise Exception( 'Custom file name not found' )

        desc = ( "The %prog utility creates Minindn network from the\n"
                 "command line. It can create parametrized topologies,\n"
                 "invoke the Minindn CLI, and run tests." )

        usage = ( '%prog [options] [template_file]\n'
                  '\nIf no template_file is given, generated template will be written to the file minindn.conf in the current directory.\n'
                  'Type %prog -h for details)' )

        opts = OptionParser( description=desc, usage=usage )

        addDictOption( opts, TOPOS, TOPODEF, 'topo' )
        addDictOption( opts, LINKS, LINKDEF, 'link' )

        opts.add_option( '--custom', type='string', default=None,
                         help='read custom topo and node params from .py' +
                         'file' )

        self.options, self.args = opts.parse_args()
        # We don't accept extra arguments after the options
        if self.args:
             if len(self.args) > 1:
                     opts.print_help()
                     exit()
             else:
                     self.template_file=self.args[0]

    def setCustom( self, name, value ):
        "Set custom parameters for MininetRunner."
        if name in ( 'topos', 'switches', 'hosts', 'controllers' ):
            # Update dictionaries
            param = name.upper()
            globals()[ param ].update( value )
        elif name == 'validate':
            # Add custom validate function
            self.validate = value
        else:
            # Add or modify global variable or class
            globals()[ name ] = value

    def parseCustomFile( self, fileName ):
        "Parse custom file and add params before parsing cmd-line options."
        customs = {}
        if os.path.isfile( fileName ):
            execfile( fileName, customs, customs )
            for name, val in customs.iteritems():
                self.setCustom( name, val )
        else:
            raise Exception( 'could not find custom file: %s' % fileName )

    def importTopo( self ):
        print 'topo='+self.options.topo
        if self.options.topo == 'none':
            return
        self.newTopology()
        topo = buildTopo( TOPOS, self.options.topo )
        link = customConstructor( LINKS, self.options.link )
        importNet = Mininet(topo=topo, build=False, link=link)
        importNet.build()

        c = self.canvas
        rowIncrement = 100
        currentY = 100

        # Add switches
        print 'switches:'+str(len(importNet.switches))
        columnCount = 0
        for switch in importNet.switches:
            name = switch.name
            self.switchOpts[name] = {}
            self.switchOpts[name]['nodeNum']=self.switchCount
            self.switchOpts[name]['hostname']=name
            self.switchOpts[name]['switchType']='default'
            self.switchOpts[name]['controllers']=[]

            x = columnCount*100+100
            self.addNode('Switch', self.switchCount,
                 float(x), float(currentY), name=name)
            icon = self.findWidgetByName(name)
            icon.bind('<Button-3>', self.do_switchPopup )

            if columnCount == 9:
                columnCount = 0
                currentY = currentY + rowIncrement
            else:
                columnCount =columnCount+1

        currentY = currentY + rowIncrement
        # Add hosts
        print 'hosts:'+str(len(importNet.hosts))
        columnCount = 0
        for host in importNet.hosts:
            name = host.name
            self.hostOpts[name] = {'sched':'host'}
            self.hostOpts[name]['nodeNum']=self.hostCount
            self.hostOpts[name]['hostname']=name
            #self.hostOpts[name]['ip']=host.IP()

            x = columnCount*100+100
            self.addNode('Host', self.hostCount,
                 float(x), float(currentY), name=name)
            icon = self.findWidgetByName(name)
            icon.bind('<Button-3>', self.do_hostPopup )
            if columnCount == 9:
                columnCount = 0
                currentY = currentY + rowIncrement
            else:
                columnCount =columnCount+1

        print 'links:'+str(len(topo.links()))
        #[('h1', 's3'), ('h2', 's4'), ('s3', 's4')]
        for link in topo.links():
            print str(link)
            srcNode = link[0]
            src = self.findWidgetByName(srcNode)
            sx, sy = self.canvas.coords( self.widgetToItem[ src ] )

            destNode = link[1]
            dest = self.findWidgetByName(destNode)
            dx, dy = self.canvas.coords( self.widgetToItem[ dest]  )

            params = topo.linkInfo( srcNode, destNode )
            print 'Link Parameters='+str(params)

            self.link = self.canvas.create_line( sx, sy, dx, dy, width=4,
                                             fill='blue', tag='link' )
            c.itemconfig(self.link, tags=c.gettags(self.link)+('data',))
            self.addLink( src, dest, linkopts=params )
            self.createDataLinkBindings()
            self.link = self.linkWidget = None

        importNet.stop()

def miniEditImages():
    "Create and return images for MiniEdit."

    # Image data. Git will be unhappy. However, the alternative
    # is to keep track of separate binary files, which is also
    # unappealing.

    return {
        'Select': BitmapImage(
            file='/usr/include/X11/bitmaps/left_ptr' ),

        'LegacyRouter': PhotoImage( data=r"""
            R0lGODlhMgAYAPcAAAEBAXZ8gQNAgL29vQNctjl/xVSa4j1dfCF+
            3QFq1DmL3wJMmAMzZZW11dnZ2SFrtyNdmTSO6gIZMUKa8gJVqEOH
            zR9Pf5W74wFjxgFx4jltn+np6Eyi+DuT6qKiohdtwwUPGWiq6ymF
            4LHH3Rh11CV81kKT5AMoUA9dq1ap/mV0gxdXlytRdR1ptRNPjTt9
            vwNgvwJZsX+69gsXJQFHjTtjizF0tvHx8VOm9z2V736Dhz2N3QM2
            acPZ70qe8gFo0HS19wVRnTiR6hMpP0eP1i6J5iNlqAtgtktjfQFu
            3TNxryx4xAMTIzOE1XqAh1uf5SWC4AcfNy1XgQJny93n8a2trRh3
            12Gt+VGm/AQIDTmByAF37QJasydzvxM/ayF3zhdLf8zLywFdu4i5
            6gFlyi2J4yV/1w8wUo2/8j+X8D2Q5Eee9jeR7Uia7DpeggFt2QNP
            m97e3jRong9bpziH2DuT7aipqQoVICmG45vI9R5720eT4Q1hs1er
            /yVVhwJJktPh70tfdbHP7Xev5xs5V7W1sz9jhz11rUVZcQ9WoCVV
            hQk7cRdtwWuw9QYOFyFHbSBnr0dznxtWkS18zKfP9wwcLAMHCwFF
            iS5UeqGtuRNNiwMfPS1hlQMtWRE5XzGM5yhxusLCwCljnwMdOFWh
            7cve8pG/7Tlxp+Tr8g9bpXF3f0lheStrrYu13QEXLS1ppTV3uUuR
            1RMjNTF3vU2X4TZupwRSolNne4nB+T+L2YGz4zJ/zYe99YGHjRdD
            cT95sx09XQldsgMLEwMrVc/X3yN3yQ1JhTRbggsdMQNfu9HPz6Wl
            pW2t7RctQ0GFyeHh4dvl8SBZklCb5kOO2kWR3Vmt/zdjkQIQHi90
            uvPz8wIVKBp42SV5zbfT7wtXpStVfwFWrBVvyTt3swFz5kGBv2+1
            /QlbrVFjdQM7d1+j54i67UmX51qn9i1vsy+D2TuR5zddhQsjOR1t
            u0GV6ghbsDVZf4+76RRisent8Xd9hQFBgwFNmwJLlcPDwwFr1z2T
            5yH5BAEAAAAALAAAAAAyABgABwj/AAEIHEiQYJY7Qwg9UsTplRIb
            ENuxEiXJgpcz8e5YKsixY8Essh7JcbbOBwcOa1JOmJAmTY4cHeoI
            abJrCShI0XyB8YRso0eOjoAdWpciBZajJ1GuWcnSZY46Ed5N8hPA
            TqEBoRB9gVJsxRlhPwHI0kDkVywcRpGe9LF0adOnMpt8CxDnxg1o
            9lphKoEACoIvmlxxvHOKVg0n/Tzku2WoVoU2J1P6WNkSrtwADuxC
            G/MOjwgRUEIjGG3FhaOBzaThiDSCil27G8Isc3LLjZwXsA6YYJmD
            jhTMmseoKQIFDx7RoxHo2abnwygAlUj1mV6tWjlelEpRwfd6gzI7
            VeJQ/2vZoVaDUqigqftXpH0R46H9Kl++zUo4JnKq9dGvv09RHFhc
            IUMe0NiFDyql0OJUHWywMc87TXRhhCRGiHAccvNZUR8JxpDTH38p
            9HEUFhxgMSAvjbBjQge8PSXEC6uo0IsHA6gAAShmgCbffNtsQwIJ
            ifhRHX/TpUUiSijlUk8AqgQixSwdNBjCa7CFoVggmEgCyRf01WcF
            CYvYUgB104k4YlK5HONEXXfpokYdMrXRAzMhmNINNNzB9p0T57Ag
            yZckpKKPGFNgw06ZWKR10jTw6MAmFWj4AJcQQkQQwSefvFeGCemM
            IQggeaJywSQ/wgHOAmJskQEfWqBlFBEH1P/QaGY3QOpDZXA2+A6m
            7hl3IRQKGDCIAj6iwE8yGKC6xbJv8IHNHgACQQybN2QiTi5NwdlB
            pZdiisd7vyanByOJ7CMGGRhgwE+qyy47DhnBPLDLEzLIAEQjBtCh
            RmVPNWgpr+Be+Nc9icARww9TkIEuDAsQ0O7DzGIQzD2QdDEJHTsI
            AROc3F7qWQncyHPPHN5QQAAG/vjzw8oKp8sPPxDH3O44/kwBQzLB
            xBCMOTzzHEMMBMBARgJvZJBBEm/4k0ACKydMBgwYoKNNEjJXbTXE
            42Q9jtFIp8z0Dy1jQMA1AGziz9VoW7310V0znYDTGMQgwUDXLDBO
            2nhvoTXbbyRk/XXL+pxWkAT8UJ331WsbnbTSK8MggDZhCTOMLQkc
            jvXeSPedAAw0nABWWARZIgEDfyTzxt15Z53BG1PEcEknrvgEelhZ
            MDHKCTwI8EcQFHBBAAFcgGPLHwLwcMIo12Qxu0ABAQA7
            """),

        'Host': PhotoImage( data=r"""
            R0lGODlhIAAYAPcAMf//////zP//mf//Zv//M///AP/M///MzP/M
            mf/MZv/MM//MAP+Z//+ZzP+Zmf+ZZv+ZM/+ZAP9m//9mzP9mmf9m
            Zv9mM/9mAP8z//8zzP8zmf8zZv8zM/8zAP8A//8AzP8Amf8AZv8A
            M/8AAMz//8z/zMz/mcz/Zsz/M8z/AMzM/8zMzMzMmczMZszMM8zM
            AMyZ/8yZzMyZmcyZZsyZM8yZAMxm/8xmzMxmmcxmZsxmM8xmAMwz
            /8wzzMwzmcwzZswzM8wzAMwA/8wAzMwAmcwAZswAM8wAAJn//5n/
            zJn/mZn/Zpn/M5n/AJnM/5nMzJnMmZnMZpnMM5nMAJmZ/5mZzJmZ
            mZmZZpmZM5mZAJlm/5lmzJlmmZlmZplmM5lmAJkz/5kzzJkzmZkz
            ZpkzM5kzAJkA/5kAzJkAmZkAZpkAM5kAAGb//2b/zGb/mWb/Zmb/
            M2b/AGbM/2bMzGbMmWbMZmbMM2bMAGaZ/2aZzGaZmWaZZmaZM2aZ
            AGZm/2ZmzGZmmWZmZmZmM2ZmAGYz/2YzzGYzmWYzZmYzM2YzAGYA
            /2YAzGYAmWYAZmYAM2YAADP//zP/zDP/mTP/ZjP/MzP/ADPM/zPM
            zDPMmTPMZjPMMzPMADOZ/zOZzDOZmTOZZjOZMzOZADNm/zNmzDNm
            mTNmZjNmMzNmADMz/zMzzDMzmTMzZjMzMzMzADMA/zMAzDMAmTMA
            ZjMAMzMAAAD//wD/zAD/mQD/ZgD/MwD/AADM/wDMzADMmQDMZgDM
            MwDMAACZ/wCZzACZmQCZZgCZMwCZAABm/wBmzABmmQBmZgBmMwBm
            AAAz/wAzzAAzmQAzZgAzMwAzAAAA/wAAzAAAmQAAZgAAM+4AAN0A
            ALsAAKoAAIgAAHcAAFUAAEQAACIAABEAAADuAADdAAC7AACqAACI
            AAB3AABVAABEAAAiAAARAAAA7gAA3QAAuwAAqgAAiAAAdwAAVQAA
            RAAAIgAAEe7u7t3d3bu7u6qqqoiIiHd3d1VVVURERCIiIhEREQAA
            ACH5BAEAAAAALAAAAAAgABgAAAiNAAH8G0iwoMGDCAcKTMiw4UBw
            BPXVm0ixosWLFvVBHFjPoUeC9Tb+6/jRY0iQ/8iVbHiS40CVKxG2
            HEkQZsyCM0mmvGkw50uePUV2tEnOZkyfQA8iTYpTKNOgKJ+C3AhO
            p9SWVaVOfWj1KdauTL9q5UgVbFKsEjGqXVtP40NwcBnCjXtw7tx/
            C8cSBBAQADs=
        """ ),

        'NetLink': PhotoImage( data=r"""
            R0lGODlhFgAWAPcAMf//////zP//mf//Zv//M///AP/M///MzP/M
            mf/MZv/MM//MAP+Z//+ZzP+Zmf+ZZv+ZM/+ZAP9m//9mzP9mmf9m
            Zv9mM/9mAP8z//8zzP8zmf8zZv8zM/8zAP8A//8AzP8Amf8AZv8A
            M/8AAMz//8z/zMz/mcz/Zsz/M8z/AMzM/8zMzMzMmczMZszMM8zM
            AMyZ/8yZzMyZmcyZZsyZM8yZAMxm/8xmzMxmmcxmZsxmM8xmAMwz
            /8wzzMwzmcwzZswzM8wzAMwA/8wAzMwAmcwAZswAM8wAAJn//5n/
            zJn/mZn/Zpn/M5n/AJnM/5nMzJnMmZnMZpnMM5nMAJmZ/5mZzJmZ
            mZmZZpmZM5mZAJlm/5lmzJlmmZlmZplmM5lmAJkz/5kzzJkzmZkz
            ZpkzM5kzAJkA/5kAzJkAmZkAZpkAM5kAAGb//2b/zGb/mWb/Zmb/
            M2b/AGbM/2bMzGbMmWbMZmbMM2bMAGaZ/2aZzGaZmWaZZmaZM2aZ
            AGZm/2ZmzGZmmWZmZmZmM2ZmAGYz/2YzzGYzmWYzZmYzM2YzAGYA
            /2YAzGYAmWYAZmYAM2YAADP//zP/zDP/mTP/ZjP/MzP/ADPM/zPM
            zDPMmTPMZjPMMzPMADOZ/zOZzDOZmTOZZjOZMzOZADNm/zNmzDNm
            mTNmZjNmMzNmADMz/zMzzDMzmTMzZjMzMzMzADMA/zMAzDMAmTMA
            ZjMAMzMAAAD//wD/zAD/mQD/ZgD/MwD/AADM/wDMzADMmQDMZgDM
            MwDMAACZ/wCZzACZmQCZZgCZMwCZAABm/wBmzABmmQBmZgBmMwBm
            AAAz/wAzzAAzmQAzZgAzMwAzAAAA/wAAzAAAmQAAZgAAM+4AAN0A
            ALsAAKoAAIgAAHcAAFUAAEQAACIAABEAAADuAADdAAC7AACqAACI
            AAB3AABVAABEAAAiAAARAAAA7gAA3QAAuwAAqgAAiAAAdwAAVQAA
            RAAAIgAAEe7u7t3d3bu7u6qqqoiIiHd3d1VVVURERCIiIhEREQAA
            ACH5BAEAAAAALAAAAAAWABYAAAhIAAEIHEiwoEGBrhIeXEgwoUKG
            Cx0+hGhQoiuKBy1irChxY0GNHgeCDAlgZEiTHlFuVImRJUWXEGEy
            lBmxI8mSNknm1Dnx5sCAADs=
        """ )
    }

def addDictOption( opts, choicesDict, default, name, helpStr=None ):
    """Convenience function to add choices dicts to OptionParser.
       opts: OptionParser instance
       choicesDict: dictionary of valid choices, must include default
       default: default choice key
       name: long option name
       help: string"""
    if default not in choicesDict:
        raise Exception( 'Invalid  default %s for choices dict: %s' %
                         ( default, name ) )
    if not helpStr:
        helpStr = ( '|'.join( sorted( choicesDict.keys() ) ) +
                    '[,param=value...]' )
    opts.add_option( '--' + name,
                     type='string',
                     default = default,
                     help = helpStr )

if __name__ == '__main__':
    setLogLevel( 'info' )
    app = MiniEdit()
    """ import topology if specified """
    app.parseArgs()
    app.importTopo()

    global isHostPopup
    global isRouterPopup
    global isLinkPopup

    app.mainloop()
