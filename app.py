import csv
import os
import shutil
from collections import defaultdict

def copy_rename(csv_file, input_dir, output_dir, single_folder_dir, filename_template='%Last Name%_%First Name%.jpg'):
    photo_dict = {}
    processed_image_numbers = set()
    all_image_numbers = set()
    duplicates = defaultdict(list)  

    try:
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Image#']:
                    image_number = row['Image#']
                    all_image_numbers.add(image_number)
                    duplicates[image_number].append(row)  

                    photo_dict[image_number] = row
    except Exception as e:
        print(f"Error reading CSV file '{csv_file}': {e}")
        return "Processing failed."

    duplicate_image_numbers = [num for num, rows in duplicates.items() if len(rows) > 1]
    if duplicate_image_numbers:
        print(f"Duplicate image numbers found: {', '.join(duplicate_image_numbers)}")

    try:
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        
        if not os.path.isdir(single_folder_dir):
            os.makedirs(single_folder_dir)
    except Exception as e:
        print(f"Error creating output directories: {e}")
        return "Processing failed."

    imagenames = []
    try:
        for entry in os.scandir(input_dir):
            if entry.path.endswith(".jpg") and entry.is_file():
                imagenames.append(entry.name)
    except Exception as e:
        print(f"Error scanning input directory '{input_dir}': {e}")
        return "Processing failed."

    for img in imagenames:
        try:
            first_underscore = img.find('_')
            if first_underscore == -1 or img.find('.') == -1:
                raise ValueError("Filename must contain at least one underscore and one period")
            
            start_index = first_underscore + 1
            end_index = img.find('.')
            num_segment = img[start_index:end_index].strip()  
            
            if num_segment in photo_dict:
                person = photo_dict[num_segment]
                
                old_filepath = os.path.join(input_dir, img)

                temp_filename = []
                for i in filename_template.split('%'):
                    if i in person.keys():
                        temp_filename.append(person[i])
                    else:
                        temp_filename.append(i)
                new_filename = ''.join(temp_filename)

                grade_folder_name = f"grade_{person['Grade']}"
                if person['Grade'] == 'Faculty':
                    grade_folder_name = 'Faculty'
                
                grade_folder_dir = os.path.join(output_dir, grade_folder_name)
                teacher_folder_name = person['Teacher'].replace(", " , "_")
                teacher_folder_dir = os.path.join(grade_folder_dir, teacher_folder_name)
                
                if not os.path.isdir(grade_folder_dir):
                    os.makedirs(grade_folder_dir)
                
                if not os.path.isdir(teacher_folder_dir):
                    os.makedirs(teacher_folder_dir)
               
                if person['Grade'] == 'Faculty':
                    new_filepath_nested = os.path.join(output_dir, 'Faculty', new_filename)
                else:
                    new_filepath_nested = os.path.join(output_dir, grade_folder_name, teacher_folder_name, new_filename)

                shutil.copy(old_filepath, new_filepath_nested)
                
                
                new_filepath_single = os.path.join(single_folder_dir, new_filename)
                shutil.copy(old_filepath, new_filepath_single)
                
                processed_image_numbers.add(num_segment)
            else:
                print(f"Segment '{num_segment}' not found in dictionary keys.")
        
        except Exception as e:
            print(f"Error processing file '{img}': {e}")

    missing_image_numbers = all_image_numbers - processed_image_numbers
    if missing_image_numbers:
        print(f"Missing image numbers from CSV: {', '.join(missing_image_numbers)}")
        return "Processing failed."

    return "Processing complete."


try:
    result = copy_rename(
        'test_photos.csv',
        input_dir='./images',
        output_dir='./output',
        single_folder_dir='./single_folder',
        filename_template='%Last Name%_%First Name%.jpg'
    )
    print(result)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
