import tkinter as tk
from tkinter.font import Font
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from lxml import etree

class Switch:
    value = None
    def __new__(class_, value):
        class_.value = value
        return value

def case(*args):
    return any((arg == Switch.value) for arg in args)

class Inscrire:
    def __init__(self, filepath):
        self.filepath = filepath
        self.tree = None
        self.root = None
        self.load_xml()

    def load_xml(self):
        try:
            self.tree = etree.parse(self.filepath)
            self.root = self.tree.getroot()
        except FileNotFoundError:
            print(f"Erreur: Fichier '{self.filepath}' n'est pas trouvé. Création d'un nouveau fichier.")
            self.root = etree.Element("Scolarite")
            inscrire = etree.SubElement(self.root, "Inscrire")
            self.tree = etree.ElementTree(self.root)
            self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True, doctype='<!DOCTYPE Scolarite SYSTEM "./scolarite.dtd">')
        except Exception as e:
            print(f"Erreur lors du chargement du fichier XML: {e}")
            self.root = etree.Element("Scolarite")
            inscrire = etree.SubElement(self.root, "Inscrire")
            self.tree = etree.ElementTree(self.root)
            self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True, doctype='<!DOCTYPE Scolarite SYSTEM "./scolarite.dtd">')

    def inscrire_etudiant(self, module_id, etu_apo, note, valide):
        # Check if the student exists
        etudiant = self.root.find(f".//Etudiant[@num_apogee='{etu_apo}']")
        if etudiant is None:
            return False, f"Aucun étudiant trouvé avec le numéro Apogée {etu_apo}."

        # Check if the module exists
        module = self.root.find(f".//Module[@id='{module_id}']")
        if module is None:
            return False, f"Aucun module trouvé avec l'ID {module_id}."

        # Check if the student is already enrolled in the module
        existing_inscription = self.root.xpath(f".//Inscrire/Inscription[@module-id='{module_id}' and @etudiant-apogee='{etu_apo}']")
        if existing_inscription:
            return False, f"L'étudiant avec le numéro Apogée {etu_apo} est déjà inscrit dans le module {module_id}."

        # Add the new inscription
        insc = self.root.find("Inscrire")
        if insc is None:
            insc = etree.SubElement(self.root, "Inscrire")

        inscription = etree.Element("Inscription")
        inscription.set("module-id", module_id)
        inscription.set("etudiant-apogee", etu_apo)
        etree.SubElement(inscription, "note").text = note
        etree.SubElement(inscription, "valide").text = valide
        insc.append(inscription)
        self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
        return True, "Inscription réussie!"

    def modifier_note(self, module_id, etu_apo, note):
        for ins in self.root.findall("Inscrire/Inscription"):
            if ins.get("module-id") == module_id and ins.get("etudiant-apogee") == etu_apo:
                ins.find("note").text = note
                if int(note) < 10:
                    ins.find("valide").text = "NV"
                else:
                    ins.find("valide").text = "V"
                self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
                return True, "Note modifiée avec succès!"
        return False, "Le numéro d'apogee ou l'id de module est incorrect!"

    def supprimer_inscription(self, module_id, etu_apo):
        for ins in self.root.findall("Inscrire/Inscription"):
            if ins.get("module-id") == module_id and ins.get("etudiant-apogee") == etu_apo:
                self.root.find("Inscrire").remove(ins)
                self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
                return True, "Inscription supprimée avec succès!"
        return False, "Le numéro d'apogee ou l'id de module est incorrect!"

    def lister_inscription(self):
        inscriptions = self.root.findall("Inscrire/Inscription")
        print(f"Liste des inscriptions: {inscriptions}")  # Debugging
        return inscriptions

class Etudiant:
    def __init__(self, filepath):
        self.filepath = filepath
        try:
            self.tree = etree.parse(filepath)
            self.root = self.tree.getroot()
        except (FileNotFoundError, OSError):
            print(f"Erreur: Le fichier '{filepath}' n'est pas trouvé. Création d'un nouveau fichier.")
            self.root = etree.Element("Scolarite")
            etudiants = etree.SubElement(self.root, "Etudiants")
            self.tree = etree.ElementTree(self.root)
            self.tree.write(filepath, encoding='UTF-8', xml_declaration=True, doctype='<!DOCTYPE Scolarite SYSTEM "./scolarite.dtd">')

    def ajouter_etudiant(self, num_apogee, nom, prenom, cin, date_naiss):
        if self.root.find(f".//Etudiant[@num_apogee='{num_apogee}']") is not None:
            return False, "Un étudiant avec ce numéro Apogée existe déjà."
        etudiants = self.root.find("Etudiants")
        etud = etree.SubElement(etudiants, "Etudiant", num_apogee=num_apogee)
        nom_complet = etree.SubElement(etud, "nom-complet", nom=nom, prenom=prenom)
        cin_element = etree.SubElement(etud, "cin")
        cin_element.text = cin
        date_naiss_element = etree.SubElement(etud, "date-naiss")
        date_naiss_element.text = date_naiss
        self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
        return True, "Étudiant ajouté avec succès!"

    def modifier_etudiant(self, num_apogee, nom, prenom, cin, date_naiss):
        etud = self.root.find(f".//Etudiant[@num_apogee='{num_apogee}']")
        if etud is not None:
            etud.find('nom-complet').set('nom', nom)
            etud.find('nom-complet').set('prenom', prenom)
            etud.find('cin').text = cin
            etud.find('date-naiss').text = date_naiss
            self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
            return True, "Étudiant modifié avec succès!"
        return False, "Aucun étudiant trouvé avec ce numéro Apogée!"

    def supprimer_etudiant(self, num_apogee):
        etud = self.root.find(f".//Etudiant[@num_apogee='{num_apogee}']")
        if etud is not None:
            etud.getparent().remove(etud)
            self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
            return True, "Étudiant supprimé avec succès!"
        return False, "Aucun étudiant trouvé avec ce numéro Apogée!"

    def lister_etudiants(self):
        etudiants = self.root.findall(".//Etudiant")
        print(f"Liste des étudiants: {etudiants}")  # Debugging
        return etudiants

class Enseignant:
    def __init__(self, filepath):
        self.filepath = filepath
        self.tree = None
        self.root = None
        self.load_xml()

    def load_xml(self):
        try:
            self.tree = etree.parse(self.filepath)
            self.root = self.tree.getroot()
        except FileNotFoundError:
            print(f"Erreur: Fichier '{self.filepath}' n'est pas trouvé. Création d'un nouveau fichier.")
            self.root = etree.Element("Scolarite")
            enseignants = etree.SubElement(self.root, "Enseignants")
            self.tree = etree.ElementTree(self.root)
            self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True, doctype='<!DOCTYPE Scolarite SYSTEM "./scolarite.dtd">')
        except Exception as e:
            print(f"Erreur lors du chargement du fichier XML: {e}")
            self.root = etree.Element("Scolarite")
            enseignants = etree.SubElement(self.root, "Enseignants")
            self.tree = etree.ElementTree(self.root)
            self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True, doctype='<!DOCTYPE Scolarite SYSTEM "./scolarite.dtd">')

    def ajouter_enseignant(self, id, nom, prenom, cin, dept):
        if self.root.find(f".//Enseignant[@id='{id}']") is not None:
            return False, "Un enseignant avec cet ID existe déjà."
        enseignants = self.root.find("Enseignants")
        if enseignants is None:
            enseignants = etree.SubElement(self.root, "Enseignants")
        ensg = etree.Element("Enseignant", id=id)
        nom_complet = etree.SubElement(ensg, "nom-complet", nom=nom, prenom=prenom)
        cin_element = etree.SubElement(ensg, "cin")
        cin_element.text = cin
        departement = etree.SubElement(ensg, "departement")
        departement.text = dept
        enseignants.append(ensg)
        self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
        return True, "Enseignant ajouté avec succès!"

    def modifier_enseignant(self, id, nom, prenom, cin, dept):
        for ens in self.root.findall("Enseignants/Enseignant"):
            if ens.get("id") == id:
                ens.find('nom-complet').set('nom', nom)
                ens.find('nom-complet').set('prenom', prenom)
                ens.find('cin').text = cin
                ens.find('departement').text = dept
                self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
                return True, "Enseignant modifié avec succès!"
        return False, "Aucun enseignant trouvé avec cet ID!"

    def supprimer_enseignant(self, id):
        for ens in self.root.findall("Enseignants/Enseignant"):
            if ens.get("id") == id:
                self.root.find("Enseignants").remove(ens)
                self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
                return True, "Enseignant supprimé avec succès!"
        return False, "Aucun enseignant trouvé avec cet ID!"

    def lister_enseignants(self):
        enseignants = self.root.findall("Enseignants/Enseignant")
        print(f"Liste des enseignants: {enseignants}")  # Debugging
        return enseignants

class Module:
    def __init__(self, filepath):
        self.filepath = filepath
        try:
            self.tree = etree.parse(filepath)
            self.root = self.tree.getroot()
        except (FileNotFoundError, OSError):
            print(f"Erreur: Le fichier '{filepath}' n'est pas trouvé. Création d'un nouveau fichier.")
            self.root = etree.Element("Scolarite")
            modules = etree.SubElement(self.root, "Modules")
            self.tree = etree.ElementTree(self.root)
            self.tree.write(filepath, encoding='UTF-8', xml_declaration=True, doctype='<!DOCTYPE Scolarite SYSTEM "./scolarite.dtd">')

    def ajouter_module(self, id, matiere, semestre, enseignant_id):
        # Check if module with the same ID already exists
        if self.root.find(f".//Module[@id='{id}']") is not None:
            return False, "Un module avec cet ID existe déjà."

        # Check if enseignant-id exists in the XML file
        if self.root.find(f".//Enseignant[@id='{enseignant_id}']") is None:
            return False, f"Aucun enseignant trouvé avec l'ID {enseignant_id}."

        # Add the new module
        modules = self.root.find("Modules")
        module = etree.SubElement(modules, "Module", **{"id": id, "enseignant-id": enseignant_id})
        matiere_elem = etree.SubElement(module, "matiere")
        matiere_elem.text = matiere
        semestre_elem = etree.SubElement(module, "semestre")
        semestre_elem.text = semestre
        self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
        return True, "Module ajouté avec succès!"

    def modifier_module(self, id, matiere, semestre, enseignant_id):
        module = self.root.find(f".//Module[@id='{id}']")
        if module is not None:
            # Check if enseignant-id exists in the XML file
            if self.root.find(f".//Enseignant[@id='{enseignant_id}']") is None:
                return False, f"Aucun enseignant trouvé avec l'ID {enseignant_id}."

            module.find('matiere').text = matiere
            module.find('semestre').text = semestre
            module.set('enseignant-id', enseignant_id)
            self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
            return True, "Module modifié avec succès!"
        return False, "Aucun module trouvé avec cet ID!"

    def supprimer_module(self, id):
        module = self.root.find(f".//Module[@id='{id}']")
        if module is not None:
            module.getparent().remove(module)
            self.tree.write(self.filepath, encoding='UTF-8', xml_declaration=True)
            return True, "Module supprimé avec succès!"
        return False, "Aucun module trouvé avec cet ID!"

    def lister_modules(self):
        modules = self.root.findall(".//Module")
        print(f"Liste des modules: {modules}")  # Debugging
        return modules

class ScolariteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Scolarité")
        self.root.geometry("1100x500")
        self.center_window(self.root, 1100, 500)
        self.root.configure(bg="#2c3e50")
        self.root.iconbitmap("images/appIcone.ico")

        self.filepath = "scolarite.xml"
        self.etudiant = Etudiant(self.filepath)
        self.enseignant = Enseignant(self.filepath)
        self.module = Module(self.filepath)
        self.inscrire = Inscrire(self.filepath)

        self.pages = {}
        self.form_entries = {}
        self.tables = {}
        self.selected_item = None

        self.create_main_page()
        self.create_secondary_pages()

        self.show_page("main")

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def on_hover(self, event):
        event.widget.configure(bg="#16a085")

    def on_leave(self, event):
        event.widget.configure(bg="#1abc9c")

    def create_main_page(self):
        page = tk.Frame(self.root, bg="#2c3e50")
        self.pages["main"] = page

        title_font = Font(family="Arial Black", size=20, weight="bold")
        button_font = Font(family="Arial", size=14, weight="bold")

        title_label = tk.Label(
            page,
            text="Gestion de Scolarité",
            font=title_font,
            bg="#2c3e50",
            fg="white"
        )
        title_label.place(relx=0.5, y=60, anchor="center")

        main_frame = tk.Frame(page, bg="#2c3e50")
        main_frame.pack(expand=True)

        image_path = "images/image.png"
        img = Image.open(image_path)
        img_resized = img.resize((750, 242))
        self.photo = ImageTk.PhotoImage(img_resized)
        image_label = tk.Label(main_frame, image=self.photo, bg="#2c3e50")
        image_label.grid(row=0, column=0, rowspan=4, padx=10, pady=12, sticky="n")

        button_frame = tk.Frame(main_frame, bg="#2c3e50")
        button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        buttons = [
            ("Gérer Étudiants", "form_etudiant"),
            ("Gérer Enseignants", "form_enseignant"),
            ("Gérer Modules", "form_module"),
            ("Gérer Inscriptions", "form_inscription")
        ]

        for i, (text, page_name) in enumerate(buttons):
            button = tk.Button(
                button_frame,
                text=text,
                font=button_font,
                bg="#1abc9c",
                fg="white",
                activebackground="#16a085",
                activeforeground="white",
                bd=0,
                padx=20,
                pady=10,
                command=lambda p=page_name: self.show_page(p),
                cursor="hand2"
            )
            button.bind("<Enter>", self.on_hover)
            button.bind("<Leave>", self.on_leave)
            button.grid(row=i, column=0, pady=5, sticky="ew")

        button_frame.grid_columnconfigure(0, weight=1)

        self.add_footer(page)

    def add_footer(self, page):
        footer = tk.Label(
            page,
            text="© 2025 Scolarité App. Tous droits réservés.",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="white"
        )
        footer.pack(side=tk.BOTTOM, pady=10)

    def create_form_page(self, page_name, title, fields, table_columns):
        page = tk.Frame(self.root, bg="#2c3e50")
        self.pages[page_name] = page

        title_font = Font(family="Arial Black", size=20, weight="bold")
        label_font = Font(family="Arial", size=12, weight="bold")
        entry_font = Font(family="Arial", size=12)

        title_label = tk.Label(
            page,
            text=title,
            font=title_font,
            bg="#2c3e50",
            fg="white"
        )
        title_label.place(relx=0.5, y=60, anchor="center")

        form_frame = tk.Frame(page, bg="#2c3e50")
        form_frame.place(relx=0.3, rely=0.5, anchor="center")

        self.form_entries[page_name] = {}

        for i, (field_name, field_type, *extra) in enumerate(fields):
            label = tk.Label(
                form_frame,
                text=field_name,
                font=label_font,
                bg="#2c3e50",
                fg="white"
            )
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            if field_type == "entry":
                entry = tk.Entry(form_frame, font=entry_font)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
                self.form_entries[page_name][field_name] = entry

        form_frame.grid_columnconfigure(1, weight=1)

        table_frame = tk.Frame(page, bg="#2c3e50")
        table_frame.place(relx=0.71, rely=0.5, anchor="center")

        table = ttk.Treeview(table_frame, columns=table_columns, show="headings")
        for col in table_columns:
            table.heading(col, text=col)
            table.column(col, width=100)

        table.grid(row=0, column=0, padx=10, pady=10)

        scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns', padx=5, pady=10)

        table.bind("<ButtonRelease-1>", lambda event: self.on_table_row_select(page_name, table_columns))

        self.tables[page_name] = table

        button_frame = tk.Frame(page, bg="#2c3e50")
        button_frame.place(relx=0.5, rely=0.85, anchor="center")

        def on_hover_x_button(event):
            event.widget.configure(bg="#0c0c0c")

        def on_leave_x_button(event):
            event.widget.configure(bg="Black")

        def on_hover_delete_button(event):
            event.widget.configure(bg="#e74c3c")

        def on_leave_delete_button(event):
            event.widget.configure(bg="#c0392b")

        def clear_inputs():
            for entry in self.form_entries[page_name].values():
                if isinstance(entry, tk.Entry):
                    entry.delete(0, tk.END)

        def add_to_table():
            data = []
            for col in table_columns:
                data.append(self.form_entries[page_name][col].get())
            if page_name == "form_etudiant":
                success, message = self.etudiant.ajouter_etudiant(data[0], data[1], data[2], data[3], data[4])
                if success:
                    self.tables[page_name].insert("", "end", values=data)
                    clear_inputs()
                else:
                    messagebox.showwarning("Erreur", message)
            elif page_name == "form_enseignant":
                success, message = self.enseignant.ajouter_enseignant(data[0], data[1], data[2], data[3], data[4])
                if success:
                    self.tables[page_name].insert("", "end", values=data)
                    clear_inputs()
                else:
                    messagebox.showwarning("Erreur", message)
            elif page_name == "form_module":
                success, message = self.module.ajouter_module(data[0], data[1], data[2], data[3])
                if success:
                    self.tables[page_name].insert("", "end", values=data)
                    clear_inputs()
                else:
                    messagebox.showwarning("Erreur", message)
            elif page_name == "form_inscription":
                success, message = self.inscrire.inscrire_etudiant(data[0], data[1], data[2], data[3])
                if success:
                    self.tables[page_name].insert("", "end", values=data)
                    clear_inputs()
                else:
                    messagebox.showwarning("Erreur", message)

        def delete_from_table():
            selected_item = self.tables[page_name].selection()
            if selected_item:
                data = self.tables[page_name].item(selected_item, "values")
                if page_name == "form_etudiant":
                    success, message = self.etudiant.supprimer_etudiant(data[0])
                    if success:
                        self.tables[page_name].delete(selected_item)
                        clear_inputs()
                    else:
                        messagebox.showwarning("Erreur", message)
                elif page_name == "form_enseignant":
                    success, message = self.enseignant.supprimer_enseignant(data[0])
                    if success:
                        self.tables[page_name].delete(selected_item)
                        clear_inputs()
                    else:
                        messagebox.showwarning("Erreur", message)
                elif page_name == "form_module":
                    success, message = self.module.supprimer_module(data[0])
                    if success:
                        self.tables[page_name].delete(selected_item)
                        clear_inputs()
                    else:
                        messagebox.showwarning("Erreur", message)
                elif page_name == "form_inscription":
                    success, message = self.inscrire.supprimer_inscription(data[0], data[1])
                    if success:
                        self.tables[page_name].delete(selected_item)
                        clear_inputs()
                    else:
                        messagebox.showwarning("Erreur", message)

        def modify_table():
            if not self.selected_item:
                messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une ligne à modifier!")
                return

            data = []
            for col in table_columns:
                data.append(self.form_entries[page_name][col].get())
            if page_name == "form_etudiant":
                success, message = self.etudiant.modifier_etudiant(data[0], data[1], data[2], data[3], data[4])
                if success:
                    self.tables[page_name].item(self.selected_item, values=data)
                    clear_inputs()
                    self.selected_item = None
                else:
                    messagebox.showwarning("Erreur", message)
            elif page_name == "form_enseignant":
                success, message = self.enseignant.modifier_enseignant(data[0], data[1], data[2], data[3], data[4])
                if success:
                    self.tables[page_name].item(self.selected_item, values=data)
                    clear_inputs()
                    self.selected_item = None
                else:
                    messagebox.showwarning("Erreur", message)
            elif page_name == "form_module":
                success, message = self.module.modifier_module(data[0], data[1], data[2], data[3])
                if success:
                    self.tables[page_name].item(self.selected_item, values=data)
                    clear_inputs()
                    self.selected_item = None
                else:
                    messagebox.showwarning("Erreur", message)
            elif page_name == "form_inscription":
                success, message = self.inscrire.modifier_note(data[0], data[1], data[2])
                if success:
                    self.tables[page_name].item(self.selected_item, values=data)
                    clear_inputs()
                    self.selected_item = None
                else:
                    messagebox.showwarning("Erreur", message)

        buttons = [
            ("Vider", clear_inputs),
            ("Ajouter", add_to_table),
            ("Modifier", modify_table),
            ("Supprimer", delete_from_table)
        ]

        for i, (text, command) in enumerate(buttons):
            button = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 12, "bold"),
                bg="Black" if text != "Supprimer" else "#c0392b",
                fg="white",
                activebackground="#0c0c0c" if text != "Supprimer" else "#e74c3c",
                activeforeground="white",
                bd=0,
                padx=20,
                pady=10,
                command=command,
                cursor="hand2"
            )
            if text == "Supprimer":
                button.bind("<Enter>", on_hover_delete_button)
                button.bind("<Leave>", on_leave_delete_button)
            else:
                button.bind("<Enter>", on_hover_x_button)
                button.bind("<Leave>", on_leave_x_button)
            button.grid(row=0, column=i, padx=5, pady=10, sticky="ew")

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        back_button = tk.Button(
            page,
            text="Retour",
            font=("Arial", 12, "bold"),
            bg="#1abc9c",
            fg="white",
            activebackground="#16a085",
            activeforeground="white",
            bd=0,
            padx=20,
            pady=10,
            command=lambda: self.show_page("main"),
            cursor="hand2"
        )
        back_button.place(relx=0.9, y=60, anchor="center")
        back_button.bind("<Enter>", self.on_hover)
        back_button.bind("<Leave>", self.on_leave)

        page.pack_propagate(False)
        page.pack(fill="both", expand=True)

        self.add_footer(page)

    def on_table_row_select(self, page_name, table_columns):
        self.selected_item = self.tables[page_name].selection()
        if self.selected_item:
            row_values = self.tables[page_name].item(self.selected_item, "values")
            for col, value in zip(table_columns, row_values):
                self.form_entries[page_name][col].delete(0, tk.END)
                self.form_entries[page_name][col].insert(0, value)

    def create_secondary_pages(self):
        self.create_form_page("form_etudiant", "Espace des Étudiants", [
            ("Appoge", "entry"),
            ("Nom", "entry"),
            ("Prenom", "entry"),
            ("CIN", "entry"),
            ("Date Naissance", "entry")
        ], ["Appoge", "Nom", "Prenom", "CIN", "Date Naissance"])

        self.create_form_page("form_module", "Espace des Modules", [
            ("Id", "entry"),
            ("Matière", "entry"),
            ("Semestre", "entry"),
            ("Enseignant ID", "entry")
        ], ["Id", "Matière", "Semestre", "Enseignant ID"])

        self.create_form_page("form_enseignant", "Espace des Enseignants", [
            ("Id", "entry"),
            ("Nom", "entry"),
            ("Prenom", "entry"),
            ("CIN", "entry"),
            ("Département", "entry")
        ], ["Id", "Nom", "Prenom", "CIN", "Département"])

        self.create_form_page("form_inscription", "Espace des Inscriptions", [
            ("Id-Module", "entry"),
            ("Id-Etudiant", "entry"),
            ("Note", "entry"),
            ("Valide", "entry")
        ], ["Id-Module","Id-Etudiant",  "Note", "Valide"])

    def show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_name].pack(fill="both", expand=True)
        self.current_page = page_name

        if page_name == "form_etudiant":
            self.load_data_to_table(page_name, self.etudiant.lister_etudiants(), ["num_apogee", "nom", "prenom", "cin", "date-naiss"])
        elif page_name == "form_enseignant":
            self.load_data_to_table(page_name, self.enseignant.lister_enseignants(), ["id", "nom", "prenom", "cin", "departement"])
        elif page_name == "form_module":
            self.load_data_to_table(page_name, self.module.lister_modules(), ["id", "matiere", "semestre", "enseignant-id"])
        elif page_name == "form_inscription":
            self.load_data_to_table(page_name, self.inscrire.lister_inscription(), ["module-id", "etudiant-apogee", "note", "valide"])

    def load_data_to_table(self, page_name, data, columns):
        table = self.tables[page_name]
        table.delete(*table.get_children())
        for item in data:
            row = []
            for col in columns:
                if col == "nom" or col == "prenom":
                    row.append(item.find("nom-complet").get(col))
                else:
                    row.append(item.get(col) if item.get(col) is not None else item.find(col).text)
            table.insert("", "end", values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScolariteApp(root)
    root.mainloop()