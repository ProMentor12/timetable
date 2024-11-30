import re

# Function to parse the timetable data from a text file
def parse_teacher_timetable_from_file(filename):
    with open(filename, 'r') as file:
        teacher_data = file.read()

    timetable_data = []
    
    # Split the data based on each teacher's information (assuming each teacher's data is separated by a blank line)
    teacher_blocks = teacher_data.strip().split("\n\n")

    for teacher_block in teacher_blocks:
        teacher_lines = teacher_block.splitlines()
        
        # Extract the teacher's name and code from the first two lines
        teacher_name = teacher_lines[0].split(":")[1].strip()
        teacher_code = teacher_lines[1].strip()

        # Regular expression to match periods and class assignments, ignoring content inside parentheses
        periods = re.findall(r"Period (\d+): (.*?)\n", teacher_block)
        
        timetable = {}
        for period, class_info in periods:
            class_info = class_info.strip()
            
            # Remove content inside parentheses using regular expression
            class_info = re.sub(r"\(.*?\)", "", class_info).strip()
            
            # Now split the class information into class name and days (if applicable)
            match = re.match(r"([A-Z0-9 ]+)(.*?)$", class_info)
            if match:
                class_name = match.group(1).strip()
                days_and_notes = match.group(2).strip() if match.group(2) else None
                timetable[period] = {
                    "class_name": class_name,
                    "days_and_notes": days_and_notes
                }

        timetable_data.append({
            "name": teacher_name,
            "code": teacher_code,
            "timetable": timetable
        })
    
    return timetable_data

# Example usage: Load timetable data from "data.txt" and print it
filename = "data.txt"  # The file containing the teacher timetable data

# Parse the timetable data from the file
teacher_data = parse_teacher_timetable_from_file(filename)

# Print the parsed timetables for each teacher
for teacher in teacher_data:
    print(f"Timetable for {teacher['name']} ({teacher['code']}):")
    for period, info in teacher['timetable'].items():
        print(f"  Period {period}: {info['class_name']} ({info['days_and_notes']})")
    print("\n")
