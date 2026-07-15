import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os

class ReactionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reaction Calculator")
        self.geometry("500x400")
        
        self.reagent_entries = []  # для хранения виджетов по реагентам
        
        # Переменные и виджеты
        self.num_reagents_var = tk.IntVar(value=3)
        self.first_moles_var = tk.DoubleVar(value=0.5)
        self.last_result_df = None
        
        self.create_widgets()

    def create_widgets(self):
        # Ввод количества реагентов
        top_frame = tk.Frame(self)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Number of reagents:").pack(side=tk.LEFT)
        tk.Spinbox(top_frame, from_=1, to=10, textvariable=self.num_reagents_var, width=5).pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Create table", command=self.create_table).pack(side=tk.LEFT, padx=10)
        
        # Контейнер для динамических полей
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(pady=10, fill=tk.X)
        
        # Ввод молей первого реагента
        moles_frame = tk.Frame(self)
        moles_frame.pack(pady=5)
        tk.Label(moles_frame, text="Moles of first reagent:").pack(side=tk.LEFT)
        tk.Entry(moles_frame, textvariable=self.first_moles_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Кнопки
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(pady=10)
        tk.Button(buttons_frame, text="Calculate", command=self.calculate).pack(side=tk.LEFT, padx=10)
        tk.Button(buttons_frame, text="Save to .txt", command=self.save_result).pack(side=tk.LEFT, padx=10)
        
        # Окно вывода результата (таблица)
        self.result_text = tk.Text(self, height=15)
        self.result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def create_table(self):
        # Очищаем старые виджеты
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.reagent_entries.clear()

        n = self.num_reagents_var.get()
        
        # Заголовки
        headers = ["Property ↓"] + [f"Reagent {i+1}" for i in range(n)]
        for col, text in enumerate(headers):
            lbl = tk.Label(self.table_frame, text=text, borderwidth=1, relief="ridge", width=15)
            lbl.grid(row=0, column=col, sticky="nsew")
        
        properties = ["Molar ratio", "Molar mass (g/mol)", "Density (g/mL)"]
        
        self.reagent_entries = {prop: [] for prop in properties}

        for row, prop in enumerate(properties, start=1):
            lbl = tk.Label(self.table_frame, text=prop, borderwidth=1, relief="ridge", width=15)
            lbl.grid(row=row, column=0, sticky="nsew")
            for col in range(n):
                ent = tk.Entry(self.table_frame, width=17)
                ent.grid(row=row, column=col+1, sticky="nsew", padx=1, pady=1)
                # Значения по умолчанию
                if prop == "Molar ratio":
                    ent.insert(0, "1.0")
                elif prop == "Molar mass (g/mol)":
                    ent.insert(0, "60.0")
                else:
                    ent.insert(0, "")  # пусто для плотности
                self.reagent_entries[prop].append(ent)

    def calculate(self):
        if not self.reagent_entries:
            messagebox.showerror("Error", "Create the table first.")
            return
        
        try:
            names = [f"Reagent {i+1}" for i in range(len(self.reagent_entries["Molar ratio"]))]
            ratios = [float(e.get()) for e in self.reagent_entries["Molar ratio"]]
            masses = [float(e.get()) for e in self.reagent_entries["Molar mass (g/mol)"]]
            
            densities = []
            for e in self.reagent_entries["Density (g/mL)"]:
                val = e.get().strip().lower()
                if val in ("", "none", "нет"):
                    densities.append(None)
                else:
                    densities.append(float(val))
            
            first_moles = self.first_moles_var.get()
            if ratios[0] == 0:
                messagebox.showerror("Error", "First reagent molar ratio cannot be zero.")
                return
            k = first_moles / ratios[0]

            mols = [round(k * r, 4) for r in ratios]
            grams = [round(m * mm, 4) for m, mm in zip(mols, masses)]
            vols = [round(g / d, 4) if d else "—" for g, d in zip(grams, densities)]

            df = pd.DataFrame({
                name: [r, m, g, v] for name, r, m, g, v in zip(names, ratios, mols, grams, vols)
            }, index=["Molar ratio", "Moles", "Mass (g)", "Volume (mL)"])
            
            self.last_result_df = df
            self.show_result(df)

        except Exception as e:
            messagebox.showerror("Error", f"Calculation error:\n{e}")

    def show_result(self, df):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, df.to_string())
    
    def save_result(self):
        if self.last_result_df is None:
            messagebox.showwarning("Warning", "Calculate the result first.")
            return

        # Диалог выбора папки для сохранения
        folder = filedialog.askdirectory(title="Select folder to save the result")
        if not folder:
            return

        base_name = "reaction_result"
        ext = ".txt"
        existing_files = [f for f in os.listdir(folder) if f.startswith(base_name) and f.endswith(ext)]
        numbers = []
        for f in existing_files:
            try:
                num = int(f[len(base_name):-len(ext)])
                numbers.append(num)
            except:
                pass
        next_num = max(numbers) + 1 if numbers else 1
        file_path = os.path.join(folder, f"{base_name}{next_num}{ext}")

        self.last_result_df.T.to_csv(
            file_path,
            sep='\t',
            index=True,
            header=True,
            float_format='%.4f'
        )
        messagebox.showinfo("Saved", f"Result saved to file:\n{file_path}")

if __name__ == "__main__":
    app = ReactionApp()
    app.mainloop()
