import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import json

class ReactionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reaction Calculator v3.0")
        self.geometry("1000x600")

        self.reagent_entries = {}
        self.num_reagents_var = tk.IntVar(value=3)
        self.first_moles_var = tk.DoubleVar(value=0.5)
        self.last_result_df = None

        self.create_widgets()

    def create_widgets(self):
        top = tk.Frame(self)
        top.pack(pady=10)
        tk.Label(top, text="Number of reagents:").pack(side=tk.LEFT)
        tk.Spinbox(top, from_=1, to=20, textvariable=self.num_reagents_var, width=5).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Create table", command=self.create_table).pack(side=tk.LEFT, padx=10)

        self.table_frame = tk.Frame(self)
        self.table_frame.pack(pady=10, fill=tk.X)

        moles_frame = tk.Frame(self)
        moles_frame.pack(pady=5)
        tk.Label(moles_frame, text="Moles of first reagent:").pack(side=tk.LEFT)
        tk.Entry(moles_frame, textvariable=self.first_moles_var, width=10).pack(side=tk.LEFT, padx=5)

        buttons = tk.Frame(self)
        buttons.pack(pady=10)
        tk.Button(buttons, text="Calculate", command=self.calculate).pack(side=tk.LEFT, padx=10)
        tk.Button(buttons, text="Save to .txt", command=self.save_result).pack(side=tk.LEFT, padx=10)
        tk.Button(buttons, text="Save multi‑preset", command=self.save_multi_preset).pack(side=tk.LEFT, padx=10)
        tk.Button(buttons, text="Load multi‑preset", command=self.load_multi_preset).pack(side=tk.LEFT, padx=10)



        self.result_text = tk.Text(self, height=20)
        self.result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def create_table(self):
        props = ["Str. Name", "Molar ratio", "Molar mass (g/mol)", "Density (g/mL)"]

        # Если таблица ещё не создана – создаём с нуля
        if not self.reagent_entries:
            self.reagent_entries = {p: [] for p in props}

            # Заголовок свойств
            tk.Label(self.table_frame, text="Property", borderwidth=1, relief="ridge", width=15)\
                .grid(row=0, column=0, sticky="nsew")
            for r, prop in enumerate(props, start=1):
                tk.Label(self.table_frame, text=prop, borderwidth=1, relief="ridge", width=15)\
                    .grid(row=r, column=0, sticky="nsew")

        current_n = len(self.reagent_entries["Str. Name"])
        requested_n = self.num_reagents_var.get()

        # === Если нужно убрать лишние колонки ===
        if requested_n < current_n:
            # Удаляем виджеты этих колонок
            for c in range(requested_n, current_n):
                for r in range(len(props)+2):  # +2 для строки с кнопками
                    for w in self.table_frame.grid_slaves(row=r, column=c+1):
                        w.destroy()
            # Обрезаем списки entries
            for k in self.reagent_entries.keys():
                self.reagent_entries[k] = self.reagent_entries[k][:requested_n]

        # === Если нужно добавить новые колонки ===
        elif requested_n > current_n:
            for c in range(current_n, requested_n):
                # Заголовок
                tk.Label(self.table_frame, text=f"Reagent {c+1}", borderwidth=1, relief="ridge", width=15)\
                    .grid(row=0, column=c+1, sticky="nsew")

                # Поля ввода
                for r, prop in enumerate(props, start=1):
                    e = tk.Entry(self.table_frame, width=17)
                    e.grid(row=r, column=c+1, padx=1, pady=1)
                    if prop == "Molar ratio":
                        e.insert(0, "1.0")
                    elif prop == "Molar mass (g/mol)":
                        e.insert(0, "60.0")
                    self.reagent_entries[prop].append(e)

                # Кнопки пресетов для этой колонки
                btn_save = tk.Button(self.table_frame, text="💾", width=3, command=lambda col=c: self.save_single_preset(col))
                btn_load = tk.Button(self.table_frame, text="📂", width=3, command=lambda col=c: self.load_single_preset(col))
                btn_save.grid(row=len(props)+1, column=c+1, sticky="w")
                btn_load.grid(row=len(props)+1, column=c+1, sticky="e")


    # ========== одиночный пресет ==========
    def save_single_preset(self, col):
        if not self.reagent_entries:
            messagebox.showerror("Error","Create table first!")
            return
        data = {k: v[col].get() for k,v in self.reagent_entries.items()}
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Preset","*.json")])
        if f:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=3)
            messagebox.showinfo("OK", f"Сохранено в {f}")

    def load_single_preset(self, col):
        if not self.reagent_entries:
            messagebox.showerror("Error","Create table first!")
            return
        f = filedialog.askopenfilename(filetypes=[("JSON Preset","*.json")])
        if f:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            for k,v in self.reagent_entries.items():
                if k in data:
                    v[col].delete(0, tk.END)
                    v[col].insert(0, data[k])
            messagebox.showinfo("OK", f"Загружено из {f}")

    # ========== мульти‑пресет ==========
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
        cols_str = simpledialog.askstring("Columns", "Какие колонки сохранить? (например 2,3,4):")
        if not cols_str: return
        cols = self._parse_cols(cols_str)
        if not cols:
            messagebox.showerror("Error", "Нет корректных колонок")
            return

        payload = {"cols": []}
        for col in cols:
            if 1 <= col <= len(self.reagent_entries["Str. Name"]):
                onecol = {}
                for k, lst in self.reagent_entries.items():
                    onecol[k] = lst[col-1].get()
                payload["cols"].append({"index": col, "data": onecol})

        f = filedialog.asksaveasfilename(defaultextension=".json",
                                         filetypes=[("JSON Multi Preset","*.json")])
        if f:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(payload, fp, indent=4)
            messagebox.showinfo("OK", f"Сохранено {len(payload['cols'])} колонок")


    def load_multi_preset(self):
        if not self.reagent_entries:
            messagebox.showerror("Error","Create table first!")
            return
        f = filedialog.askopenfilename(filetypes=[("JSON Multi Preset","*.json")])
        if not f: return

        with open(f, "r", encoding="utf-8") as fp:
            payload = json.load(fp)

        if "cols" not in payload:
            messagebox.showerror("Error","Файл не мультипресет")
            return

        # спросим пользователя: вставлять в те же колонки или со сдвигом?
        use_same_positions = messagebox.askyesno(
            "Insert mode",
            "Вставить в исходные позиции?\n(Да = заменить именно сохранённые индексы, Нет = спросить начальную позицию)"
        )

        if use_same_positions:
            # заменяем ровно те колонки, которые были сохранены
            maxcols = len(self.reagent_entries["Str. Name"])
            for item in payload["cols"]:
                idx = item["index"] - 1
                if 0 <= idx < maxcols:
                    for k, lst in self.reagent_entries.items():
                        lst[idx].delete(0, tk.END)
                        lst[idx].insert(0, item["data"][k])
            messagebox.showinfo("OK", f"Вставлено {len(payload['cols'])} колонок (по исходным позициям)")
        else:
            # вставляем начиная с указанной колонки подряд
            start_col_str = simpledialog.askstring("Start", "С какой колонки начать вставку?")
            if not start_col_str or not start_col_str.isdigit(): return
            start = int(start_col_str) - 1
            maxcols = len(self.reagent_entries["Str. Name"])
            for i, item in enumerate(payload["cols"]):
                idx = start + i
                if 0 <= idx < maxcols:
                    for k, lst in self.reagent_entries.items():
                        lst[idx].delete(0, tk.END)
                        lst[idx].insert(0, item["data"][k])
            messagebox.showinfo("OK", f"Вставлено {len(payload['cols'])} колонок начиная с {start+1}")


    # ========== расчёт ==========
    def calculate(self):
        if not self.reagent_entries:
            messagebox.showerror("Error", "Create table first!")
            return
        try:
            names = [e.get().strip() or f"Reagent {i+1}" for i,e in enumerate(self.reagent_entries["Str. Name"])]
            ratios = [float(e.get()) for e in self.reagent_entries["Molar ratio"]]
            masses = [float(e.get()) for e in self.reagent_entries["Molar mass (g/mol)"]]
            densities = []
            for e in self.reagent_entries["Density (g/mL)"]:
                val = e.get().strip().lower()
                densities.append(float(val) if val not in ("", "none", "нет") else None)

            first_moles = self.first_moles_var.get()
            if ratios[0] == 0:
                messagebox.showerror("Error","First reagent ratio cannot be zero.")
                return
            k = first_moles / ratios[0]
            mols = [round(k*r,4) for r in ratios]
            grams = [round(m*mm,4) for m,mm in zip(mols,masses)]
            vml = [round(g/d,4) if d else "—" for g,d in zip(grams,densities)]
            vmkl = [round(v*1000,2) if isinstance(v,float) else "—" for v in vml]

            df = pd.DataFrame({
                "Molar ratio": ratios,
                "Moles": mols,
                "Molar mass (g/mol)": masses,
                "mass (g)": grams,
                "Vol (ml)": vml,
                "Vol (µL)": vmkl
            }, index=names).T

            self.last_result_df = df
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, df.to_string())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_result(self):
        if self.last_result_df is None:
            messagebox.showwarning("Warning","Сначала посчитай!")
            return
        f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")])
        if f:
            self.last_result_df.to_csv(f, sep='\t', index=True, header=True, float_format="%.4f")
            messagebox.showinfo("Saved", f"Сохранено в {f}")

if __name__ == "__main__":
    app = ReactionApp()
    app.mainloop()
