# ------------------------------------------------------------
# Pluckeye Lockbox
# Copyright (c) 2026 No_Name
#
# This software is released into the public domain.
# You may use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of this software with no
# restrictions. This software is provided without warranty.
# ------------------------------------------------------------



# Compile this script by getting 'pyinstaller' and then do this:
# pyinstaller --noconsole --onefile lockbox.py
# Modules:


#sudo apt install python3-cryptography
#sudo apt install python3-tk

import os
import shutil
import sqlite3
import time
import base64
import hashlib
import codecs as __________
import builtins as ___________
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hmac
import tkinter as tk
from tkinter import (
    messagebox,
    simpledialog,
    filedialog,
    ttk,
)




DB_FILE = "lockbox_local.db"
LOCK_FILE = "lockbox.lock"


def apply_custom_style(btn):
    """Applies a consistent 'Swing-style' look with a blue outline to a button."""
    LIGHT_BLUE_OUTLINE = "#B0CFDE" 
    btn.config(
        font=("Segoe UI", 10),
        bg="#E0E0E0",
        activebackground="#D5D5D5",
        relief="flat",
        # This creates the 1px border effect
        highlightbackground=LIGHT_BLUE_OUTLINE,
        highlightcolor=LIGHT_BLUE_OUTLINE,
        highlightthickness=1,
        # Adding a tiny bit of borderwidth ensures the highlight is visible
        bd=0, 
        padx=8,
        pady=4,
        cursor="hand2"
    )
    
    
    
class PepperObfuscator:
    # Paste the generated values here:
    XOR_KEY = 167  # example; replace with printed value
    OBF_DATA = [
    
        212,
        35,
        0,
        222,
        63,
        16,
        192,
        8,
        211,
        33,
        26,
        208,
        47,
        13,
        5,
        53,
        11,
        210,
        219,
        193,
        28,
        59,
        220,
        20,
        195,
        15,
        221,
        23,
        54,
        5,
        223,
        210,
        212,
        210,
        5,
        13,
        18,
        15,
        20,
        18,
        14,
        5,
        209,
        32,
        28,
        20,
        2,
        27,
        5,
        221,
        55,
        18,
        26,
        30,
        13,
        5,
        219,
        41,
        28,
        27,
        1
        
    ]

    @classmethod
    def get_pepper(cls) -> bytes:


        __ = lambda x: ''.join(chr(i) for i in x)


        ___b = __import__(__([98,117,105,108,116,105,110,115]))


        ___ = __([114,111,116,95,49,51])     
        ____ = __([117,116,102,45,56])      


        _____ = cls.__dict__


        ______ = next(
            v for v in _____ .values()
            if isinstance(v, (list, tuple))
            and v and all(isinstance(i, int) for i in v)
        )


        _______ = next(
            v for v in _____ .values()
            if isinstance(v, int) and v > 0x20
        )


        ________ = ___b.__dict__[__([109,97,112])]  
        _________ = ___b.__dict__[__([99,104,114])]  
        __________ = ___b.__dict__[__([108,105,115,116])]  
        ___________r = ___b.__dict__[__([114,101,118,101,114,115,101,100])]  

        __join = str.__dict__[__([106,111,105,110])]


        __xor_safe = lambda a, b: ((a | b) - (a & b)) & 0xFF


        def __id(x):
            return (lambda z: z)(x)


        def __pipe(data):
            return __id(
                ___________r(
                    __________(
                        ________(
                            lambda t: __xor_safe(t, _______),
                            data
                        )
                    )
                )
            )


        def __pipe2(data):
            return ________(lambda x: x, __pipe(data))

        def __shift(x):
            return ________(lambda n: max(0, n - 67), x)


        def __strify(x):
            return __join('', ________(_________, x))

        def __decode(x):
            return (__import__(__([99,111,100,101,99,115]))
                    .__dict__[__([100,101,99,111,100,101])])(x, ___)


        return (
            lambda f:
                lambda g:
                    lambda h:
                        (lambda z: z)(
                            h(
                                g(
                                    f(______)
                                )
                            )
                        )
        )(
            lambda d: __strify(__shift(__pipe2(d)))
        )(
            lambda e: __decode(e)
        )(
            lambda w: w.encode(____)
        )
    
# ---------------------- Cryptographic related helpers ----------------------
class CryptoManager:
    """
    Handles:
      - generating a random data key
      - encrypting/decrypting contents with that key
      - 'protecting' (obfuscating) the key so it's not stored in plain form
    """


    def __init__(self):
        self._PEPPER = PepperObfuscator.get_pepper()

    # ---------- low-level helpers ----------

    def _derive_wrap_key(self, context: str) -> bytes:
        """
        Derive a wrapping key from a context string (e.g. name+unlock_delay)
        plus a secret pepper. This is used to encrypt the data key.
        """
        ctx_bytes = context.encode("utf-8")
        salt = hashlib.sha256(self._PEPPER + ctx_bytes).digest()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=300_000,
        )
        key = kdf.derive(ctx_bytes)
        return base64.urlsafe_b64encode(key)  # Fernet key format

    # ---------- public API ----------

    def generate_data_key(self) -> bytes:
        """Random key used to encrypt the lockbox contents."""
        return Fernet.generate_key()  # already base64-encoded 32 bytes

    def encrypt_contents(self, data_key: bytes, plaintext: str) -> str:
        f = Fernet(data_key)
        token = f.encrypt(plaintext.encode("utf-8"))
        return token.decode("ascii")

    def decrypt_contents(self, data_key: bytes, token_str: str) -> str:
        f = Fernet(data_key)
        return f.decrypt(token_str.encode("ascii")).decode("utf-8")

    def protect_key(self, data_key: bytes, name: str, unlock_delay_ms: int) -> str:
        """
        Obfuscate the data key using:
          - box name
          - unlock delay
          - internal pepper
        Returns a base64 string to store in DB.
        """
        context = f"{name}:{unlock_delay_ms}"
        wrap_key = self._derive_wrap_key(context)
        f = Fernet(wrap_key)
        wrapped = f.encrypt(data_key)
        return wrapped.decode("ascii")

    def unprotect_key(self, protected_str: str, name: str, unlock_delay_ms: int) -> bytes:
        """
        Reverse of protect_key. Reconstructs the data key from the stored blob.
        """
        context = f"{name}:{unlock_delay_ms}"
        wrap_key = self._derive_wrap_key(context)
        f = Fernet(wrap_key)
        data_key = f.decrypt(protected_str.encode("ascii"))
        return data_key    
        
    def compute_integrity(self, box) -> str:
        msg = (
            str(box.name) +
            str(box.contents) +
            str(box.unlock_delay) +
            str(box.relock_delay) +
            str(box.unlock_timestamp) +
            str(box.relock_timestamp) +
            str(box.key_obf)
        ).encode("utf-8")

        return hmac.new(self._PEPPER, msg, hashlib.sha256).hexdigest()


# ---------------------- Entity ----------------------
class Lockbox:
    def __init__(
        self,
        name,
        contents,
        unlock_delay,
        relock_delay,
        locked=1,
        unlock_timestamp=None,
        relock_timestamp=0,
        key_obf=None,
        integrity=None,
    ):
        self.name = name
        self.contents = contents
        self.unlock_delay = unlock_delay
        self.relock_delay = relock_delay
        self.locked = locked
        self.unlock_timestamp = unlock_timestamp
        self.relock_timestamp = relock_timestamp
        self.key_obf = key_obf
        self.integrity = integrity




# ---------------------- Model ----------------------
class Model:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.crypto = CryptoManager()  # <--- add this
        self._init_schema()

        
    

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS boxes (
                name TEXT PRIMARY KEY,
                contents TEXT NOT NULL,
                unlock_delay INTEGER NOT NULL,
                relock_delay INTEGER NOT NULL,
                locked INTEGER NOT NULL,
                unlock_timestamp INTEGER,
                relock_timestamp INTEGER NOT NULL,
                key_obf TEXT,
                integrity TEXT
            )
            """
        )
        self.conn.commit()


    def close(self):
        self.conn.close()


    def getBoxes(self):
        cur = self.conn.execute("SELECT name FROM boxes ORDER BY name")
        return [row["name"] for row in cur.fetchall()]

    def boxExists(self, name):
        cur = self.conn.execute("SELECT 1 FROM boxes WHERE name = ?", (name,))
        return cur.fetchone() is not None

    def createBox(self, name, contents, unlock_delay_ms, relock_delay_ms):
        data_key = self.crypto.generate_data_key()
        encrypted_contents = self.crypto.encrypt_contents(data_key, contents)
        key_obf = self.crypto.protect_key(data_key, name, unlock_delay_ms)

        box = Lockbox(
            name=name,
            contents=encrypted_contents,
            unlock_delay=unlock_delay_ms,
            relock_delay=relock_delay_ms,
            locked=1,
            unlock_timestamp=None,
            relock_timestamp=0,
            key_obf=key_obf,
            integrity=None,
        )

        box.integrity = self.crypto.compute_integrity(box)

        self.conn.execute(
            """
            INSERT INTO boxes
            (name, contents, unlock_delay, relock_delay,
             locked, unlock_timestamp, relock_timestamp, key_obf, integrity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                box.name,
                box.contents,
                box.unlock_delay,
                box.relock_delay,
                box.locked,
                box.unlock_timestamp,
                box.relock_timestamp,
                box.key_obf,
                box.integrity,
            ),
        )
        self.conn.commit()



    def deleteBox(self, name):
        self.conn.execute("DELETE FROM boxes WHERE name = ?", (name,))
        self.conn.commit()

    def getBox(self, name):
        cur = self.conn.execute(
            """
            SELECT name, contents, unlock_delay, relock_delay,
                   locked, unlock_timestamp, relock_timestamp,
                   key_obf, integrity
            FROM boxes
            WHERE name = ?
            """,
            (name,),
        )

        row = cur.fetchone()
        if not row:
            return None

        # Build the Lockbox object
        box = Lockbox(
            name=row["name"],
            contents=row["contents"],
            unlock_delay=row["unlock_delay"],
            relock_delay=row["relock_delay"],
            locked=row["locked"],
            unlock_timestamp=row["unlock_timestamp"],
            relock_timestamp=row["relock_timestamp"],
            key_obf=row["key_obf"],
            integrity=row["integrity"],
        )

        # 🔥 TAMPER CHECK GOES HERE
        expected = self.crypto.compute_integrity(box)

        if box.integrity != expected:
            return "TAMPERED"


        return box



    def updateBox(self, box: Lockbox):

        # 1. Recompute integrity BEFORE saving
        box.integrity = self.crypto.compute_integrity(box)

        # 2. Update the row including integrity
        self.conn.execute(
            """
            UPDATE boxes
            SET contents = ?, unlock_delay = ?, relock_delay = ?,
                locked = ?, unlock_timestamp = ?, relock_timestamp = ?,
                key_obf = ?, integrity = ?
            WHERE name = ?
            """,
            (
                box.contents,
                box.unlock_delay,
                box.relock_delay,
                box.locked,
                box.unlock_timestamp,
                box.relock_timestamp,
                box.key_obf,
                box.integrity,   # ← correct
                box.name,
            ),
        )

        self.conn.commit()


    def exportDB(self, output_path):
        try:
            self.conn.commit()
            self.conn.execute("PRAGMA wal_checkpoint(FULL);")
            shutil.copyfile(self.db_path, output_path)
            return True
        except Exception as e:
            print("Export error:", e)
            return False

    def importBoxes(self, input_file):
        try:
            other_conn = sqlite3.connect(input_file)
            other_conn.row_factory = sqlite3.Row

            cur = other_conn.execute(
                """
                SELECT name, contents, unlock_delay, relock_delay,
                       locked, unlock_timestamp, relock_timestamp,
                       key_obf, integrity
                FROM boxes
                """
            )
            rows = cur.fetchall()
            total = len(rows)
            imported = 0

            for row in rows:
                name = row["name"]
                if self.boxExists(name):
                    continue

                self.conn.execute(
                    """
                    INSERT INTO boxes
                    (name, contents, unlock_delay, relock_delay,
                     locked, unlock_timestamp, relock_timestamp,
                     key_obf, integrity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["name"],
                        row["contents"],
                        row["unlock_delay"],
                        row["relock_delay"],
                        row["locked"],
                        row["unlock_timestamp"],
                        row["relock_timestamp"],
                        row["key_obf"],
                        row["integrity"],
                    ),
                )
                imported += 1

            self.conn.commit()
            other_conn.close()
            return (total, imported)

        except Exception as e:
            print("Import error:", e)
            return (-1, -1)



# ---------------------- Views ----------------------

class HomeView(tk.Frame):

    def __init__(self, master, model: Model):
        super().__init__(master)
        self.model = model
        self.master = master
        self.pack(fill="both", expand=True, padx=25, pady=15) # Added outer padding




        # 3. Buttons row - Added pady=(20, 20) to move it lower from the top
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=(5, 20)) 

        self.create_btn = tk.Button(btn_frame, text="New", command=self.on_create)
        self.delete_btn = tk.Button(btn_frame, text="Delete", command=self.on_delete)
        self.open_btn = tk.Button(btn_frame, text="Open", command=self.on_open)
        self.export_btn = tk.Button(btn_frame, text="Export", command=self.on_export)
        self.import_btn = tk.Button(btn_frame, text="Import", command=self.on_import)

        for btn in [self.create_btn, self.delete_btn, self.open_btn, self.export_btn, self.import_btn]:
            apply_custom_style(btn)
            btn.pack(side="left", padx=3)

        # 5. Spacing for Labels
        self.list_label = tk.Label(self, text="Lockboxes:", pady=5)
        self.list_label.pack(anchor="w", padx=2) # padx adds space from the left edge

        # 1. Error Label - Positioned between Heading and Listbox
        self.error_label = tk.Label(self, text="", fg="#CC0000", font=("Segoe UI", 9, "bold"))
        # We don't pack it yet, show_error will handle it

        self.box_list = tk.Listbox(self, borderwidth=0, height=6, activestyle="none")
        self.box_list.pack(fill="x", expand=False, pady=(5, 0), padx=2)
        
        # ADD THIS LINE:
        self.box_list.bind("<<ListboxSelect>>", self.on_listbox_select)

        self.refresh_boxes()


    def on_listbox_select(self, event):
        sel = self.box_list.curselection()
        if sel:
            index = sel[0]
            content = self.box_list.get(index).strip()
            if not content:  # If it's an empty "ghost" row
                self.box_list.selection_clear(index)

    def refresh_boxes(self):
            self.box_list.delete(0, tk.END)
            boxes = self.model.getBoxes()
            
            # We want to show 6 rows total (matching your Listbox height)
            for i in range(6):
                if i < len(boxes):
                    # Real data
                    name = boxes[i]
                    self.box_list.insert(tk.END, f"  {name}")
                else:
                    # Ghost data to keep the stripe pattern
                    self.box_list.insert(tk.END, "")
                
                # Apply stripes to every row created
                if i % 2 == 0:
                    self.box_list.itemconfigure(i, bg="white")
                else:
                    self.box_list.itemconfigure(i, bg="#F0F0F0")

    def _selected_name(self):
        sel = self.box_list.curselection()
        if not sel:
            return None
        # Get the text, strip the leading spaces you added in refresh_boxes
        name = self.box_list.get(sel[0]).strip()
        
        # Crucial: if the stripped name is empty, it's a ghost row. Return None.
        if not name:
            return None
        return name

    def show_error(self, msg):
            self.error_label.config(text=msg)
            # Packing BEFORE the listbox makes the listbox shift down
            self.error_label.pack(anchor="w", padx=2, before=self.box_list, pady=(0, 5))

    def hide_error(self):
        self.error_label.pack_forget()

    def on_create(self):
        win = tk.Toplevel(self.master)
        win.title("Create a New Lockbox")
        win.configure(bg="#F4F4F4")
        win.option_add("*Background", "#F4F4F4")
        win.option_add("*Frame.Background", "#F4F4F4")
        win.option_add("*Label.Background", "#F4F4F4")
        win.geometry("350x380")
        win.resizable(False, False)
        win.grab_set()
        CreateBoxView(win, self.model, on_close=self.refresh_boxes)

    def on_delete(self):
        name = self._selected_name()
        if not name:
            self.show_error("No lockbox is selected.")
            return
        self.hide_error()
        if messagebox.askokcancel(
            "Confirm Deletion",
            "Are you sure you want to delete this lockbox? You won't be able to recover it after deleting it.",
            parent=self.master,
        ):
            self.model.deleteBox(name)
            self.refresh_boxes()

    def on_open(self):
        name = self._selected_name()
        if not name:
            self.show_error("No lockbox is selected.")
            return
        self.hide_error()
        win = tk.Toplevel(self.master)
        win.title("Pluckeye Lockbox")
        win.configure(bg="#F4F4F4")
        win.option_add("*Background", "#F4F4F4")
        win.option_add("*Frame.Background", "#F4F4F4")
        win.option_add("*Label.Background", "#F4F4F4")
        win.geometry("320x320")
        win.resizable(False, False)
        win.grab_set()
        DisplayBoxView(win, self.model, name, on_close=self.refresh_boxes)


    def on_export(self):
        name = self._selected_name()
        if not name:
            self.show_error("No lockbox is selected.")
            return
        self.hide_error()

        win = tk.Toplevel(self.master)
        win.title("Export Boxes")
        win.geometry("250x150")
        win.resizable(False, False)
        win.configure(bg="#F4F4F4")
        win.option_add("*Background", "#F4F4F4")
        win.option_add("*Frame.Background", "#F4F4F4")
        win.option_add("*Label.Background", "#F4F4F4")
        win.grab_set()
        ExportView(win, self.model)

    def on_import(self):
        file_path = filedialog.askopenfilename(
            title="Select a file to import.",
            filetypes=[("Lockbox Files (.lbf)", "*.lbf"), ("All files", "*.*")],
            parent=self.master,
        )
        if not file_path:
            return

        if not messagebox.askokcancel(
            "Import Alert",
            "No two lockboxes can have the same name. Any lockbox with a name identical to one you've already made will not be imported. Press \"OK\" to continue.",
            parent=self.master,
        ):
            return

        total, imported = self.model.importBoxes(file_path)
        if total != -1:
            messagebox.showinfo(
                "Import Complete",
                f"{total} boxes found in import file. {imported} were successfully imported.",
                parent=self.master,
            )
            self.refresh_boxes()
        else:
            messagebox.showerror(
                "Error",
                "Something went wrong while importing.",
                parent=self.master,
            )
            self.refresh_boxes()


class ExportView(tk.Frame):
    def __init__(self, master, model: Model):
        super().__init__(master)
        self.master = master
        self.model = model
        self.pack(fill="both", expand=True, padx=10, pady=10)

        self.field_label = tk.Label(self, text="Name of export file:")
        self.field_label.pack(anchor="w")

        self.filename_label = tk.Label(self, text="", font=("TkDefaultFont", 9))
        self.filename_label.pack(anchor="w")
        self.filename_label.pack_forget()

        self.filename_var = tk.StringVar()

        self.filename_entry = tk.Entry(self, textvariable=self.filename_var, width=40, bg="white")
        self.filename_entry.pack(anchor="w")
        

        self.filename_entry.bind("<KeyRelease>", self.on_filename_change)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        self.export_btn = tk.Button(btn_frame, text="Export", command=self.on_export)
        
        apply_custom_style(self.export_btn) # Reuse the same global function
        self.export_btn.pack()
    def on_filename_change(self, event=None):
        name = self.filename_var.get().strip()
        if name:
            self.filename_label.config(text=f"{name}.lbf")
            self.filename_label.pack(anchor="w")
        else:
            self.filename_label.pack_forget()

    def on_export(self):
        name = self.filename_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a filename.", parent=self.master)
            return

        directory = filedialog.askdirectory(
            title="Select export location",
            parent=self.master,
        )
        if not directory:
            return

        output_path = os.path.join(directory, f"{name}.lbf")
        if os.path.exists(output_path):
            messagebox.showerror(
                "File already exists",
                "A file with that name already exists in this directory.",
                parent=self.master,
            )
            return

        ok = self.model.exportDB(output_path)
        if not ok:
            messagebox.showerror(
                "Error",
                "Something went wrong while exporting.",
                parent=self.master,
            )
        else:
            messagebox.showinfo(
                "Export Boxes",
                "Export was successful.",
                parent=self.master,
            )
            self.master.destroy()


class CreateBoxView(tk.Frame):
    def __init__(self, master, model: Model, on_close=None):
        super().__init__(master)
        self.master = master
        self.model = model
        self.on_close = on_close

        self.pack(fill="both", expand=True, padx=10, pady=10)

        self.name_label = tk.Label(self, text="Name:")
        self.name_label.pack(anchor="w")

        self.name_error = tk.Label(self, text="", fg="red", font=("TkDefaultFont", 8))
        self.name_error.pack(anchor="w")
        self.name_error.pack_forget()

        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(self, textvariable=self.name_var, width=40, bg="white")
        self.name_entry.pack(anchor="w")

        self.contents_label = tk.Label(self, text="Contents:")
        self.contents_label.pack(anchor="w")

        self.contents_text = tk.Text(self, height=3.7, width=40, bg="white")
        self.contents_text.pack(anchor="w")

# Unlock delay
        self.unlock_frame = tk.Frame(self)
        self.unlock_frame.pack(anchor="w", pady=(15, 5)) 
        
        tk.Label(self.unlock_frame, text="Unlock delay:").pack(side="left")
        
        self.unlock_num_var = tk.StringVar()
        self.unlock_num_entry = tk.Entry(self.unlock_frame, textvariable=self.unlock_num_var, width=6, bg="white")
        self.unlock_num_entry.pack(side="left", padx=5)

        # Added a space before each unit name in the list
        self.unlock_unit_var = tk.StringVar(value=" seconds") 
        self.unlock_unit_combo = ttk.Combobox(
            self.unlock_frame,
            textvariable=self.unlock_unit_var,
            values=[" seconds", " minutes", " hours", " days"], # Added leading spaces here
            state="readonly",
            width=10,
        )
        self.unlock_unit_combo.pack(side="left")

        # Repeat for Relock delay
        self.relock_frame = tk.Frame(self)
        self.relock_frame.pack(anchor="w", pady=(5, 15))
        
        tk.Label(self.relock_frame, text="Relock delay:").pack(side="left")
        
        self.relock_num_var = tk.StringVar()
        self.relock_num_entry = tk.Entry(self.relock_frame, textvariable=self.relock_num_var, width=6, bg="white")
        self.relock_num_entry.pack(side="left", padx=5)

        self.relock_unit_var = tk.StringVar(value=" seconds")
        self.relock_unit_combo = ttk.Combobox(
            self.relock_frame,
            textvariable=self.relock_unit_var,
            values=[" seconds", " minutes", " hours", " days"], # Added leading spaces here
            state="readonly",
            width=10,
        )
        self.relock_unit_combo.pack(side="left")

        self.relock_error = tk.Label(self, text="", fg="red", font=("TkDefaultFont", 8))
        self.relock_error.pack(anchor="w")
        self.relock_error.pack_forget()


        # Confirm button
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        self.confirm_btn = tk.Button(btn_frame, text="Confirm", command=self.on_confirm)
        apply_custom_style(self.confirm_btn) # Reuse the same global function
        self.confirm_btn.pack()

        # underscore validation
        self.name_entry.bind("<KeyRelease>", self.validate_name)
        #self.contents_text.bind("<KeyRelease>", self.validate_underscore)

        self.master.protocol("WM_DELETE_WINDOW", self._on_close)
        

    def _on_close(self):
        if self.on_close:
            self.on_close()
        self.master.destroy()

    def validate_name(self, event=None):
        name = self.name_var.get()

        if "_" in name:
            self.name_error.config(text="Names cannot contain underscores.")
            self.name_error.pack(anchor="w")



    def to_ms(self, units, unit_type):
        base = 1000
        # Matches the exact strings in your Combobox values list
        if unit_type == " seconds":
            return units * base
        if unit_type == " minutes":
            return units * base * 60
        if unit_type == " hours":
            return units * base * 60 * 60
        if unit_type == " days":
            return units * base * 60 * 60 * 24
        return units * base


    def on_confirm(self):
        name = self.name_var.get().strip()
        contents = self.contents_text.get("1.0", "end-1c").strip()

        if "_" in name:
            self.relock_error.config(text="Names cannot contain underscores.")
            self.relock_error.pack(anchor="w")
            return

        # 1. Block empty names
        if not name:
            self.relock_error.config(text="Lockbox name cannot be empty.")
            self.relock_error.pack(anchor="w")
            return
            
        # 2. NEW: Block empty contents
        if not contents:
            self.relock_error.config(text="Contents cannot be empty.")
            self.relock_error.pack(anchor="w")
            return

        # 2. Block if limit of 5 is reached
        if len(self.model.getBoxes()) >= 5:
            self.relock_error.config(text="Limit reached: You can only have 5 lockboxes.")
            self.relock_error.pack(anchor="w")
            return

        unlock_units_str = self.unlock_num_var.get().strip()
        relock_units_str = self.relock_num_var.get().strip()
        


        try:
            unlock_units = int(unlock_units_str)
            relock_units = int(relock_units_str)
            
            # --- NEW: Minimum Value Check ---
            if unlock_units < 1 or relock_units < 1:
                self.relock_error.config(
                    text="Delay values must be at least 1."
                )
                self.relock_error.pack(anchor="w")
                return
            # --------------------------------
            
        except Exception:
            self.relock_error.config(
                text="Please input valid numbers for the unlock and relock delays."
            )
            self.relock_error.pack(anchor="w")
            return

        MAX_UNLOCK_MS = 28 * 24 * 60 * 60 * 1000
        # Use .get() normally, the strip() inside to_ms handles the rest
        unlock_delay_ms = self.to_ms(unlock_units, self.unlock_unit_var.get())
        relock_delay_ms = self.to_ms(relock_units, self.relock_unit_var.get())

        if unlock_delay_ms > MAX_UNLOCK_MS:
            self.relock_error.config(
                text="Unlock delay cannot be greater than 28 days."
            )
            self.relock_error.pack(anchor="w")
            return
            
            
        if self.relock_unit_var.get() == " days" and relock_units > 7:
            self.relock_error.config(
                text="A lockbox can't have a relock delay greater than 7 days."
            )
            self.relock_error.pack(anchor="w")
            return





        if self.model.boxExists(name):
            self.relock_error.config(text="A box with this name already exists.")
            self.relock_error.pack(anchor="w")
            return

        self.model.createBox(name, contents, unlock_delay_ms, relock_delay_ms)
        self._on_close()


class DisplayBoxView(tk.Frame):
    def __init__(self, master, model: Model, box_name: str, on_close=None):
        self.on_close = on_close

        super().__init__(master)
        self.master = master
        self.model = model
        self.box_name = box_name

        self.pack(fill="both", expand=True, padx=10, pady=10)

        self.currentBox = self.model.getBox(self.box_name)
        
        if self.currentBox == "TAMPERED":
            self.show_tamper_screen()
            return
        
        if not self.currentBox:
            messagebox.showerror("Error", "This lockbox no longer exists.", parent=self.master)
            self.master.destroy()
            return


        self.lastStatus = None
        self.currentlyUnlocking = self.currentBox.unlock_timestamp is not None

        self.title_label = tk.Label(self, text=self.box_name, font=("Courier", 14))
        self.title_label.pack(anchor="w")

        self.lock_status = tk.Label(self, text="Locked")
        self.lock_status.pack(anchor="w", pady=(0, 10)) # Reduced pady slightly

        # 1. Define the Time Label here (but don't pack it yet)
        self.time_label = tk.Label(self, text="", fg="black", font=("Tahoma", 10))

        # 2. Define and pack the Button Frame
        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(anchor="w", pady=(0, 20))
        
        self.unlock_btn = tk.Button(self.btn_frame, text="Unlock", command=self.on_unlock)
        self.relock_btn = tk.Button(self.btn_frame, text="Relock", command=self.on_relock)
        self.unlock_btn.pack(side="left", padx=(0, 8))
        self.relock_btn.pack(side="left", padx=8)
        
        apply_custom_style(self.unlock_btn)
        apply_custom_style(self.relock_btn)

        self.contents_label = tk.Label(self, text="Contents:", font=("Tahoma", 10))
        self.contents_label.pack(anchor="w")

        self.contents_text = tk.Text(self, height=10, width=40, bg='white')
        self.contents_text.pack(fill="both", expand=True)
        self.lastStatus = None
        self.updateUI()
        self._tick()
        
    def show_tamper_screen(self):
        # Clear the window
        for widget in self.winfo_children():
            widget.destroy()

        # Big red warning
        warning = tk.Label(
            self,
            text="⚠️  This lockbox has been tampered.\nIt cannot be opened.",
            fg="red",
            font=("Segoe UI", 12, "bold"),
            justify="center"
        )
        warning.pack(pady=20)

        # Optional: Delete button
        delete_btn = tk.Button(
            self,
            text="Delete Lockbox",
            command=self.on_delete_tampered
        )
        apply_custom_style(delete_btn)
        delete_btn.pack(pady=10)

        # Optional: Close button
        close_btn = tk.Button(
            self,
            text="Close",
            command=self.master.destroy
        )
        apply_custom_style(close_btn)
        close_btn.pack(pady=5)

    def on_delete_tampered(self):
        self.model.deleteBox(self.box_name)
        messagebox.showinfo("Deleted", "The tampered lockbox has been removed.")

        if self.on_close:
            self.on_close()  # refresh HomeView list

        self.master.destroy()


    def lockBox(self):
        self.currentBox.locked = 1
        self.currentBox.unlock_timestamp = None
        self.currentBox.relock_timestamp = 0

    def getTimeString(self, duration_ms):
            sec_len = 1000
            min_len = sec_len * 60
            hour_len = min_len * 60
            day_len = hour_len * 24

            remaining = duration_ms
            
            # Calculate units
            d = remaining // day_len
            remaining %= day_len
            
            h = remaining // hour_len
            remaining %= hour_len
            
            m = remaining // min_len
            remaining %= min_len
            
            s = max(0, (remaining - 1) // sec_len)


            # Build the string parts
            parts = []
            if d > 0: parts.append(f"{d}d")
            if h > 0: parts.append(f"{h}h")
            if m > 0: parts.append(f"{m}m")
            if s > 0 or not parts: # Show seconds if it's the only thing left
                parts.append(f"{s}s")

            # Join with a space for a tight look: "1d 4h 20m"
            return " ".join(parts)

    def updateUI(self):
            # Fix 1: Check if the window still exists before doing anything
            if not self.winfo_exists():
                return
        
            box = self.model.getBox(self.box_name)
            
            # Fix 2: If the box is gone, close the window silently
            if not box:
                self.master.destroy()
                return
            
            self.currentBox = box
            now_ms = int(time.time() * 1000)
            
            show_timer = False
            timer_text = ""

            # Determine if any timer (unlocking OR relocking) is currently active
            timer_active = self.currentBox.unlock_timestamp is not None

            if timer_active:
                if now_ms < self.currentBox.unlock_timestamp:
                    # Phase 1: Waiting to open
                    diff = self.currentBox.unlock_timestamp - now_ms
                    timer_text = f"{self.getTimeString(diff)} to unlock."
                    show_timer = True
                elif now_ms < self.currentBox.relock_timestamp:
                    # Phase 2: Open, waiting to relock
                    if self.currentBox.locked == 1:
                        self.currentBox.locked = 0
                        self.model.updateBox(self.currentBox)
                    diff = self.currentBox.relock_timestamp - now_ms
                    timer_text = f"{self.getTimeString(diff)} to relock."
                    show_timer = True
                else:
                    # Phase 3: Timer expired, perform relock
                    self.lockBox()
                    self.model.updateBox(self.currentBox)
                    self.currentlyUnlocking = False
                    timer_active = False # Reset flag as the cycle is done

            # --- Dynamic Layout Logic ---
            # Only pack the label if it isn't already visible to prevent UI flickering
            if show_timer:
                self.time_label.config(text=timer_text)
                if not self.time_label.winfo_manager(): 
                    self.time_label.pack(anchor="w", before=self.btn_frame, pady=(0, 10))
            else:
                self.time_label.pack_forget()

            # --- Box Content & Button Logic ---
            status_changed = self.lastStatus is None or self.lastStatus != self.currentBox.locked

            if self.currentBox.locked == 1:
                # Update visual text only if status just flipped to Locked
                if status_changed:
                    self.lock_status.config(text="Locked", fg="red")
                    self.contents_text.config(state="normal")
                    self.contents_text.delete("1.0", tk.END)
                    self.contents_text.insert("1.0", "-- locked --")
                    self.contents_text.config(state="disabled")
                
                # Button Logic for Locked State:
                # Disable Unlock button if a timer is running (the "unlocking" phase)
                if timer_active:
                    self.unlock_btn.config(state="disabled")
                else:
                    self.unlock_btn.config(state="normal")
                
                self.relock_btn.config(state="disabled")

            elif self.currentBox.locked == 0:
                # Update visual text only if status just flipped to Unlocked
                if status_changed:
                    self.lock_status.config(text="Unlocked", fg="green")

                    try:
                        # Reconstruct the data key and decrypt
                        data_key = self.model.crypto.unprotect_key(
                            self.currentBox.key_obf,
                            self.currentBox.name,
                            self.currentBox.unlock_delay,
                        )
                        decrypted = self.model.crypto.decrypt_contents(
                            data_key,
                            self.currentBox.contents,
                        )
                        self.contents_text.config(state="normal")
                        self.contents_text.delete("1.0", tk.END)
                        self.contents_text.insert("1.0", decrypted)
                    except Exception:
                        messagebox.showerror("Error", "Could not decrypt contents.", parent=self.master)
                        self.on_relock()
                        return

                # Button Logic for Unlocked State:
                # Unlock is always disabled while open; Relock is enabled
                self.unlock_btn.config(state="disabled")
                self.relock_btn.config(state="normal")

            self.lastStatus = self.currentBox.locked




    def on_unlock(self):
        if self.currentBox.unlock_timestamp is None:
            now_ms = int(time.time() * 1000)
            self.currentBox.unlock_timestamp = now_ms + self.currentBox.unlock_delay

            self.currentBox.relock_timestamp = (
                self.currentBox.unlock_timestamp + self.currentBox.relock_delay
            )

            self.model.updateBox(self.currentBox)
            self.currentlyUnlocking = True

            # FIRST tick happens immediately (no delay)
            # First tick after 1 second
            self._tick()





    def on_relock(self):
        self.lockBox()
        self.model.updateBox(self.currentBox)
        self.currentlyUnlocking = False
        self.updateUI()

    def _tick(self):
        if not self.winfo_exists():
            return
        
        self.updateUI()
        
        # Change the condition to keep ticking as long as ANY timestamp is active
        if self.currentBox and (self.currentBox.unlock_timestamp is not None):
            self._after_id = self.after(1000, self._tick)
        else:
            # If the box just finished relocking, refresh the UI one last time
            self.updateUI()


# ---------------------- Main ----------------------
def main():
    # 1. ATTEMPT TO CLAIM THE LOCK
    # We try to open the file for writing.
    # If instance #1 is already running, instance #2 will fail to delete or overwrite it.
    lock_file_handle = None
    
    if os.path.exists(LOCK_FILE):
        try:
            # Try to remove it. If the other app is running, this triggers an OSError.
            os.remove(LOCK_FILE)
        except OSError:
            # THIS IS THE BLOCK: Another instance is currently holding this file open.
            root = tk.Tk()
            root.withdraw() 
            messagebox.showerror("App Already Running", 
                                 "Another instance of Pluckeye Lockbox is already open.")
            root.destroy()
            return

    try:
        # Create the file and KEEP IT OPEN. 
        # By not using 'with', the file stays 'in use' by this script.
        lock_file_handle = open(LOCK_FILE, "w")
        lock_file_handle.write(str(os.getpid()))
        lock_file_handle.flush() # Ensure it's written to disk
    except Exception as e:
        print(f"Could not create lock: {e}")

    # 2. START THE UI
    root = tk.Tk()
    root.title("Pluckeye Lockbox")

    # Styling and configuration
    default_font = ("Segoe UI", 11)
    LIGHT_BLUE_OUTLINE = "#B0CFDE"
    
    root.configure(bg="#F4F4F4")
    root.option_add("*Background", "#F4F4F4")
    root.option_add("*Frame.Background", "#F4F4F4")
    root.option_add("*Label.Background", "#F4F4F4")
    root.option_add("*Entry.Background", "white")
    root.option_add("*Text.Background", "white")
    root.option_add("*Listbox.Background", "white")
    root.option_add("*Entry.HighlightColor", LIGHT_BLUE_OUTLINE)
    root.option_add("*Entry.HighlightBackground", LIGHT_BLUE_OUTLINE)
    root.option_add("*Entry.HighlightThickness", 1)
    root.option_add("*Text.HighlightBackground", LIGHT_BLUE_OUTLINE)
    root.option_add("*Text.HighlightColor", LIGHT_BLUE_OUTLINE)
    root.option_add("*Text.HighlightThickness", 1)
    root.option_add("*Listbox.HighlightBackground", LIGHT_BLUE_OUTLINE)
    root.option_add("*Listbox.HighlightColor", LIGHT_BLUE_OUTLINE)
    root.option_add("*Listbox.HighlightThickness", 1)
    root.option_add("*Font", default_font)
    root.option_add("*Button.Font", ("Segoe UI", 10))
    root.option_add("*Button.Background", "#E0E0E0")
    root.option_add("*Entry.BorderWidth", 1) 
    root.option_add("*Listbox.BorderWidth", 1)
    root.option_add("*Listbox.selectBackground", "#ADD8E6")
    root.option_add("*Listbox.selectForeground", "black")
    root.option_add("*Entry.Relief", "flat")
    root.option_add("*Text.Relief", "flat")
    root.option_add("*Listbox.Relief", "flat")

    model = Model()
    HomeView(root, model)

    def on_close():
        model.close()
        # Close the file handle so the OS releases the lock
        if lock_file_handle:
            lock_file_handle.close()
        
        # Now we can safely remove the file
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
            except:
                pass
        root.destroy()

    root.geometry("370x300")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_close)

    try:
        root.mainloop()
    finally:
        # Emergency cleanup if the app crashes
        if lock_file_handle:
            try:
                lock_file_handle.close()
            except:
                pass
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
            except:
                pass


if __name__ == "__main__":
    main()
