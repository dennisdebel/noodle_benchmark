# noodle benchmark tool 0.2
#
# usage:
#
# open two terminal windows in one transmit the minimodem man page using minimodem:
# e.g.  $ man minimodem | minimodem -t 200 
# 
# in the second terminal window pipe a recieving minimodem into this benchmarkt tool like:
#       $ minimodem -r  200 | python noodle_benchmark.py 
#
# pres start to start, in i3 window manager hit special+shift+space to float the window

import wx, time, sys

from threading import Thread
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub

time.time()

test = 0
start_time = time.time()
current_size = 0
total_size = 8341 # wordcount (wc) of minimodem man page
start_listening = False

class MyFrame(wx.Frame):
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title,size=(800, 500)) #set size so that everything is in view (in i3 hit special+shift+space to float the window)
        global test
        self.count = 0
        self.initUI()
        
        #self.stdin parser
        #self.uiUpdater
        self.thread = stream_listener()


    def initUI(self):
        self.panel = wx.Panel(self)

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(18)

        #one vertical container
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        #with several horizontal ones

        #top label
        label_box = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self.panel, wx.ID_ANY, label='Noodle Transfer Speed Benchmarking Tool')#, style=wx.ALIGN_CENTRE)
        label_box.Add(st1, 0, wx.ALL, 5)

        #buttons
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        startBtn = wx.Button(self.panel, wx.ID_ANY, 'Start Benchmark')
        stopBtn = wx.Button(self.panel, wx.ID_ANY, 'Stop')
        self.Bind(wx.EVT_BUTTON, self.exit, stopBtn)
        self.Bind(wx.EVT_BUTTON, self.start, startBtn)
        button_box.Add(startBtn, 0, wx.EXPAND | wx.RIGHT, 200)
        button_box.Add(stopBtn, 0, wx.EXPAND | wx.LEFT, 200)

        #transfer animation
        animation_box = wx.BoxSizer(wx.HORIZONTAL)
        self.image = wx.StaticBitmap(self.panel, bitmap=wx.EmptyBitmap(807, 210))
        #load the next/first frame
        self.DisplayNextFrame()

        animation_box.Add(self.image, 0, wx.ALL, 5)

        #statistics
        stat_box = wx.BoxSizer(wx.VERTICAL)
        # self.statistics = wx.TextCtrl(self.panel, wx.ID_ANY, style=wx.TE_READONLY) #looks bad
        # self.statistics.SetEditable(False)
        # stat_box.Add(self.statistics, 0, wx.ALL,5)


        #transfer speed
        self.transfer_speed = wx.StaticText(self.panel, wx.ID_ANY, label="Transfer speed: 51kbs")
        self.transfer_speed.SetFont(font)
        stat_box.Add(self.transfer_speed, 0, wx.ALL,5)

        #progress bar
        self.percent_complete = wx.StaticText(self.panel, wx.ID_ANY, label="Transfer total: 0%")
        self.percent_complete.SetFont(font)
        stat_box.Add(self.percent_complete, 0, wx.ALL,5)

         #time left time
        self.time_remaining = wx.StaticText(self.panel, wx.ID_ANY, label="Time remaining: 304 seconds")
        self.time_remaining.SetFont(font)
        stat_box.Add(self.time_remaining, 0, wx.ALL,5)

        #running time
        self.time_running = wx.StaticText(self.panel, wx.ID_ANY, label="Time elapsed: 34 seconds")
        self.time_running.SetFont(font)
        stat_box.Add(self.time_running, 0, wx.ALL,5)



        pub.subscribe(self.update_statistics, "update")
        
    


        #add all the horizontal containers to the vertical one
        vbox.Add(label_box, 0, wx.CENTER)
        vbox.Add(button_box, 0, wx.CENTER)
        vbox.Add(animation_box,0, wx.CENTER)
        vbox.Add(stat_box,0, wx.CENTER)



        self.panel.SetSizer(vbox)

    def exit(self, event):
        print "Closing.."
        global start_listening
        start_listening = False
        self.Close()
        self.thread.join()
        sys.stdout.flush()
        sys.exit()
        

    def start(self, event):
        print 'started'
        global start_listening
        start_listening = True
    def update_statistics(self,msg):
        current_size = msg[0]
        total_size =msg[1]
        percent_complete = self.percentage(msg[0],msg[1])
        time_elapsed =str(msg[2])
        bps = msg[3]
        time_remaining = (total_size-current_size)/bps 

        self.transfer_speed.SetLabel('Transfer speed: '+str(bps)+' bytes per second')
        self.time_running.SetLabel('Time running: '+time_elapsed+' seconds')
        self.percent_complete.SetLabel('Transfer total: '+str(round(percent_complete,2))+'%')
        self.time_remaining.SetLabel('Time remaining: '+str(round(time_remaining,1))+' seconds')

        self.DisplayNextFrame()
        self.Refresh()

    def percentage(self,part, whole):
        return 100 * float(part)/float(whole)

    def DisplayNextFrame(self, event=None):
        #cycles through animation frames
        # load the image
        Img = wx.Image('frames/'+'{:05}'.format(self.count)+'.png', wx.BITMAP_TYPE_ANY)

        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        self.image.SetBitmap(wx.BitmapFromImage(Img))
        if self.count >= 17:
            self.count = 0
        else:
            self.count +=1
        self.Refresh()

########################################################################

class stream_listener(Thread):
    """Thread To listen to STDIN"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Init Worker Thread Class."""
        Thread.__init__(self)
       
        self.start()    # start the thread
        

    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.

        global start_time
        global current_size
        global total_size
        global start_listening

        current_size_old =0

        while True:
            
            if start_listening: #listen to the button
                

                time.sleep(0.1)
                
                input_stream = sys.stdin.read(1)
                if len(input_stream):
                    # print (len(input_stream))
                    for character in input_stream:
                        current_size += len(character)
                        print current_size, input_stream #also print characters
                    input_stream = 0
                else:
                    print('no stream')
                wx.CallAfter(pub.sendMessage, "update", msg=self.report(start_time, current_size, total_size))
                # if current_size == total_size:
                #     print('\nTransfer complete!')
                #     sys.stdout.flush()


                        #sys.exit()
            # except KeyboardInterrupt:
            #     sys.stdout.flush()
            #     pass



    def report(self, start, current_size, total_size):
        time_elapsed = time.time() - start_time
        bps = current_size/time_elapsed
        # print ("Transferred: {}% ({} of {}),  time elapsed: {}, current_speed  {} Bps".format(str(int(percentage(current_size, total_size))), current_size, total_size, round(time_elapsed,1), round(bps,1)))
        # print current_size, total_size, round(time_elapsed,1), round(bps,1)
        return(current_size, total_size, round(time_elapsed,1), round(bps,1))


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, -1, "Noodle Benchmark")
    frame.Show()
    app.MainLoop()