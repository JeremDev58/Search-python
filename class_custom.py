from os import path, walk
from tkinter import filedialog, messagebox, Text, Button, Tk, StringVar, BooleanVar, Toplevel, TclError
from tkinter.ttk import Label, Frame, Labelframe, Entry, Checkbutton
from threading import Thread
from typing import Tuple


class App(Tk):
    def __init__(self, root):
        Tk.__init__(self)
        self.geometry("500x600")
        self.title("Search")
        self.resizable(width=False, height=False)

        # ATTR
        self.STOP = False
        self.FONT = [(None, 18), (None, 16), (None, 12), (None, 12), (None, 9)]
        self.pattern = None
        self.ltitle = Label(self, text="Search", font=self.FONT[0])
        self.ltitle.pack(fill='x', padx=20, pady=5)
        self.lframe = Labelframe(self)
        self.lframe.pack(fill='x', padx=20)
        self.lsearch = Label(self.lframe, text="Fichier et/ou dossier a rechercher:", font=self.FONT[2])
        self.lsearch.pack(fill='x', pady=2, padx=2)
        self.varsearch = StringVar()
        self.esearch = Entry(self.lframe, textvariable=self.varsearch)
        self.esearch.pack(fill='x', pady=2, padx=2)
        self.varoption = BooleanVar(value=True)
        self.boption = Checkbutton(self.lframe, text="Rechercher dossiers", variable=self.varoption, onvalue=True,
                                   offvalue=False)
        self.boption.pack(anchor='w', pady=2, padx=2)
        self.varword = BooleanVar(value=False)
        self.bword = Checkbutton(self.lframe, text="Recherche un pattern dans les fichiers trouvées",
                                 variable=self.varword, onvalue=True, offvalue=False)
        self.bword.pack(anchor='w', pady=2, padx=2)
        self.lbrowser = Label(self.lframe, text="Chemin d'accès:", font=self.FONT[2])
        self.lbrowser.pack(fill='x', pady=2, padx=2)

        self.varbrowser = StringVar(value=root)
        self.ebrowser = Entry(self.lframe, textvariable=self.varbrowser)
        self.ebrowser.pack(fill='x', side='left', expand=1, pady=2, padx=2)
        self.bbrowser = Button(self.lframe, text="Parcourir", command=self.select_dir, font=self.FONT[2])
        self.bbrowser.pack(side='right', pady=2, padx=2)
        self.varexplorer = StringVar()
        self.lexplorer = Label(self, textvariable=self.varexplorer, font=self.FONT[4])
        self.lexplorer.pack(fill='x', padx=20, pady=5)
        self.lresult = Label(self, text="Résultat:", font=self.FONT[1])
        self.lresult.pack(fill='x', padx=20, pady=5)
        self.canvas_frame = Text(self, height=14, exportselection=0)
        self.canvas_frame.pack(fill='both', padx=20, pady=5)
        self.fbtn = Frame(self)
        self.fbtn.pack(fill='x', padx=20, pady=15)
        self.bsearch = Button(self.fbtn, text="Rechercher", command=lambda: self._thread_searching(), font=self.FONT[2])
        self.bsearch.pack(side='right')
        self.bcancel = Button(self.fbtn, text="Annuler", command=lambda: self._thread_cancel(), font=self.FONT[2])
        self.bcancel.pack(side='right')
        self.protocol("WM_DELETE_WINDOW", self.close)

    def searching(self):
        if self.STOP:
            self.STOP = False
        self.canvas_frame.delete(1.0, 'end')
        for child in self.lframe.children.values():
            child["state"] = 'disabled'
        self.bsearch["state"] = 'disabled'
        rootdir = self.varbrowser.get()
        if rootdir is None or rootdir == '' or not path.exists(rootdir):
            messagebox.showerror("Erreur", "Vous devez renseigner un Chemin d'accès valide !")
            for child in self.lframe.children.values():
                child["state"] = 'normal'
            self.bsearch["state"] = 'normal'
            return

        if self.esearch.get() is None or self.esearch.get() == '':
            messagebox.showerror("Erreur", "Vous devez renseigner un nom de fichier ou de dossier a rechercher !")
            for child in self.lframe.children.values():
                child["state"] = 'normal'
            self.bsearch["state"] = 'normal'
            return
        files_and_dir = self._walk(rootdir)
        self.varexplorer.set("Terminé: " + str(files_and_dir[0]) + " fichiers trouvés et " + str(files_and_dir[1]) +
                             " dossiers trouvés.")
        if files_and_dir == (0, 0, list) and not self.STOP:
            self.canvas_frame.delete(0.0, 'end')
            self.canvas_frame.insert('end', "Aucun résultat.")
        elif files_and_dir[0] > 0 and self.varword.get() and not self.STOP:
            self._rchildren()
            self.pattern = TopPattern(self, files_and_dir[2])
            self.wait_window(self.pattern)
        self._rchildren(option='normal')

    def revocation(self):
        self.STOP = True

    def select_dir(self) -> None:
        rootdir = filedialog.askdirectory(title="Sélectionner le dossier", initialdir=self.varbrowser.get())
        if len(rootdir) != 0:
            self.varbrowser.set(rootdir)

    def _walk(self, rootdir) -> Tuple[int, int, list]:
        check = [0, 0, list()]
        for root, dirs, files in walk(rootdir):
            if self.STOP:
                self.canvas_frame.insert('end', "Recherche interrompu.")
                return check[0], check[1], list()
            for file in files:
                self.varexplorer.set(root + '/' + file)
                if self.esearch.get().lower() in file.lower():
                    check[0] += 1
                    check[2].append(root + '/' + file)
                    self.canvas_frame.insert('end', "Fichier trouvée: " + root + '/' + file + '\n\n')
            if self.varoption.get():
                for directory in dirs:
                    self.varexplorer.set(root + '/' + directory)
                    if self.esearch.get().lower() in directory.lower():
                        check[1] += 1
                        self.canvas_frame.insert('end', "Dossier trouvée: " + root + '/' + directory + '\n\n')
        return check[0], check[1], check[2]

    def _thread_searching(self):
        x = Thread(target=self.searching)
        x.start()

    def _thread_cancel(self):
        x = Thread(target=self.revocation)
        x.start()

    def close(self):
        if self.pattern is not None:
            self.pattern.destroy()
        self.destroy()

    def _rchildren(self, widget=None, option='disabled'):
        if widget is not None:
            children = widget.winfo_children()
        else:
            children = self.winfo_children()
        for child in children:
            children.extend(child.winfo_children())
            if option != 'ls':
                try:
                    child["state"] = option
                except TclError:
                    pass
        if option == 'ls':
            return children


class TopPattern(Toplevel):
    def __init__(self, master, lsfiles):
        Toplevel.__init__(self, master=master)

        self.geometry("400x400")
        self.title("Pattern Search")
        self.resizable(width=False, height=False)
        self.ltitle = Label(self, text="Pattern rechercher:", font=(None, self.master.FONT[1][1]))
        self.ltitle.pack(fill='x', padx=20, pady=5)
        self.varpattern = StringVar()
        self.epattern = Entry(self, textvariable=self.varpattern)
        self.epattern.pack(fill='x', padx=20, pady=5)
        self.lexplore = Label(self)
        self.lexplore.pack(fill='x', padx=20, pady=5)
        self.lres = Label(self, text="Résultat:", font=(None, self.master.FONT[1][1]))
        self.lres.pack(fill='x', padx=20, pady=5)
        self.tres = Text(self, height=10, exportselection=0)
        self.tres.pack(fill='both', padx=20, pady=5)
        self.fbutton = Frame(self)
        self.fbutton.pack(fill='x', padx=20, pady=15)
        self.bstart = Button(self.fbutton, text="Commencer", command=lambda: self._thread_pattern(lsfiles),
                             font=self.master.FONT[2])
        self.bstart.pack(side='right')
        self.bclose = Button(self.fbutton, text="Annuler", command=lambda: self.master._thread_cancel(),
                             font=self.master.FONT[2])
        self.bclose.pack(side='right')

        self.protocol("WM_DELETE_WINDOW", self.close)

    def _thread_pattern(self, lsfiles):
        x = Thread(target=self.search_pattern, args=(lsfiles,))
        x.start()
        pass

    def search_pattern(self, lsfiles):
        global found
        self.master.STOP = False
        self.epattern['state'] = 'disabled'
        self.bstart['state'] = 'disabled'
        self.tres.delete(0.0, 'end')
        lines = []
        check = 0
        found = 0
        nbfilesanalyse = 0
        if self.epattern.get() is None or self.epattern.get() == '':
            messagebox.showerror("Erreur", "Vous devez renseigner un pattern a rechercher !")
            self.stop(nbfilesanalyse, lsfiles, check, False)
            return
        for file in lsfiles:
            found = 0
            lines.clear()
            if self.master.STOP:
                self.stop(nbfilesanalyse, lsfiles, check)
                return
            if path.exists(file):
                with open(file, 'r') as f:
                    try:
                        lines.extend(f.readlines())
                    except:
                        nbfilesanalyse -= 1
                    else:
                        nbfilesanalyse += 1
                        for line in lines:
                            self.lexplore["text"] = line
                            if self.epattern.get().lower() in line.lower():
                                print("Match: " + line + "     Fichier : " + file)
                                found += 1
                        if found != 0:
                            check += 1
                            self.tres.insert('end', "Pattern trouvée: " + file + '\n\n')
        if check == 0:
            self.tres.delete(0.0, 'end')
            self.tres.insert('end', "Aucun résultat.")
        self.lexplore["text"] = "Terminé: " + str(nbfilesanalyse) + "/" + str(len(lsfiles)) + " Fichiers analysé et " + \
                                str(check) + " Pattern Trouvé."
        self.bstart['state'] = 'normal'
        self.epattern['state'] = 'normal'

    def close(self):
        self.master._rchildren(option='normal')
        self.destroy()

    def stop(self, nbfilesanalyse, lsfiles, check, explore=True):
        if explore:
            self.tres.insert('end', "Recherche interrompu.")
            self.lexplore["text"] = "Terminé: " + str(nbfilesanalyse) + "/" + str(len(lsfiles)) + \
                                    " Fichiers analysé et " + str(check) + " Pattern Trouvé."
        self.epattern['state'] = 'normal'
        self.bstart['state'] = 'normal'
