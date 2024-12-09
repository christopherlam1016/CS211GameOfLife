import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

class GameOfLifeGUI:
    def __init__(self, root):
        # Initialize the GUI
        self.root = root
        self.root.title("Game of Life - Made by Christopher Lam (cl1515)")
        self.root.geometry("800x600")
        self.root.focus_force()
        self.root.resizable(False, False)

        # Center the window on the screen (doesn't adjust to smaller screens)
        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        self.grid_size_label = tk.Label(self.root, text="Game Parameters:",font=("Helvetica",30))
        self.grid_size_label.pack()

        # Frame for row and column inputs
        input_frame = tk.Frame(self.root)
        input_frame.pack()

        # Get user parameters for rows
        self.rows_label = tk.Label(input_frame, text="Rows:")
        self.rows_label.grid(row=0, column=0)
        self.rows_entry = tk.Entry(input_frame)
        self.rows_entry.insert(0, "(default is 8)")
        self.rows_entry.grid(row=0, column=1)

        # Get user parameters for columns
        self.columns_label = tk.Label(input_frame, text="Columns:")
        self.columns_label.grid(row=1, column=0)
        self.columns_entry = tk.Entry(input_frame)
        self.columns_entry.insert(0, "(default is 8)")
        self.columns_entry.grid(row=1, column=1)

        # Slider for initial probability of a cell being alive
        self.probability_label = tk.Label(input_frame, text="Initial Probability of a Cell Being Alive:")
        self.probability_label.grid(row=0, column=3, columnspan=2,padx=(30,0))
        self.probability_slider = tk.Scale(input_frame, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01)
        self.probability_slider.set(0.3)
        self.probability_slider.grid(row=1, column=3, rowspan=2, columnspan=2, sticky='ns',padx=(30,0))

        # Get user parameters for seed
        self.seed_label = tk.Label(input_frame, text="Seed:")
        self.seed_label.grid(row=2, column=0)
        self.seed_entry = tk.Entry(input_frame)
        self.seed_entry.insert(0, "(default is 211)")
        self.seed_entry.grid(row=2, column=1)

        # Get user parameters for iteration count
        self.iteration_label = tk.Label(input_frame, text="Iteration Count:")
        self.iteration_label.grid(row=3, column=0)
        self.iteration_entry = tk.Entry(input_frame)
        self.iteration_entry.insert(0, "(default is 10)")
        self.iteration_entry.grid(row=3, column=1)

        # FOR TASK 2, CUSTOM RULESET
        self.file_label = tk.Label(self.root, text="Optional: Select a JSON file for custom ruleset")
        self.file_label.pack()
        self.file_button = tk.Button(self.root, text="Browse", command=self.browse_file)
        self.file_button.pack()
        self.file_path = tk.StringVar()
        self.file_entry = tk.Entry(self.root, textvariable=self.file_path, state='readonly')
        self.file_entry.pack()

        self.start_button = tk.Button(self.root, text="Start",pady=(10),padx=(10),command=self.start_simulation)
        self.start_button.pack()

        # Frame for the Matplotlib plot
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

        # Flag to control the running state of the simulation
        self.running = False
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")],initialdir=".")
        if file_path:
            self.file_path.set(file_path)

    def start_simulation(self):
            # Get the user parameters before clearing the widgets
            rows = int(self.rows_entry.get()) if self.rows_entry.get() != "(default is 8)" else 8
            columns = int(self.columns_entry.get()) if self.columns_entry.get() != "(default is 8)" else 8
            seed = int(self.seed_entry.get()) if self.seed_entry.get() != "(default is 211)" else 211
            probability = self.probability_slider.get()
            iterations = int(self.iteration_entry.get()) if self.iteration_entry.get() != "(default is 10)" else 10
            file_path = self.file_path.get()

            np.random.seed(seed)

            # Clear the root frame
            for widget in self.root.winfo_children():
                widget.destroy()

            # Check if the user parameters are valid
            if rows <= 0 or columns <= 0:
                messagebox.showerror("Error", "Rows and columns must be greater than 0.")
                return
            if probability < 0 or probability > 1:
                messagebox.showerror("Error", "Probability must be between 0 and 1.")
                return

            # Initialize the game & attributes
            self.life_state = init_life_state_1(rows, columns, probability)
            self.original_life_state = self.life_state.copy()
            self.iterations = iterations
            self.current_iteration = 0

            # Add iteration counter
            self.iteration_counter_label = tk.Label(self.root, text=f"Iteration: {self.current_iteration}", font=("Helvetica", 16))
            self.iteration_counter_label.pack()

            fig, ax = plt.subplots()
            ax.axis('on')
            ax.set_title("Game of Life on a {0}x{1} Grid & {2}% probability".format(rows, columns, probability*100))
            self.im = ax.imshow(self.life_state, cmap='binary')

            # Add gridlines
            ax.set_xticks(np.arange(-0.5, columns, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
            ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
            ax.tick_params(which='minor', size=0)

            # Embed the plot in the Tkinter GUI
            self.canvas = FigureCanvasTkAgg(fig, master=self.root)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Frame for the simulation buttons
            button_frame = tk.Frame(self.root)
            button_frame.pack()

            # Add a button to update the plot with the next iteration
            self.next_button = tk.Button(button_frame, text="Next Iteration", command=self.next_iteration)
            self.next_button.grid(row=0, column=0)

            # Add a button to run through all iterations
            self.run_button = tk.Button(button_frame, text="Run All Iterations", command=self.run_all_iterations)
            self.run_button.grid(row=1, column=0)

            # Add a button to stop the simulation
            self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_simulation)
            self.stop_button.grid(row=0, column=1)

            # Add a button to restart the simulation
            self.restart_button = tk.Button(button_frame, text="Restart", command=self.restart_simulation)
            self.restart_button.grid(row=1, column=1)

    def next_iteration(self):
        self.life_state = update_life_state_1(self.life_state)
        self.im.set_array(self.life_state)
        self.current_iteration += 1
        self.canvas.draw()
        self.iteration_counter_label.config(text=f"Iteration: {self.current_iteration}")

    def run_all_iterations(self):
        self.running = True
        for _ in range(self.iterations):
            if not self.running or not np.any(self.life_state): # if the simulation is stopped or all cells are dead,
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

#=================================================================================================== USER FUNCTIONS ===================================================================================================#

def init_life_state_1(n, m, p):
    """
    Generate an initial random subset of life cells (2D points)
    IN: n, int, number of rows
        m, int, number of columns
        p, float, probability of a cell being alive
    OUT: ndarray of shape (n, m), initial state of the cells
    """

    # generate random numbers
    rand = np.random.rand(n, m)

    # create a boolean array
    state = rand < p
    return state

def draw_life_state_1(life_state):
    """
    Display the 2D positions of the selected collection of cells (2D points)
    IN: life_state, ndarray of shape (n, m), initial state of the cells
    OUT: None
    """

    # display the state
    plt.imshow(life_state, cmap='binary')
    plt.show()

def update_life_state_1(life_state, out_life_state=None):
    """
    For each cell evaluate the update rules specified above to obtain its new state
    IN: life_state, ndarray of shape (n, m), initial state of the cells
        out_life_state, ndarray of shape (n, m), for storing the next state of the cells, if None, create a new array
    OUT: ndarray of shape (n, m), next state of the cells
    """
    
    # get the shape of the array
    n, m = life_state.shape

    # create a new array if necessary
    if out_life_state is None:
        out_life_state = np.zeros((n, m), dtype=bool)

    # iterate over all cells
    for i in range(n):
        for j in range(m):

            # get the number of alive neighbors
            row_start = max(i - 1, 0)
            row_end = min(i + 2, n)
            col_start = max(j - 1, 0)
            col_end = min(j + 2, m)

            neighborhood_sum = np.sum(life_state[row_start:row_end, col_start:col_end])
            alive_neighbors = neighborhood_sum - life_state[i, j]

            # apply the rules
            if life_state[i, j] == 1: # if the cell is alive
                if alive_neighbors != 2 or alive_neighbors != 3: # if the cell has less than 2 or more than 3 neighbors (exclusive)
                    out_life_state[i, j] = 0 # kill the cell
            else: # if the cell is dead
                if alive_neighbors == 3: # if the cell has exactly 3 neighbors 
                    out_life_state[i, j] = 1 # revive the cell

    return out_life_state

if __name__ == "__main__":
    root = tk.Tk()
    game = GameOfLifeGUI(root)
    root.mainloop()