import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import json
import re
import requests
import os 
from typing import Optional


class CreateToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     
        self.wraplength = 300   
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.id = None
        self.tw = None
    def enter(self, event=None):
        self.schedule()
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)
    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)
    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         wraplength = self.wraplength)
        label.pack(ipadx=1)
    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()


class ReactionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IGN software | Reaction App")

        # Размеры главного окна 
        win_width, win_height = 800, 600  # можно подогнать под твой интерфейс

        # Размеры экрана
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Координаты для центрирования
        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 2) - (win_height // 2)

        # Установка геометрии
        self.geometry(f"{win_width}x{win_height}+{x}+{y}")

        # Иконку из той же папки
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Не удалось загрузить иконку: {e}")

        self.reagent_entries = {}
        self.num_reagents_var = tk.IntVar(value=3)
        self.first_moles_var = tk.DoubleVar(value=0.005)
        self.last_result_df = None

        self.create_widgets()

    def create_widgets(self):
        # Верхняя панель
        top = tk.Frame(self)
        top.pack(pady=10, fill=tk.X)

        tk.Label(top, text="Number of reagents:").pack(side=tk.LEFT, padx=10)
        spin = tk.Spinbox(top, from_=1, to=20, textvariable=self.num_reagents_var, width=5)
        spin.pack(side=tk.LEFT, padx=5)
        
        btn_create = tk.Button(top, text="Create table", command=self.create_table)
        btn_create.pack(side=tk.LEFT, padx=10)
        CreateToolTip(btn_create, "Create input table with specified number of reagents")

        # NEW: кнопка "?" справа
        btn_help = tk.Button(top, text="(?)", command=self.show_contacts)
        btn_help.pack(side=tk.RIGHT, padx=10)
        CreateToolTip(btn_help, "Show contact info")

        self.table_frame = tk.Frame(self)
        self.table_frame.pack(pady=10, fill=tk.X)

        moles_frame = tk.Frame(self)
        moles_frame.pack(pady=5, anchor="w")  # anchor="w" выравнивает влево

        tk.Label(moles_frame, text="Moles of first reagent:").pack(side=tk.LEFT, padx=10)  # такой же отступ
        ent_moles = tk.Entry(moles_frame, textvariable=self.first_moles_var, width=10)
        ent_moles.pack(side=tk.LEFT, padx=5)
        CreateToolTip(ent_moles, "Set the amount in moles of the first reagent")


        buttons = tk.Frame(self)
        buttons.pack(pady=10)

        btn_calc = tk.Button(buttons, text="Calculate", command=self.calculate)
        btn_calc.pack(side=tk.LEFT, padx=10)
        CreateToolTip(btn_calc, "Calculate quantities based on input data")

        btn_save_txt = tk.Button(buttons, text="Save to .txt", command=self.save_result)
        btn_save_txt.pack(side=tk.LEFT, padx=10)
        CreateToolTip(btn_save_txt, "Save last calculation result to a text file")

        btn_load_txt = tk.Button(buttons, text="Import from .txt", command=self.load_from_txt)
        btn_load_txt.pack(side=tk.LEFT, padx=10)
        CreateToolTip(btn_load_txt, "Import reagent data from a tab-separated text file")

        btn_save_multi = tk.Button(buttons, text="Save multi-preset", command=self.save_multi_preset)
        btn_save_multi.pack(side=tk.LEFT, padx=10)
        CreateToolTip(btn_save_multi, "Save multiple columns presets into a JSON file")

        btn_load_multi = tk.Button(buttons, text="Load multi-preset", command=self.load_multi_preset)
        btn_load_multi.pack(side=tk.LEFT, padx=10)
        CreateToolTip(btn_load_multi, "Load multiple columns presets from a JSON file")

        btn_autofill = tk.Button(buttons, text="Auto-fill from PubChem", command=self.autofill_from_pubchem)
        btn_autofill.pack(side=tk.LEFT, padx=10)
        CreateToolTip(btn_autofill, "Auto-fetch molar mass and density by reagent name")

        self.result_text = tk.Text(self, height=20)
        self.result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def show_contacts(self):
        win = tk.Toplevel(self)
        win.title("Contacts")
        win.resizable(False, False)

        # Размеры окна контакта
        win_width, win_height = 400, 180

        # Геометрия окна
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        
        parent_w = self.winfo_width()
        parent_h = self.winfo_height()

        # Центрирование
        x = parent_x + (parent_w // 2 - win_width // 2)
        y = parent_y + (parent_h // 2 - win_height // 2)

        win.geometry(f"{win_width}x{win_height}+{x}+{y}")

        # Заголовок
        tk.Label(
            win,
            text="If you have suggestions or found a problem,\nplease contact me:",
            font=("Arial", 10, "italic"),
            justify="center",
            fg="gray20"
        ).pack(pady=(10, 15))

        contacts = {
            "📧 Email": "ivanguzeknovikov881@gmail.com",
        }

        frame = tk.Frame(win)
        frame.pack(pady=5)

        def copy_to_clipboard(value: str):
            self.clipboard_clear()
            self.clipboard_append(value)
            self.update()

            status.config(text=f"Copied: {value}", fg="green")
            win.after(2000, lambda: status.config(text=""))

        row = 0
        for label, value in contacts.items():
            tk.Label(frame, text=label, anchor="w").grid(row=row, column=0, padx=10, pady=5, sticky="w")

            entry = tk.Entry(frame, width=30, bd=0, relief="flat", fg="blue")
            entry.insert(0, value)
            entry.configure(state="readonly")
            entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")

            tk.Button(frame, text="Copy", command=lambda v=value: copy_to_clipboard(v))\
                .grid(row=row, column=2, padx=5, pady=5)
            row += 1

        status = tk.Label(win, text="", font=("Arial", 9))
        status.pack(pady=(5, 5))


    def create_table(self):
        props = ["Str. Name", "Molar ratio", "Molar mass (g/mol)", "Density (g/mL)"]

        if not self.reagent_entries:
            self.reagent_entries = {p: [] for p in props}

            tk.Label(self.table_frame, text="Property", borderwidth=1, relief="ridge", width=15)\
                .grid(row=0, column=0, sticky="nsew")
            for r, prop in enumerate(props, start=1):
                tk.Label(self.table_frame, text=prop, borderwidth=1, relief="ridge", width=15)\
                    .grid(row=r, column=0, sticky="nsew")

        current_n = len(self.reagent_entries["Str. Name"])
        requested_n = self.num_reagents_var.get()

        # Убавить колонки
        if requested_n < current_n:
            for c in range(requested_n, current_n):
                for r in range(len(props)+2):
                    for w in self.table_frame.grid_slaves(row=r, column=c+1):
                        w.destroy()
            for k in self.reagent_entries.keys():
                self.reagent_entries[k] = self.reagent_entries[k][:requested_n]

        # Добавить колонки
        elif requested_n > current_n:
            for c in range(current_n, requested_n):
                tk.Label(self.table_frame, text=f"Reagent {c+1}", borderwidth=1, relief="ridge", width=15)\
                    .grid(row=0, column=c+1, sticky="nsew")

                for r, prop in enumerate(props, start=1):
                    e = tk.Entry(self.table_frame, width=17)
                    e.grid(row=r, column=c+1, padx=1, pady=1)
                    if prop == "Molar ratio":
                        e.insert(0, "1.0")
                    elif prop == "Molar mass (g/mol)":
                        e.insert(0, "0")
                    self.reagent_entries[prop].append(e)

                btn_save = tk.Button(self.table_frame, text="💾", width=3, command=lambda col=c: self.save_single_preset(col))
                btn_load = tk.Button(self.table_frame, text="📂", width=3, command=lambda col=c: self.load_single_preset(col))
                btn_save.grid(row=len(props)+1, column=c+1, sticky="w")
                btn_load.grid(row=len(props)+1, column=c+1, sticky="e")
                CreateToolTip(btn_save, f"Save preset for Reagent {c+1}")
                CreateToolTip(btn_load, f"Load preset for Reagent {c+1}")
                
        # После добавления/удаления столбцов
        total_columns = len(self.reagent_entries["Str. Name"])
        base_width = 1000  # ширина окна
        column_width = 120  # ширина на каждый реагент
        max_visible = 6     # количество реагентов, умещающихся без скролла

        # Увеличиваем ширину окна
        if total_columns > max_visible:
            new_width = base_width + (total_columns - max_visible) * column_width
            self.geometry(f"{new_width}x600")
        else:
            self.geometry("1000x600")  # сброс ширины


    def autofill_from_pubchem(self):
        if not self.reagent_entries:
            messagebox.showerror("Error", "Create table first!")
            return

        for i, name_entry in enumerate(self.reagent_entries["Str. Name"]):
            name = name_entry.get().strip()
            if not name:
                continue

            try:
                props = self.get_pubchem_properties(name)

                # Молярная масса
                mw_entry = self.reagent_entries["Molar mass (g/mol)"][i]
                if "Molecular Weight" in props:
                    mw_entry.delete(0, tk.END)
                    mw_entry.insert(0, str(props["Molecular Weight"]))

                # Плотность
                dens_entry = self.reagent_entries["Density (g/mL)"][i]
                if "Density" in props and props["Density"] is not None:
                    dens_entry.delete(0, tk.END)
                    dens_entry.insert(0, str(props["Density"]))

            except Exception as e:
                print(f"Error fetching for '{name}': {e}")


    def save_single_preset(self, col):
        if not self.reagent_entries:
            messagebox.showerror("Error", "Create table first!")
            return
        data = {k: v[col].get() for k,v in self.reagent_entries.items()}
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Preset", "*.json")])
        if f:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=3)
            messagebox.showinfo("OK", f"Saved to {f}")

    def load_single_preset(self, col):
        if not self.reagent_entries:
            messagebox.showerror("Error", "Create table first!")
            return
        f = filedialog.askopenfilename(filetypes=[("JSON Preset", "*.json")])
        if f:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            for k,v in self.reagent_entries.items():
                if k in data:
                    v[col].delete(0, tk.END)
                    v[col].insert(0, data[k])
            messagebox.showinfo("OK", f"Loaded from {f}")

    def _parse_cols(self, s: str):
        s = s.replace(' ', '')
        result = []
        for part in s.split(','):
            if '-' in part:
                try:
                    a,b = map(int, part.split('-'))
                    result.extend(range(a,b+1))
                except: pass
            else:
                if part.isdigit():
                    result.append(int(part))
        return sorted(set(result))

    def save_multi_preset(self):
        if not self.reagent_entries:
            messagebox.showerror("Error", "Create table first!")
            return
        cols_str = simpledialog.askstring("Columns", "Which columns to save? (e.g. 2,3,4):")
        if not cols_str: return
        cols = self._parse_cols(cols_str)
        if not cols:
            messagebox.showerror("Error", "No valid columns found")
            return

        payload = {"cols": []}
        for col in cols:
            if 1 <= col <= len(self.reagent_entries["Str. Name"]):
                onecol = {}
                for k, lst in self.reagent_entries.items():
                    onecol[k] = lst[col-1].get()
                payload["cols"].append({"index": col, "data": onecol})

        f = filedialog.asksaveasfilename(defaultextension=".json",
                                         filetypes=[("JSON Multi Preset", "*.json")])
        if f:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(payload, fp, indent=4)
            messagebox.showinfo("OK", f"Saved {len(payload['cols'])} columns")

    def load_multi_preset(self):
        if not self.reagent_entries:
            messagebox.showerror("Error", "Create table first!")
            return
        f = filedialog.askopenfilename(filetypes=[("JSON Multi Preset", "*.json")])
        if not f: return

        with open(f, "r", encoding="utf-8") as fp:
            payload = json.load(fp)

        if "cols" not in payload:
            messagebox.showerror("Error", "File is not a multi-preset")
            return

        use_same_positions = messagebox.askyesno(
            "Insert mode",
            "Insert into original positions?\n(Yes = replace saved indexes, No = ask for start position)"
        )

        if use_same_positions:
            maxcols = len(self.reagent_entries["Str. Name"])
            for item in payload["cols"]:
                idx = item["index"] - 1
                if 0 <= idx < maxcols:
                    for k, lst in self.reagent_entries.items():
                        lst[idx].delete(0, tk.END)
                        lst[idx].insert(0, item["data"][k])
            messagebox.showinfo("OK", f"Inserted {len(payload['cols'])} columns at original positions")
        else:
            start_col_str = simpledialog.askstring("Start", "Start inserting from which column?")
            if not start_col_str or not start_col_str.isdigit(): return
            start = int(start_col_str) - 1
            maxcols = len(self.reagent_entries["Str. Name"])
            for i, item in enumerate(payload["cols"]):
                idx = start + i
                if 0 <= idx < maxcols:
                    for k, lst in self.reagent_entries.items():
                        lst[idx].delete(0, tk.END)
                        lst[idx].insert(0, item["data"][k])
            messagebox.showinfo("OK", f"Inserted {len(payload['cols'])} columns starting at {start+1}")

    def calculate(self):
        if not self.reagent_entries:
            messagebox.showerror("Error", "Create table first!")
            return
        try:
            # Колонки
            names = [e.get().strip() or f"Reagent {i+1}" for i, e in enumerate(self.reagent_entries["Str. Name"])]

            # Считываем свойства
            ratios = [float(e.get()) for e in self.reagent_entries["Molar ratio"]]
            masses = [float(e.get()) for e in self.reagent_entries["Molar mass (g/mol)"]]

            densities = []
            for e in self.reagent_entries["Density (g/mL)"]:
                val = e.get().strip()
                if val == "" or val.lower() in ("none", "нет", "no"):
                    densities.append(None)
                else:
                    try:
                        densities.append(float(val))
                    except:
                        densities.append(None)

            # Расчёт по первому реагенту
            first_moles = self.first_moles_var.get()
            if ratios[0] == 0:
                messagebox.showerror("Error", "First reagent ratio cannot be zero.")
                return
            k = first_moles / ratios[0]
            mols = [round(k * r, 6) for r in ratios]
            grams = [round(m * mm, 6) for m, mm in zip(mols, masses)]
            vol_ml = [round(g / d, 4) if d else "—" for g, d in zip(grams, densities)]
            vol_ul = [round(v * 1000, 1) if isinstance(v, float) else "—" for v in vol_ml]

            # Плотности
            densities_display = [d if d is not None else "—" for d in densities]

            # DataFrame
            df = pd.DataFrame({
                "Molar ratio": ratios,
                "Moles": mols,
                "Molar mass (g/mol)": masses,
                "Density (g/mL)": densities_display,
                "mass (g)": grams,
                "Vol (ml)": vol_ml,
                "Vol (µL)": vol_ul
            }, index=names).T

            self.last_result_df = df
            # Выводим в текстовое поле
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, df.to_string())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_result(self):
        if self.last_result_df is None:
            messagebox.showwarning("Warning", "Calculate first!")
            return
        f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")])
        if f:
            # last_result_df уже в нужном виде: строки — свойства, столбцы — реагенты
            df_to_save = self.last_result_df.copy()

            # Заменяем None и NaN на прочерк
            df_to_save = df_to_save.fillna("—")
            for c in df_to_save.columns:
                df_to_save[c] = df_to_save[c].replace(["", None, "nan", "NaN"], "—")

            df_to_save.to_csv(f, sep='\t', index=True, header=True)
            messagebox.showinfo("Saved", f"Saved to {f}")

    def load_from_txt(self):
        f = filedialog.askopenfilename(filetypes=[("Text files","*.txt"),("All files","*.*")])
        if not f:
            return
        try:
            # Считаем, где индекс — это строки (свойства), а колонки — реагенты (названия)
            df = pd.read_csv(f, sep='\t', index_col=0, engine='python')

            # Проверим, что нужные свойства есть
            required_props = ["Molar ratio", "Molar mass (g/mol)"]
            for p in required_props:
                if p not in df.index:
                    messagebox.showerror("Error", f"File missing required property: {p}")
                    return

            # Извлечём названия реагентов (колонки)
            reagents = list(df.columns)
            n = len(reagents)
            self.num_reagents_var.set(n)
            self.create_table()

            # Заполняем форму
            for i, reagent in enumerate(reagents):
                # Название реагента
                self.reagent_entries["Str. Name"][i].delete(0, tk.END)
                self.reagent_entries["Str. Name"][i].insert(0, reagent)

                # И заполняем остальные параметры
                for param in ["Molar ratio", "Molar mass (g/mol)", "Density (g/mL)"]:
                    val = df.at[param, reagent] if param in df.index else ""
                    if pd.isna(val):
                        val = ""
                    self.reagent_entries[param][i].delete(0, tk.END)
                    self.reagent_entries[param][i].insert(0, str(val))

            messagebox.showinfo("Success", f"Loaded {n} reagents from {f}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")
    def get_cid_by_name(self, name: str) -> Optional[int]:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/TXT"
        r = requests.get(url, timeout=10)
        if r.ok and r.text.strip():
            return int(r.text.strip().split()[0])
        return None

    def search_property(self, sections, target: str):
        for sec in sections:
            if sec.get("TOCHeading") == target:
                for info in sec.get("Information", []):
                    vals = info.get("Value", {}).get("StringWithMarkup", [])
                    if vals:
                        return [v.get("String") for v in vals]
            for info in sec.get("Information", []):
                if info.get("Name") == target:
                    vals = info.get("Value", {}).get("StringWithMarkup", [])
                    if vals:
                        return [v.get("String") for v in vals]
            if "Section" in sec:
                found = self.search_property(sec["Section"], target)
                if found:
                    return found
        return None

    def get_pubchem_json(self, cid: int):
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
        r = requests.get(url, timeout=10)
        if not r.ok:
            raise RuntimeError(f"Ошибка запроса: {r.status_code}")
        return r.json()

    def clean_density(self, raw_list):
        if not raw_list:
            return None
        text = raw_list[0]
        m = re.search(r"([\d\.]+)\s*(g/cm³|g/cm3)?", text)
        density = m.group(1) if m else None
        return density

    def clean_temperature(self, raw_list):
        if not raw_list:
            return None
        text = raw_list[0]
        tmatch = re.search(r"([\d\.\-]+)\s*°F", text)
        if tmatch:
            temp_f = float(tmatch.group(1))
            temp_c = round((temp_f - 32) * 5/9, 1)
            return f"{temp_c} °C"
        return text

    def get_pubchem_properties(self, name: str) -> dict:
        cid = self.get_cid_by_name(name)
        if cid is None:
            return {}
        data = self.get_pubchem_json(cid)
        sections = data.get("Record", {}).get("Section", [])
        result = {}
        raw_density = self.search_property(sections, "Density")
        raw_mw = self.search_property(sections, "Molecular Weight")
        if raw_density:
            result["Density"] = self.clean_density(raw_density)
        if raw_mw:
            try:
                result["Molecular Weight"] = float(raw_mw[0].split()[0])
            except:
                pass
        return result


if __name__ == "__main__":
    app = ReactionApp()
    app.mainloop()

#собирать так:
#python -m PyInstaller --onefile --noconsole --icon=icon.ico --add-data "icon.ico;." reaction_app_6.py