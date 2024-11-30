
import csv
from collections import defaultdict
import shutil
from tabulate import tabulate




original_filename = "teachersdaTA.txt"  # Change this to the filename you used to save teacher data
temp_filename = "temp.txt"  # Temporary file to store teacher data and substitutions

def read_teacher_data(filename):
    teachers = []
    try:
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse subjects and classes into lists
                row['subjects'] = row['subjects'].split(', ')
                row['classes'] = row['classes'].split(', ')
                # Parse class schedule for Monday
                class_schedule = {"Monday": {}}
                for period_class in row["Monday"].split(", "):
                    period, class_assigned = period_class.split(":")
                    class_schedule["Monday"][period.strip()] = class_assigned.strip()
                row['class_schedule'] = class_schedule
                del row['Monday']
                teachers.append(row)
    except FileNotFoundError:
        print(f"The file '{filename}' does not exist.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return teachers

def mark_teachers_absent(absent_teacher_names, teacher_data):
    for teacher_name in absent_teacher_names:
        for teacher in teacher_data:
            if teacher['name'].lower() == teacher_name.lower():
                teacher['absent'] = True
                break

def find_substitute(period, class_name, teacher_data, excluded_teachers, assigned_periods):
    substitute_teacher = None
    for teacher in teacher_data:
        if 'absent' not in teacher and class_name in teacher['classes'] and teacher not in excluded_teachers:
            if period not in teacher['class_schedule']['Monday'] and period not in assigned_periods.get(teacher['name'], {}).values():
                if all(period not in periods.values() for periods in teacher['class_schedule'].values()):
                    if all(period not in periods.values() for periods in assigned_periods.values()):
                        # Update available teachers
                        if teacher['name'] not in assigned_periods:
                            assigned_periods[teacher['name']] = {}
                        assigned_periods[teacher['name']][period] = class_name
                        excluded_teachers.append(teacher)
                        substitute_teacher = teacher
                        break
    if substitute_teacher:
        return substitute_teacher
    else:
        print(f"No substitute available for {class_name} during period {period}.")
        return None

def write_substitutions_to_file(filename, substitutions):
    with open(filename, "a") as file:
        for substitution in substitutions:
            file.write(str(substitution) + "\n")


def clear_temp_file(filename):
    open(filename, "w").close()

from tabulate import tabulate

def main():
    shutil.copyfile(original_filename, temp_filename)
    teachers_data = read_teacher_data(temp_filename)
    
    if teachers_data:
        absent_teacher_names = input("Enter the names of the absent teachers separated by commas: ").split(",")
        absent_teacher_names = [name.strip() for name in absent_teacher_names]
        
        mark_teachers_absent(absent_teacher_names, teachers_data)
        
        substitutions = []  # List to store substitutions
        
        print("Substitute teachers assigned:")
        substitute_table = []  # List to store rows for the table
        for teacher_name in absent_teacher_names:
            absent_teacher = next((teacher for teacher in teachers_data if teacher['name'].lower() == teacher_name.lower()), None)
            if absent_teacher:
                print(f"\n{teacher_name} marked as absent.")
                excluded_teachers = [absent_teacher]
                assigned_periods = defaultdict(dict)
                for day, schedule in absent_teacher['class_schedule'].items():
                    for period, class_name in schedule.items():
                        substitute_teacher = find_substitute(period, class_name, teachers_data, excluded_teachers, assigned_periods)
                        if substitute_teacher:
                            substitution = [substitute_teacher['name'], class_name, period]
                            substitute_table.append(substitution)
                            substitutions.append(substitution)
                            if substitute_teacher['name'] not in assigned_periods:
                                assigned_periods[substitute_teacher['name']] = {}
                            assigned_periods[substitute_teacher['name']][period] = class_name
                            # Update temp file with new assignment for substitute teacher
                            with open(temp_filename, "r") as file:
                                lines = file.readlines()
                            with open(temp_filename, "w") as file:
                                for line in lines:
                                    if substitute_teacher['name'] in line:
                                        line = line.strip() + f", {class_name}: {day} {period}\n"
                                    file.write(line)
                            # Update the timetable of the substitute teacher in the teacher data
                            for t in teachers_data:
                                if t['name'] == substitute_teacher['name']:
                                    if day not in t['class_schedule']:
                                        t['class_schedule'][day] = {}
                                    t['class_schedule'][day][period] = class_name
                            # Clear excluded teachers list for next substitution
                            excluded_teachers = [absent_teacher]

        # Print the substitution table
        headers = ["Substitute Teacher", "Class Name", "Period"]
        print(tabulate(substitute_table, headers=headers, tablefmt="grid"))

        
        # Write substitutions to temp file
        write_substitutions_to_file(temp_filename, substitutions)
        
        # Clear temp file for next run
        clear_temp_file(temp_filename)
    else:
        print("No teacher data found.")

if __name__ == "__main__":
    main()
