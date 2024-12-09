import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import csv

class GameOfLifeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game of Life - Made by Christopher Lam (cl1515)")
        self.root.geometry("800x600")
        self.root.focus_force()
        self.root.resizable(False, False)

        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        self.create_initial_widgets()

    def create_initial_widgets(self):
        self.quit_button_frame = tk.Frame(self.root)
        self.quit_button_frame.pack(side=tk.TOP, anchor=tk.NE)
        self.quit_button = tk.Button(self.quit_button_frame, text="Quit", command=self.root.quit)
        self.quit_button.pack()

        self.grid_size_label = tk.Label(self.root, text="Game Parameters:", font=("Helvetica", 30))
        self.grid_size_label.pack()

        input_frame = tk.Frame(self.root)
        input_frame.pack()

        self.rows_label = tk.Label(input_frame, text="Rows:")
        self.rows_label.grid(row=0, column=0)
        self.rows_entry = tk.Entry(input_frame)
        self.rows_entry.insert(0, "(default is 8)")
        self.rows_entry.grid(row=0, column=1)

        self.columns_label = tk.Label(input_frame, text="Columns:")
        self.columns_label.grid(row=1, column=0)
        self.columns_entry = tk.Entry(input_frame)
        self.columns_entry.insert(0, "(default is 8)")
        self.columns_entry.grid(row=1, column=1)

        self.probability_label = tk.Label(input_frame, text="Initial Probability of a Cell Being Alive:")
        self.probability_label.grid(row=0, column=3, columnspan=2, padx=(30, 0))
        self.probability_slider = tk.Scale(input_frame, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01)
        self.probability_slider.set(0.3)
        self.probability_slider.grid(row=1, column=3, rowspan=2, columnspan=2, sticky='ns', padx=(30, 0))

        self.seed_label = tk.Label(input_frame, text="Seed:")
        self.seed_label.grid(row=2, column=0)
        self.seed_entry = tk.Entry(input_frame)
        self.seed_entry.insert(0, "(default is 211)")
        self.seed_entry.grid(row=2, column=1)

        self.iteration_label = tk.Label(input_frame, text="Iteration Count:")
        self.iteration_label.grid(row=3, column=0)
        self.iteration_entry = tk.Entry(input_frame)
        self.iteration_entry.insert(0, "(default is 10)")
        self.iteration_entry.grid(row=3, column=1)

        self.file_label = tk.Label(self.root, text="Optional: Select a JSON file for custom ruleset")
        self.file_label.pack()
        self.file_button = tk.Button(self.root, text="Browse", command=self.browse_file)
        self.file_button.pack()
        self.file_path = tk.StringVar()
        self.file_entry = tk.Entry(self.root, textvariable=self.file_path, state='readonly')
        self.file_entry.pack()

        self.csv_label = tk.Label(self.root, text="Optional: Select a CSV file for custom grid")
        self.csv_label.pack()
        self.csv_button = tk.Button(self.root, text="Browse CSV", command=self.browse_csv)
        self.csv_button.pack()
        self.csv_path = tk.StringVar()
        self.csv_entry = tk.Entry(self.root, textvariable=self.csv_path, state='readonly')
        self.csv_entry.pack()

        self.start_button = tk.Button(self.root, text="Start", pady=(10), padx=(10), command=self.start_simulation)
        self.start_button.pack()

        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

        self.running = False

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], initialdir=".")
        if file_path:
            self.file_path.set(file_path)

    def browse_csv(self):
        csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], initialdir=".")
        if csv_path:
            self.csv_path.set(csv_path)
            self.load_csv_grid(csv_path)

    def load_csv_grid(self, csv_path):
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            grid = np.array([list(map(int, row)) for row in reader])
            rows, columns = grid.shape
            self.rows_entry.delete(0, tk.END)
            self.rows_entry.insert(0, str(rows))
            self.columns_entry.delete(0, tk.END)
            self.columns_entry.insert(0, str(columns))
            self.custom_grid = grid

    def start_simulation(self):
        if self.csv_path.get():
            self.life_state = self.custom_grid
            rows, columns = self.life_state.shape
        else:
            rows = int(self.rows_entry.get()) if self.rows_entry.get() != "(default is 8)" else 8
            columns = int(self.columns_entry.get()) if self.columns_entry.get() != "(default is 8)" else 8
            seed = int(self.seed_entry.get()) if self.seed_entry.get() != "(default is 211)" else 211
            probability = self.probability_slider.get()
            np.random.seed(seed)
            self.life_state = init_life_state_1(rows, columns, probability)

        iterations = int(self.iteration_entry.get()) if self.iteration_entry.get() != "(default is 10)" else 10
        file_path = self.file_path.get()

        for widget in self.root.winfo_children():
            widget.destroy()

        if rows <= 0 or columns <= 0:
            messagebox.showerror("Error", "Rows and columns must be greater than 0.")
            return
        if not self.csv_path.get() and (probability < 0 or probability > 1):
            messagebox.showerror("Error", "Probability must be between 0 and 1.")
            return

        self.original_life_state = self.life_state.copy()
        self.iterations = iterations
        self.current_iteration = 0

        self.iteration_counter_label = tk.Label(self.root, text=f"Iteration: {self.current_iteration}", font=("Helvetica", 16))
        self.iteration_counter_label.pack()

        fig, ax = plt.subplots()
        ax.axis('on')
        ax.set_title("Game of Life on a {0}x{1} Grid".format(rows, columns))
        self.im = ax.imshow(self.life_state, cmap='binary')

        ax.set_xticks(np.arange(-0.5, columns, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
        ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
        ax.tick_params(which='minor', size=0)

        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self.root)
        button_frame.pack()

        self.next_button = tk.Button(button_frame, text="Next Iteration", command=self.next_iteration)
        self.next_button.grid(row=0, column=0)

        self.run_button = tk.Button(button_frame, text="Run {self.iterations} Iterations", command=self.run_all_iterations)
        self.run_button.grid(row=1, column=0)

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_simulation)
        self.stop_button.grid(row=0, column=1)

        self.restart_button = tk.Button(button_frame, text="Restart", command=self.restart_simulation)
        self.restart_button.grid(row=1, column=1)

        self.back_button = tk.Button(button_frame, text="Back", command=self.reset_to_initial)
        self.back_button.grid(row=2, column=0, columnspan=2)

    def next_iteration(self):
        self.life_state = update_life_state_1(self.life_state)
        self.im.set_array(self.life_state)
        self.current_iteration += 1
        self.canvas.draw()
        self.iteration_counter_label.config(text=f"Iteration: {self.current_iteration}")

    def run_all_iterations(self):
        self.running = True
        for _ in range(self.iterations):
            if not self.running or not np.any(self.life_state):
                break
            self.next_iteration()
            self.root.update()
            self.root.after(500)

    def stop_simulation(self):
        self.running = False

    def restart_simulation(self):
        self.life_state = self.original_life_state.copy()
        self.current_iteration = 0
        self.im.set_array(self.life_state)
        self.canvas.draw()
        self.iteration_counter_label.config(text=f"Iteration: {self.current_iteration}")

    def reset_to_initial(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_initial_widgets()

def init_life_state_1(n, m, p):
    rand = np.random.rand(n, m)
    state = rand < p
    return state

def draw_life_state_1(life_state):
    plt.imshow(life_state, cmap='binary')
    plt.show()

def update_life_state_1(life_state, out_life_state=None):
    n, m = life_state.shape
    if out_life_state is None:
        out_life_state = np.zeros((n, m), dtype=bool)

    for i in range(n):
        for j in range(m):
            row_start = max(i - 1, 0)
            row_end = min(i + 2, n)
            col_start = max(j - 1, 0)
            col_end = min(j + 2, m)

            neighborhood_sum = np.sum(life_state[row_start:row_end, col_start:col_end])
            alive_neighbors = neighborhood_sum - life_state[i, j]

            if life_state[i, j] == 1:
                if alive_neighbors < 2  or alive_neighbors > 3:
                    out_life_state[i, j] = 0
                else:
                    out_life_state[i, j] = 1
            else:
                if alive_neighbors == 3:
                    out_life_state[i, j] = 1
                else:
                    out_life_state[i, j] = 0

    return out_life_state

if __name__ == "__main__":
    root = tk.Tk()
    game = GameOfLifeGUI(root)
    root.mainloop()
