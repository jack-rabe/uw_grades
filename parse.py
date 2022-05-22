from PyPDF2 import PdfFileReader

def parse_grades(number_str):
    result = {}
    grades = ['a', 'ab', 'b', 'bc', 'c', 'd', 'f']
    num = ''
    percents = []
    end = False # set when a period is reached

    for char in number_str:
        num += char
        if char == '.':
            end = True
        elif end:
            percents.append(num)
            num = ''
            end = False

    for i in range(7):
        result[grades[i]] =  percents[i]
    return result

pdf_reader = PdfFileReader('2022-grade-dist.pdf')
page = pdf_reader.pages[0]

filename = 'output.txt'
data = {}
with open(filename, 'w+') as f:
    print(page.extract_text(), file=f)

with open(filename, 'r') as f:
    content = f.readlines()
    for idx, line, in enumerate(content):
        content[idx] = line.strip()
    data['term'] = content[0]
    data['school'] = content[8]
    data['department'] = content[10]

    current_block = 'SECTION'
    grades_str = ''
    courses = []
    course_data = {}
    for i in range(17, len(content)):
        # parse the section number and gpa for a new class
        if current_block == 'SECTION':
            section_str = content[i]
            course_data['section_number'] = section_str[0:3]
            gpa = section_str[-6:-1]
            course_data['average_gpa'] = gpa if '*' not in gpa else 'NA'
            current_block = 'GRADES'
                
        # next, find the grade distributions NOTE: this may span multiple lines
        elif current_block == 'GRADES':
            # skip grade data collection if too few students took the class
            if course_data['average_gpa'] == 'NA':
                print('no grade data')
                course_data['grades'] = [0 for i in range(7)]
                current_block = 'COURSE_NUMBER'
                continue
            # aggregate data if spread across multiple lines
            grades_str += content[i]
            if grades_str.count('.') == 16:
                course_data['grades'] = parse_grades(grades_str)
                current_block = 'COURSE_NUMBER'
        # next, extract course number
        elif current_block == 'COURSE_NUMBER':
            course_data['course_number'] = int(content[i])
            current_block = 'NAME'
        # finally, extract course name
        elif current_block == 'NAME':
            course_data['name'] = content[i]
            grades_str = ''
            current_block = 'SECTION'
            courses.append(course_data)
            course_data = {}
            print('collection done')
        data['courses'] = courses

print(data)
