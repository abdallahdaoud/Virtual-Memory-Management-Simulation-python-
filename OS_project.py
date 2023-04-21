import platform
import math
import random
from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
from tkinter import filedialog
from time import *  # for alert in testing
from threading import *
import winsound  # for alert in testing


class f:
    FilePath = "generated__config.txt"


class mainWindow:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''

        top.geometry("1112x540")
        top.resizable(False, False)
        top.title("Virtual Memory Management Simulation (ENCS3390)")
        top.configure(background="#d9d9d9")

        self.top = top
        self.combobox = tk.StringVar()
        self.style = ttk.Style()

        self.Label1 = tk.Label(self.top)
        self.Label1.configure(
            anchor='w', background="#d9d9d9", text="Choose An Algorithm" , font=("", 11)) 
        # relx and rely Horizontal and vertical offset as a float between 0.0 and 1.0, as a fraction of the height and width of the parent widget.
        self.Label1.place(relx=0.589, rely=0.056, height=20, width=155)

        algorithmSelection = tk.StringVar()
        self.TCombobox1 = ttk.Combobox(
            self.top, width=27, textvariable=algorithmSelection)
        self.TCombobox1.place(relx=0.745, rely=0.056,
                              relheight=0.039, relwidth=0.221)
        self.TCombobox1.configure(textvariable=self.combobox, state="readonly")

        # Adding combobox drop down list
        self.TCombobox1['values'] = ('FIFO', 'LRU', 'Second Chance')
        self.TCombobox1.current(0)

        self.Label2 = tk.Label(self.top)
        self.Label2.configure(anchor='w', background="#d9d9d9",
                              text="Simulation Results (display the changes on the system)", font=("", 11))
        self.Label2.place(relx=0.012, rely=0.150, height=23, width=400)

        self.TLabel1 = ttk.Label(self.top)
        self.TLabel1.configure(anchor='w', background="#d9d9d9",
                               text="You can either use an exist file or generate a random one", font=("", 11))
        self.TLabel1.place(relx=0.012, rely=0.040, height=35, width=440)

        self.generate_button = tk.Button(self.top)
        self.generate_button.configure(background="#c0c0c0", cursor="star", text="Generate Random File",
                                       relief="groove", command=generation)
        self.generate_button.place(
            relx=0.397, rely=0.074, height=24, width=137)

        self.exist = tk.Button(self.top)
        self.exist.configure(background="#c0c0c0", cursor="based_arrow_down", text="Open An Existing File",
                             relief="groove", command=openFile)
        self.exist.place(relx=0.397, rely=0.019, height=24, width=137)

        self.RUN_BUTTON = ttk.Button(self.top)
        self.style.configure("TButton", font=("", 10))
        self.RUN_BUTTON.place(relx=0.865, rely=0.111, height=45, width=86)
        self.RUN_BUTTON.configure(text="RUN!", command=self.runSimulation)

        self.style.configure('Treeview', font=("Andalus", 11))
        self.memContents = ScrolledTreeView(self.top)
        self.memContents.place(relx=0.012, rely=0.207,
                               relheight=0.778, relwidth=0.975)

        # build_treeview_support starting.
        self.memContents['columns'] = (
            "Col1", "Col2", "Col3", "Col4", "Col5", "Col6")
        self.memContents.heading("#0", text="", anchor="w")
        self.memContents.column("#0", width=0, stretch=NO)

        # style = ttk.Style() 
        self.style.configure("Treeview.Heading", font=(None, 10))
        self.memContents.heading("Col1", text="Cycles", anchor="w")
        self.memContents.heading("Col2", text="Blocked Queue", anchor="w")
        self.memContents.heading("Col3", text="Job Queue", anchor="w")
        self.memContents.heading("Col4", text="Ready Queue", anchor="w")
        self.memContents.heading("Col5", text="Process In Threads", anchor="w")
        self.memContents.heading("Col6", text="Available Frames", anchor="w")

        self.memContents.column("Col1", width="100",
                                anchor="w", minwidth="50")
        self.memContents.column("Col2", width="210", anchor="w", minwidth="50") 
        self.memContents.column("Col3", width="220", anchor="w", minwidth="50")
        self.memContents.column("Col4", width="220", anchor="w", minwidth="50")
        self.memContents.column("Col5", width="220", anchor="w", minwidth="50")
        self.memContents.column("Col6", width="110", anchor="w", minwidth="50")

################################## The simulation ##################################
    def main_test(self, threadsNumber, quantum):
        t = time()  # for testing

        # Contains general variables and functions
        cycles = 0

        class Shared:  # to access from memory thread and modify it's value
            numOfProcesses = 0  # changed when read file
            memorySizeByFrame = 0  # changed when read file
            availableFrames = 0  # changed when read file
            maxAvailableFrames = 0  # changed when read file
            minFramesPerProcess = 0  # changed when read file
            turnOff = False  # to kill threads
            preStatus = ''  # the system previous status to ptint the changes only
            memoryChange = False  # lock from memory manager thread to have proper results
            pageFaultCounter = 0  # used to count number of page faults
            Hits = 0  # used to count number of memory hits

        newProcesses = []  # all processes that there arrival time not become
        # new ####### # processes that the system cannot provide them with minimum needed frames
        blockedQueue = []
        jobQueue = []  # here processes stay after page fult until get there pages
        readyQueue = []  # here all ready processes to be execute wait it's turn
        processOnThread = []  # processes that executing in threads
        threads = []  # thread ojects
        finishedProcesses = []
        finishedProcessestofreeItsFrames = []
        # for testing
        print(
            "cycles|jobQueue|blockedQueue|readyQueue|processOnThread|availableFrames")

        def readConfig():  # save processes information in Process opjects on newProcesses list
            file = open(f.FilePath, 'r')
            n = int(file.readline())
            Shared.numOfProcesses = n
            ms = int(file.readline()[:-1])
            Shared.memorySizeByFrame = ms
            Shared.availableFrames = ms
            Shared.maxAvailableFrames = ms
            Shared.minFramesPerProcess = int(file.readline())
            temp = file.readline()
            i = 0
            for i in range(n):
                strings = str.split(temp[:-1], ' ')
                traces = strings[4:]
                while(True):
                    if traces[-1] == '':
                        traces.pop()
                    else:
                        break
                traces.reverse()  # .reverse() is because it will be used as a stack later
                newProcesses.append(Process(strings[0], int(
                    strings[1]), int(strings[2]), int(strings[3]), traces))
                i += 1
                temp = file.readline()

        # to get smaller start time first by .pop()
        def sortProcessesByStartTime(processes):
            i = len(processes)
            while(i > 1):
                for j in range(1, i):
                    if processes[j].start > processes[j-1].start:
                        temp = processes[j]
                        processes[j] = processes[j-1]
                        processes[j-1] = temp
                i -= 1

        def trackAll():
            line = ''
            for process in blockedQueue:
                line += str(process.pid) + ','
            line += '|'
            for process in jobQueue:
                line += str(process.pid) + ','
            line += '|'
            l = len(readyQueue)
            if l > threadsNumber - 2:
                rq = l - threadsNumber + 2
                l = threadsNumber - 2
                for i in range(0, rq):
                    line += str(readyQueue[i].pid) + ','
            line += '|'
            for i in range(-l, 0):
                line += str(readyQueue[i].pid) + ','
            line += '|' + str(Shared.availableFrames)
            if Shared.preStatus != line:
                print(str(cycles) + '|' + line)  # for testing
                Shared.preStatus = line
                arr = list(line.split('|'))
                self.memContents.insert(parent='', index='end', text='', values=(str(cycles), list(arr[0][:-1]),
                                                                                 list(arr[1][:-1]), list(arr[2][:-1]), list(arr[3][:-1]), list(arr[4])))
                root.update()

        class Process:
            def __init__(self, pid, start, duration, size, memoryTraces):
                # read from file and fill these variables
                # ,pid, start, duration, size, memoryTraces
                self.pid = pid  # process id
                self.start = start  # arrival time
                self.duration = duration  # process duration by houers on relation with burst time
                self.size = size  # process size by frames
                self.memoryTraces = memoryTraces  # + hex
                self.pageAccesses = []
                self.hasFrames = 0
                # every frame address in page table takes 4 bytes and frame size = 2^12 bytes
                # --> neededFrames = 4*('number of pages in page table'=='process size by frames')/2^12 = size/1024
                self.minNeededFrames = Shared.minFramesPerProcess + math.ceil(
                    self.size/1024)  # ceil, where frames number could be just integer
                for trace in memoryTraces:
                    self.pageAccesses.append(hex(int(trace, 16) >> 12))
                self.pageTable = {}
                for page in self.pageAccesses:  # False means that the page dose not on main memory
                    # [isValid, timeBrought, lastuseTime]
                    self.pageTable[page] = [False, 0, 0]

            def nextPage(self):
                if(len(self.pageAccesses) != 0):
                    return self.pageAccesses[-1]
                return ''  # null string '' means that the process was finished

            def execute(self, i):  # simulate execute instructions on the page (takes 1 cycle)
                Shared.Hits += 1
                self.pageTable[self.pageAccesses[-1]][2] = i
                self.pageAccesses.pop()

            def isInMainMemory(self, page):
                return self.pageTable[page][0]

        ######################  page replacement algorithm section  ######################
        # choose a frame to free then 'just' choosenProcess.pageTable[firstPage] = [False, 0, 0]
        # and choosenProcess.hasFrames -= 1
        # note there no common frames between processes so you have to do that in one process
        def FIFO():
            minTime = math.inf
            queue = [jobQueue[-1]]
            if Shared.maxAvailableFrames > 0:  # we cannot evict a frame from a process if all has just as they need < 0
                # so we just replace a page in the process to another in it --> queue = [jobQueue[-1]]
                # (+ processOnThread) not needed where there not process on it here 
                queue = readyQueue + jobQueue
            for process in queue:
                # we cannot evict a frame from a process if it has just as it need
                if process.hasFrames > process.minNeededFrames or len(queue) < 2:
                    # len(queue) < 2: replace from process itself if we cannot evict from other
                    table = process.pageTable
                    for page in table:
                        if table[page][0] and (table[page][1] < minTime):
                            firstPage = page
                            minTime = table[page][1]
                            firstPageProcess = process
            firstPageProcess.pageTable[firstPage] = [False, 0, 0]
            firstPageProcess.hasFrames -= 1 

        def LRU():
            minTime = math.inf
            queue = [jobQueue[-1]]
            if Shared.maxAvailableFrames > 0:
                queue = readyQueue + jobQueue
            for process in queue:
                if (process.hasFrames > process.minNeededFrames) or (len(queue) < 2):
                    table = process.pageTable
                    for page in table:
                        if table[page][0] and (table[page][2] < minTime):
                            LRUPage = page
                            minTime = table[page][2]
                            firstPageProcess = process
            firstPageProcess.pageTable[LRUPage] = [False, 0, 0]
            firstPageProcess.hasFrames -= 1 

        def secondchance():
            evictPage = ''
            ePageProcess = ''
            queue = [jobQueue[-1]]
            if Shared.maxAvailableFrames > 0:
                queue = readyQueue + jobQueue
            while True:
                for process in queue:
                    if (process.hasFrames > process.minNeededFrames) or (len(queue) < 2):
                        table = process.pageTable
                        for page in table:
                            if table[page][0] and table[page][2] == 0:
                                evictPage = page
                                ePageProcess = process
                                break
                            elif table[page][0]:
                                table[page][2] = 0
                        if evictPage != '':
                            break
                if evictPage != '':
                    break
            ePageProcess.pageTable[evictPage] = [False, 0, 0]
            ePageProcess.hasFrames -= 1 
        ###################################################################################

        def arrivalProcesses():  # put arrival process in blockedQueue
            l = len(newProcesses)
            while l > 0:
                if newProcesses[-1].start <= cycles:  # -1 is the same as l-1
                    blockedQueue.append(newProcesses.pop())
                    l -= 1
                else:
                    break

        def memoryManager(pageReplacementFunction):  # in memory manager thread
            while(True):
                if Shared.turnOff:
                    break  # stop this thread if turnOff flag = True

                # free finished Processes frams because thay will not be used again
                for process in finishedProcessestofreeItsFrames:
                    finishedProcessestofreeItsFrames.pop()
                    Shared.availableFrames += process.hasFrames
                    Shared.maxAvailableFrames += process.minNeededFrames
                
                timer = cycles 
                stop = timer + quantum 
                # go out the loop to see finishedProcessestofreeItsFrames when timer > stop
                # where the scheduler finish
                while len(jobQueue) > 0 and timer < stop:
                    # the cycle that manager get the page on it, to simulate getting the page
                    timer += 300
                    while(timer >= cycles): ########'='pppp
                        Shared.memoryChange = False  # release the lock if getting the page
                    if Shared.availableFrames < 1:
                        pageReplacementFunction()
                        Shared.availableFrames += 1
                    process = jobQueue[-1]
                    process.pageTable[process.nextPage()] = [
                        True, cycles, cycles] #!!!!!!!!!!!!!!!!!!!!!!!!!ppp
                    process.hasFrames += 1
                    if process.hasFrames >= process.minNeededFrames:
                        readyQueue.insert(0, jobQueue.pop())
                    Shared.availableFrames -= 1

                if len(finishedProcessestofreeItsFrames) + len(jobQueue) < 1:
                    Shared.memoryChange = False  # release
        # this method will run in the threads by diffirent argumants(process)

        def runThread(threadNumber):  # run on threads
            while(True):
                if Shared.turnOff:
                    break  # stop this thread if turnOff flag = True
                process = processOnThread[threadNumber]
                if process != True:  # see if there a process to work on
                    for i in range(quantum):  # to simulate working quantum of cycles
                        nextPage = process.nextPage()
                        if nextPage != '':
                            if process.isInMainMemory(nextPage):
                                process.execute(cycles+i) ####
                                if i+1 == quantum:
                                    # if threadNumber > 0: # *
                                    #     while processOnThread[threadNumber-1] != True: pass
                                    readyQueue.insert(0, process)
                            else:
                                # page fault, push the prosses in jobQueue
                                # if threadNumber > 0: # *
                                #     while processOnThread[threadNumber-1] != True: pass
                                jobQueue.insert(0, process)
                                Shared.pageFaultCounter += 1
                                break
                        else:
                            # if threadNumber > 0: # *
                            #     while processOnThread[threadNumber-1] != True: pass
                            finishedProcesses.append(process)  # maybe used
                            # all frames in process won't be accessed by another processes so we decided to free them
                            finishedProcessestofreeItsFrames.insert(0, process)
                            break
                    # tell scheduler that the process go out the thread
                    processOnThread[threadNumber] = True

        ################ Start runing ################
        readConfig()
        sortProcessesByStartTime(newProcesses)

        algo = FIFO
        algotxt = self.TCombobox1.get()
        if algotxt == "LRU":
            algo = LRU
        elif algotxt == "Second Chance":
            algo = secondchance

        memoryThread = Thread(target=memoryManager, args=[algo])
        memoryThread.start()

        for i in range(0, threadsNumber-2):  # set threads and turn on
            # True means there no process to work for the thread
            processOnThread.append(True)
            threads.append(Thread(target=runThread, args=[i]))
            threads[-1].start()

        while(True):  # this loop presents scheduler thread 'Round Robin' scheduler

            arrivalProcesses()  # put arrival processes in blocked queue

            # send processes on blockedQueue to jobQueue to get needed pages if we can provide needed frames to it
            l = len(blockedQueue) 
            for i in range(l):
                minNeededFrames = blockedQueue[-1].minNeededFrames
                if Shared.maxAvailableFrames >= minNeededFrames:
                    # to jobQueue not readyQueue where definitely this process without frames
                    jobQueue.insert(0, blockedQueue.pop())
                    Shared.maxAvailableFrames -= minNeededFrames 

            Shared.memoryChange = True  # lock
            while Shared.memoryChange: pass
            # manager work to get page or do nothing below

            trackAll()  # record the current status

            # if the system finish, then stop all threads and go out the loop
            if (len(newProcesses) + len(blockedQueue) + len(jobQueue) + len(readyQueue)) == 0:
                Shared.turnOff = True
                break

            # do context switch here
            l = len(readyQueue)  # where len(readyQueue) changeable
            if l > threadsNumber-2:
                l = threadsNumber-2
            for i in range(l):
                processOnThread.insert(i, readyQueue.pop())

            # # stay until all threads finished there work
            # while processOnThread[l-1] != True: pass # *
            
            # stay until all threads finished there work
            while(True):
                finished = True
                for finished in processOnThread:
                    if(finished != True):
                        finished = False
                        break
                if finished:
                    break
            # quantum time passed and all threads finished here
            # context switch = 5
            cycles += quantum + 5  # note: after this line memory manager maybe go in critical section

        self.memContents.insert(parent='', index='end', text='',
                                values=(' --- ', ' --- ', ' --- ', ' --- ', ' --- ', ' --- '))
        ###########EDITED###########################
       ###########EDITED###########################
        alert = tk.Toplevel()
        alert.title(algotxt)
        alert.geometry("350x300") 
        alert.resizable(False, False)
        Label(alert, text="\nNumber of threads: " +
              str(threadsNumber)).pack() 
        Label(alert, text="Quantum time: " + str(quantum)).pack()
        Label(alert, text="Number of processes: " +
              str(Shared.numOfProcesses)).pack()
        Label(alert, text="Memory size by frame: " +
              str(Shared.memorySizeByFrame)).pack()
        Label(alert, text="Number of cycles: " + str(cycles)).pack()
        PF = Label(alert, text="Number of Page faults: " +
                   str(Shared.pageFaultCounter)) 
        PF.configure(foreground="Red")
        PF.pack()
        PFR = Label(alert, text="Page Fault Rate: " + str(100 *
                    Shared.pageFaultCounter / (Shared.pageFaultCounter + Shared.Hits))[:5] + "%")
        PFR.configure(foreground="Red")
        PFR.pack()
        NOH = Label(alert, text="Number of hits: " + str(Shared.Hits))
        NOH.configure(foreground="Green")
        NOH.pack()
        HR = Label(alert, text=" Hit Rate: " + str(100 * Shared.Hits /
                   (Shared.pageFaultCounter + Shared.Hits))[:5] + "%")
        HR.configure(foreground="Green")
        HR.pack()
        Label(alert, text="\tAverage Number of Cycles Per Page Fault: " + str(
            int(cycles / Shared.pageFaultCounter)) + "\t").pack()
        Label(alert, text="Average Number of Cycles Per Hit: " +
              str(int(cycles / Shared.Hits))).pack()
        Label(alert, text='Processing time: ' +
              str(int(time() - t)) + 's\n').pack()
        root.update()

        print('\n######### Start ' + algotxt + ' #########')
        print("Number of threads: " + str(threadsNumber))
        print("Quantum time: " + str(quantum))
        print("Number of processes: " + str(Shared.numOfProcesses))
        print("Memory size by frame: " + str(Shared.memorySizeByFrame))
        print("Number of cycles: " + str(cycles))
        print("Number of Page faults : " + str(Shared.pageFaultCounter) + " Page Fault Rate : " + str(
            int(100 * Shared.pageFaultCounter / (Shared.pageFaultCounter + Shared.Hits))) + "%")
        print("Number of hits : " + str(Shared.Hits) + " Hit Rate : " + str(
            int(100 * Shared.Hits / (Shared.pageFaultCounter + Shared.Hits))) + "%")
        print("Average Number of Cycles Per Page Fault : " + str(
            int(cycles / Shared.pageFaultCounter)) + " Average Number of Cycles Per Hit : " + str(int(cycles / Shared.Hits)))
        ###########EDITED###########################
        print('Processing time: ' + str(time() - t) + 's')
        winsound.Beep(1000, 1000)
        print("#################")
####################################################################################

    def runSimulation(self):
        info = Toplevel()
        info.geometry("341x256")
        info.resizable(False, False)
        info.title("Pop menu")
        Label(info, text="\n\n\n\tNumber Of Threads 'from 3 to 16':\t\t").pack()
        thN = Entry(info, width="10")
        thN.pack()
        Label(info, text="\n").pack()
        Label(info, text="Quantam Time 'more than 0': ").pack()
        qu = Entry(info, width="10")
        qu.pack()

        def getInfo():
            n = thN.get()
            q = qu.get()
            if n.isnumeric() and q.isnumeric():
                n = int(n)
                q = int(q)
                if n > 2 and n < 17: 
                    if q > 0:
                        info.destroy()
                        self.main_test(int(n), int(q))
        Label(info, text="\n").pack()
        Button(info, text="  Start  ", command=getInfo).pack()
        Label(info, text="\n").pack()
        root.update()


def generation():
    outString = ""
    generated_config = open('generated__config.txt', 'w')
    # theoritacly we can have from 1 to 65536, but to have a reasonably timed system we use only 10 processes
    numberOfProcesses = random.randint(3, 10) 
    # randint(50, 4096) #if we have frames at a maximum of that way any frame can be pointed to with at most 12 bits
    indexForSize = random.randint(0, 9) 
    sizeOfPhysicalMemory = [10, 10, 20, 20,
                            20, 30, 30, 40, 200, 500][indexForSize]
    # random.randint(1, math.floor(sizeOfPhysicalMemory / numberOfProcesses))
    minimumFramesPerProcess = random.randint(1, 5)
    print(f'{numberOfProcesses}\n{sizeOfPhysicalMemory}\n{minimumFramesPerProcess}')
    generated_config.write(
        f'{numberOfProcesses}\n{sizeOfPhysicalMemory}\n{minimumFramesPerProcess}\n')
    for i in range(numberOfProcesses):
        PID = i + 1  # randint(0, 65535) #0- (2^16) -1
        # can be anything but since our run time is so long we can have a bigger range
        StartTime = random.randint(0, numberOfProcesses * 10) * 20
        durationTime = random.randint(1, 10)  # can be from 1 to 10 hours
        ######################################
        # specified by project, 16 bits for page number, meaning any process can have at most 65536
        # 1 to traces number to had more repeated frames than to 65536
        size = random.randint(1, durationTime*5)
        # outString = f"{hex(PID)[2:]} {StartTime} {durationTime} {size} "
        outString = f"{PID} {StartTime} {durationTime} {size} "
        for j in range(durationTime * 5):  # durationTime = 1 means 5 traces
            pageID = random.randint(0, size - 1)
            if pageID < 16:
                pageID = '0' + str(hex(pageID)[2:])
            else:
                pageID = str(hex(pageID)[2:])
            traceID = random.randint(0, 4095)  # 2^12 -1
            if traceID < 256:
                if traceID < 16:
                    traceID = '00' + str(hex(traceID)[2:])
                else:
                    traceID = '0' + str(hex(traceID)[2:])
            else:
                traceID = str(hex(traceID)[2:])

            outString += f'{pageID + traceID} '

        print(outString)
        generated_config.write(f'{outString}\n')
    generated_config.close()
    # tkinter.messagebox.showinfo(title="Done!", message="A random file <generated_config.txt> has been generated!")
    f.FilePath = "generated__config.txt"
    print(f.FilePath)


def openFile():
    f.FilePath = filedialog.askopenfilename(
        initialdir="C:/Users/MainFrame/Desktop/",
        title="Opening A Text File",
        filetypes=(
            ('Text Files', '*.txt'),
            ('All Files', '*.*')
        )
    )
    print(f.FilePath)
    # The following code is added to facilitate the Scrolled widgets you specified.


class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''

    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))
        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        # Copy geometry methods of master  (taken from ScrolledText.py)
        methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
            | tk.Place.__dict__.keys()
        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''

        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)

        return wrapped

    def __str__(self):
        return str(self.master)


def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''

    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
        container.bind(
            '<Leave>', lambda e: _unbound_to_mousewheel(e, container))
        return func(cls, container, **kw)

    return wrapped


class ScrolledTreeView(AutoScroll, ttk.Treeview):
    '''A standard ttk Treeview widget with scrollbars that will
    automatically show/hide as needed.'''

    @_create_container
    def __init__(self, master, **kw):
        ttk.Treeview.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)


def _bound_to_mousewheel(event, widget):
    child = widget.winfo_children()[0]
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-MouseWheel>',
                       lambda e: _on_shiftmouse(e, child))
    else:
        child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
        child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))


def _unbound_to_mousewheel(event, widget):
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        widget.unbind_all('<MouseWheel>')
        widget.unbind_all('<Shift-MouseWheel>')
    else:
        widget.unbind_all('<Button-4>')
        widget.unbind_all('<Button-5>')
        widget.unbind_all('<Shift-Button-4>')
        widget.unbind_all('<Shift-Button-5>')


def _on_mousewheel(event, widget):
    if platform.system() == 'Windows':
        widget.yview_scroll(-1 * int(event.delta / 120), 'units')
    elif platform.system() == 'Darwin':
        widget.yview_scroll(-1 * int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.yview_scroll(-1, 'units')
        elif event.num == 5:
            widget.yview_scroll(1, 'units')


def _on_shiftmouse(event, widget):
    if platform.system() == 'Windows':
        widget.xview_scroll(-1 * int(event.delta / 120), 'units')
    elif platform.system() == 'Darwin':
        widget.xview_scroll(-1 * int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.xview_scroll(-1, 'units')
        elif event.num == 5:
            widget.xview_scroll(1, 'units')


'''Main entry point for the application.'''
global root
root = tk.Tk()
root.protocol('WM_DELETE_WINDOW', root.destroy)
# Creates a toplevel widget.
global _top1, _w1
_top1 = root
_w1 = mainWindow(_top1)
root.mainloop()
