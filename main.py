import openpyxl
import re

# Function to clean the data (remove parentheses, irrelevant entries, and trailing numbers)
def clean_timetable_entry(entry):
    if entry is None or str(entry).strip() == '':
        return None  # Ignore null or empty entries
    
    # Remove anything inside parentheses, including the parentheses themselves
    cleaned_entry = re.sub(r'.*?', '', str(entry)).strip()
    
    # Remove any trailing numbers that might appear at the end of the entry
    cleaned_entry = re.sub(r'\s*\d+$', '', cleaned_entry).strip()
    
    # Ignore irrelevant data like "M.SC", "FRUIT BREAK", "RECESS" or any other non-relevant entries
    irrelevant_entries = ['M.SC', 'FRUIT BREAK', 'RECESS', 'Lunch Break', 'Free Period', 'Recess']
    for entry_word in irrelevant_entries:
        if entry_word in cleaned_entry:
            return None
    
    # If it's just a free period or any other specific word, treat it as 'Free Period'
    if cleaned_entry == '-':
        return 'Free Period'
    
    return cleaned_entry if cleaned_entry else None

# Mapping of numbers to days of the week
day_mapping = {
    '1': 'Monday',
    '2': 'Tuesday',
    '3': 'Wednesday',
    '4': 'Thursday',
    '5': 'Friday',
    '6': 'Saturday'
}

# Function to replace numbers with actual days
def replace_numbers_with_days(entry):
    for number, day in day_mapping.items():
        entry = entry.replace(number, day)
    return entry

# Load the Excel file
try:
    workbook = openpyxl.load_workbook('file.xlsx')
    sheet = workbook.active
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# Flag to indicate when we are in the teacher-wise section
teacher_wise_section = False
current_teacher = None

# Open data.txt file in write mode
with open('data.txt', 'w') as file:
    # Iterate through rows and columns
    for row in sheet.iter_rows(values_only=True):
        # Look for department names or headers
        if row[0] and 'DEPT.' in str(row[0]):
            # Mark the beginning of a department section
            teacher_wise_section = True
        elif row[0] and ('SR. NO.' in str(row[0])):  # Stop when you hit a row that indicates the teacher table section
            teacher_wise_section = False

        # If we're in a teacher-wise section, extract teacher names and their timetables
        if teacher_wise_section:
            # The teacher's name is assumed to be in the second column (index 1)
            teacher_name = row[1]
            if teacher_name:  # Check if the name exists (some rows might be empty)
                if current_teacher != teacher_name:
                    # Write the timetable for the previous teacher (if any) and update the current teacher
                    if current_teacher:
                        file.write(f"\nTimetable for {current_teacher}:\n")
                    current_teacher = teacher_name
                    file.write(f"\nTeacher: {teacher_name}\n")

                # Assuming that columns 2 onwards contain the timetable data
                timetable = row[2:]  # Adjust this based on your actual Excel layout

                # Process and clean timetable data
                cleaned_timetable = []
                for entry in timetable:
                    cleaned_entry = clean_timetable_entry(entry)
                    if cleaned_entry:
                        # Replace day numbers with actual days of the week
                        cleaned_entry = replace_numbers_with_days(cleaned_entry)
                        cleaned_timetable.append(cleaned_entry)

                # Write the cleaned timetable with "Period" labels
                if cleaned_timetable:
                    for period_num, entry in enumerate(cleaned_timetable, start=1):
                        file.write(f"Period {period_num}: {entry}\n")

print("Timetable has been saved to data.txt.")
