import re
import random
import tkinter as tk
from tkinter import messagebox

def parse_timetable(file_path):
    """Parse the timetable from a text file."""
    timetables = {}
    current_teacher = None
    current_timetable = {}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Check if the line starts with "Teacher: " to identify a new teacher
            teacher_match = re.match(r"Teacher:\s*(.+)", line)
            if teacher_match:
                # Save the current teacher's timetable before starting a new one
                if current_teacher:
                    timetables[current_teacher] = current_timetable
                
                # Initialize new teacher's timetable
                current_teacher = teacher_match.group(1)
                current_timetable = {}
                continue
            
            # Check if the line specifies a period
            period_match = re.match(r"Period\s*(\d+):\s*(.+)", line)
            if period_match:
                period = int(period_match.group(1))
                subject = period_match.group(2)
                current_timetable[period] = subject

        # Add the last teacher's timetable
        if current_teacher:
            timetables[current_teacher] = current_timetable

    return timetables

def adjust_schedule(timetables, absent_teachers):
    """Adjust the schedule by reassigning periods of the absent teachers."""
    adjustments = {}
    
    # List of all available teachers (excluding the ones that are absent)
    available_teachers = [t for t in timetables if t not in absent_teachers]

    # Adjust each period for the absent teachers
    for absent_teacher in absent_teachers:
        absent_schedule = timetables[absent_teacher]
        for period, subject in absent_schedule.items():
            if subject == "Free Period":
                continue  # Skip free periods

            # Shuffle the available teachers to ensure randomness
            random.shuffle(available_teachers)

            # Try to find a replacement teacher
            replacement_found = False
            for teacher in available_teachers:
                if timetables[teacher].get(period, "Free Period") == "Free Period":
                    adjustments.setdefault(absent_teacher, {})[period] = f"Replaced with {teacher} for {subject}"
                    timetables[teacher][period] = f"Covering for {absent_teacher}"  # Mark the replacement teacher
                    replacement_found = True
                    break

            if not replacement_found:
                adjustments.setdefault(absent_teacher, {})[period] = "No replacement available"

    return adjustments

def on_submit(timetables, checkboxes):
    """Handle the submit button click."""
    # Get the list of selected absent teachers
    absent_teachers = [teacher for teacher, var in checkboxes.items() if var.get() == 1]

    if not absent_teachers:
        messagebox.showerror("Error", "Please select at least one teacher as absent.")
        return
    
    # Adjust the timetable for the selected teachers
    adjustments = adjust_schedule(timetables, absent_teachers)
    
    # Show the adjustments in a messagebox
    adjustment_messages = []
    for teacher, periods in adjustments.items():
        adjustment_messages.append(f"Adjustments for {teacher}:")
        for period, info in periods.items():
            adjustment_messages.append(f"  Period {period}: {info}")
    
    messagebox.showinfo("Adjustments", "\n".join(adjustment_messages))

def main():
    # File containing the timetable
    file_path = "data.txt"

    # Parse the file to get the timetable data
    timetables = parse_timetable(file_path)

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Teacher Absence Adjustment")

    # Create a canvas and a scrollbar for the scrolling interface
    canvas = tk.Canvas(root)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame to hold the checkboxes inside the canvas
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    checkboxes = {}

    # Display available teachers and their subjects with checkboxes
    for teacher, schedule in timetables.items():
        subjects = ', '.join(schedule.values())  # List the subjects
        label = tk.Label(frame, text=f"{teacher} (Subjects: {subjects})")
        label.pack(anchor="w")

        var = tk.IntVar()
        checkbox = tk.Checkbutton(frame, text="Absent", variable=var)
        checkbox.pack(anchor="w")
        checkboxes[teacher] = var

    # Update the scrolling region
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Create a submit button
    submit_button = tk.Button(root, text="Submit", command=lambda: on_submit(timetables, checkboxes))
    submit_button.pack(pady=20)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
