#!/bin/python3

# The above #!/bin/python is a UNIX Shebang telling all *nix systems what type of interpreter to use
# when parsing this file. For more information please see
# https://en.wikipedia.org/wiki/Shebang_%28Unix%29
#
# Contributors: Tyler Renken tyler.renken@colorado.edu
# Intended Course: ASEN 3801
# File name: matlab_linter
# Created: 1/17/24

"""

To use this software, in a terminal type python (or python3 on Linux) path/to/the/matlab_linter.py
/different/path/to/your/matlab.m and issues and recommendations with your MATLAB code will be
printed in the terminal window. The program will run until either it finds an issue in your header
file, or it finds issues with a function header. Both of these are critical issues that should be
addressed before the homework file is submitted as homework, and the intention is to bring the
user's intention to the problem immediately, rather than finding all problems throughout the file.
Less critical issues, like non-conformance to the recommended naming schemes (a check which can be
disabled entirely) will then be listed after all critical problems have been resolved by the user.
It is the intention that in the development of a MATLAB file the linter will be run multiple times
on the same file as it is edited (and as the user fixes problems revealed by the linter).

For information on how to run the program, running this script with the -h option will open a help
window. A pyinstaller binary containing a self-contained python execution environment so that
Windows users without a python installation can run this program is also available.

This software uses the DBAD license, from the website https://dbad-license.org/, and is also
listed below:

===================================================================================================
# DON'T BE A DICK PUBLIC LICENSE

> Version 1.1, December 2016

> Copyright (C) 2024 Tyler Renken

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document.

> DON'T BE A DICK PUBLIC LICENSE
> TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

1. Do whatever you like with the original work, just don't be a dick.

   Being a dick includes - but is not limited to - the following instances:

 1a. Outright copyright infringement - Don't just copy this and change the name.
 1b. Selling the unmodified original with no work done what-so-ever, that's REALLY being a dick.
 1c. Modifying the original work to contain hidden harmful content. That would make you a PROPER
     dick.

2. If you become rich through modifications, related works/services, or supporting the original
work, share the love. Only a dick would make loads off this work and not buy the original work's
creator(s) a pint.

3. Code is provided with no warranty. Using somebody else's code and bitching when it goes wrong
makes you a DONKEY dick. Fix the problem yourself. A non-dick would submit the fix back.

===================================================================================================

The purpose of this program is to check that the matlab files conform to the header
specifications for the labs in ASEN 3801. All it does is report where the code does not conform. 
It does not edit the target MATLAB file. The specification is as follows. Check to make sure that
your class's specification matches the specification listed below, taken from ASEN3801 Lab 1:

'All M-files developed for this course should have the same header information. The header should
have the students' names, the course name and number, the file name, and the date the file was
created:

% Contributors: <Names go here>
% Course number: ASEN 3801
% File name: <Name_of_the_file_without_the_extension_goes_here>
% Created: 12/31/99

Every software function will have a "docstring" that describes the inputs to the function, the
outputs, and a basic description of the technical approach.

function return_val = NameOfFunction(arguments)
%
% Inputs:   argument1 = description of argument1
%           argument2 = description of argument2
%
% Outputs:  return_val = [different variables in a matrix]
%           different = description of this variable
%           variables =              ''
%           in =                     ''
%           a =                      ''
%           matrix =                 ''
%
% Methodology: Describe how the function works here

Additionally, the lab suggests that variables be written in snake_case and that function names
are written in CapitalCamelCase. While this will be inforced by this linter by default, it can
be turned off with a command line argument, as this is merely a recommendation by the professors,
and not a requirement.

This program is called a 'linter' in the C.S. industry. Linters are programs designed to judge code
purely on it's syntax and neatness, and many companies will not let code into a codebase that
doesn't have the linter's approval. This program itself is linted with pylint.

This program, in addition to displaying text, has the following error codes:
0 - Everything's fine, the MATLAB code is ready to submit
1 - The specified file cannot be read
2 - Something is wrong with the file header
3 - Something is wrong with a function docstring
4 - Something is wrong with the variable and/or function names (if this is enabled, which it is by
    default)
"""

import argparse
import os
import sys

# Helper Functions
def readnn(f):
    """ read no newline: Read a line without its newline """
    #
    # Inputs:   f = a file returned from open()
    #
    # Outputs:  The next line read from f, with the newline removed
    #
    # Methodology: This program simply calls readline() which obtains the current line and advances
    # the file pointer to the next line, and then removes the newline from the stored line before
    # returning to the caller.
    return f.readline().replace('\n', '')

def check_date(line):
    """ verify that the date in the header is of the form MM/DD/YY """
    #
    # Inputs:   line = the string containing the date (with the date at the front of the string)
    #
    # Outputs:  bool: True if an error was found, false otherwise
    #
    # Methodoology: Loop through each character in the string and count the width of each field,
    # and that there are an appropriate number of fields. Note: the number of characters in the
    # year field is not checked, allowing for four digit years (or more or less), which should
    # future proof this program for hundreds of thousands of years to come
    count_slashes = 0
    chars_since_slash = 0
    correct_date_format = True
    for c in line:
        if c == '/':
            count_slashes += 1
            if chars_since_slash > 2:
                correct_date_format = False
                break
            chars_since_slash = 0
        elif c.isnumeric():
            chars_since_slash += 1
        else:
            print('Error, non-numeric or slash characters in the file created date')
            return True
    if not correct_date_format or count_slashes != 2:
        print('Error, date format not correct. Expecting MM/DD/YY')
        return True
    return False

def check_file_header(file, args):
    """ Check the file header for correctness """
    #
    # Inputs:   file = the file descriptor of the current MATLAB file
    #           args = the argparse argument structure
    #
    # Outputs:  bool: True if an error was found, false otherwise
    #
    # Methodology: Examine each of the four lines sequentially. Exit as soon as an error is found

    # Contributors
    contributors_line = readnn(file)
    contributor_beginning = contributors_line[0:16]
    contributor_model = '% Contributors: '
    if contributor_beginning != contributor_model:
        print('Error, the 1st line should start with "' + contributor_model + '" It was "' + \
                contributor_beginning + '"')
        return True
    if contributors_line[16:] == '':
        print('Error, no contributors listed!')
        return True

    # Course Number
    course_number_line = readnn(file)
    course_number_model = '% Course number: ' + args.coursenumber
    if course_number_line != course_number_model:
        print('Error, the 2nd line should be "' + course_number_model + '". It was "' + \
                course_number_line + '"')
        return True

    # File name
    file_name_line = readnn(file)
    file_name_model= '% File name: ' + os.path.splitext(os.path.basename(args.filename))[0]
    if file_name_line != file_name_model:
        print('Error, the 3rd line should be "' + file_name_model + '". It was "' + \
            file_name_line + '"')
        return True

    # Created
    created_line = readnn(file)
    created_beginning = created_line[0:11]
    created_model = '% Created: '
    if created_beginning != created_model:
        print('Error, the 1st line should start with "' + created_model + '" It was "' + \
                created_beginning + '"')
        return True

    # Check the date, if this succeeds, all checks have been completed without finding problems :)
    return check_date(created_line[11:])

def check_var(var, num):
    """ Checks that the variable conforms to snake_case lettering """
    #
    # Inputs:   var = a string containing the variable name
    #           num = the line number the variable was found on
    #
    # Outputs:  bool: True if an error was found, false otherwise
    #
    # Methodology: Iterate through each character to check that it's lowercase, a number, or a _
    for char in var:
        if char != '_':
            if (not char.islower() and not char.isnumeric()) or not char.isalnum():
                print('On line ' + str(num) + ' the variable ' + var + ' does not conform to ' + \
                    'snake_case naming')
                return 1
    return 0

def check_vars(current, line_num):
    """
    Checks if the line contains a variable declaration. Then checks if the variable name is the
    right style.
    """
    #
    # Inputs:   current = the line potentially containing variable definitions
    #           line_num = the line number of the current line
    #
    # Outputs:  bool: error_count = the number of nonconfomring variable names found on the line
    #
    # Methodology: If an equals sign is found in the string, split the string by it, and
    # determine if a matrix is being assigned to. Further split the string if this is the case.
    # Variable names are isolated by splitting by spaces or commas, and each variable in the matrix
    # or outside of the matrix is then evaluated, and the total number of errors returned

    error_count = 0

    if '=' in current:
        var_chunks = current.split('=')
        var_group = var_chunks[0].strip()
        if '[' in var_group and ']' in var_group:
            # A matrix of variables is being assigned
            var_list = var_group[1:-1].replace(' ', ',').split(',')
            while '' in var_list:
                var_list.remove('')
            while '~' in var_list:
                var_list.remove('~')
            for var in var_list:
                error_count += check_var(var, line_num)
        else:
            var_list = var_group.split(' ')
            while '' in var_list:
                var_list.remove('')
            var = var_list[-1]
            error_count += check_var(var, line_num)
    return error_count

def check_func_vars(current, line_num):
    """ Checks the function input arguments for snake_case compliance """
    #
    # Inputs:   current = the line containing a function declaration
    #           line_num = the line number of the current line
    #
    # Outputs:  bool: error_count = the number of nonconfomring variable names found on the line
    #
    # Methodology: Isolate the parenthesis, and split thhe arguments within. Check each arg

    error_count = 0

    var_chunks = current.split('(')
    var_group = var_chunks[-1].replace(')', '').strip()
    var_list = var_group.split(',')
    for var in var_list:
        var = var.strip()
        error_count += check_var(var, line_num)
    return error_count

def remove_comment_and_strings(dirty_line):
    """ Anything in comments should be ignored by the linter """
    #
    # Inputs:   dirty_line = a line of code potentiallly containing a comment
    #
    # Outputs:  clean_line = the same line with the comment removed
    #
    # Methodology: If a percentage sign is found, indicating the potential of a comment to exist,
    # iterate through each character before the comment is found to verify that the % is not found
    # in a string. As the line is iterated, each character is then copied over to the clean_line,
    # and the copying stops once the start of the comment has been found.
    is_in_string = ''
    if '%' in dirty_line:
        clean_line = ''
        for char in dirty_line:
            if char == '"':
                if is_in_string == '"':
                    is_in_string = ''
                else:
                    is_in_string = '"'
            if char == "'":
                if is_in_string == "'":
                    is_in_string = ''
                else:
                    is_in_string = "'"
            if is_in_string == '' and char == '%':
                break
            if is_in_string == '':
                clean_line += char
        return clean_line
    return dirty_line

def check_func(current, file, check_name, line_num):
    """
    Checks if the line contains a function delcaration, if it does, optionally check its name and
    then check its header
    """
    #
    # Inputs:  current    = a line of code potentiallly containing a function declaration
    #          file       = the file descriptor
    #          check_name = determines whether to check the name for CapitalCamelCase
    #          line_num   = the current line number in the file, for reporting purposes
    #
    # Outputs: 0          = No function declaration was found
    #          -1         = An error with the function docstring was found
    #          <number>   = Number of lines in the file pointer advanced, for keeping track of line
    #                       numbers
    #
    # Methodology: If check_name = true, check the function name. Otherwise evaluate the docstring
    #              line by line. As Inputs and Outputs are similar these are processed with a loop.

    # Cut up string so that variable names containing the word function are not false positives
    components = current.split(' ')
    while '' in components:
        components.remove('')
    # Check if the lilne contains a function declaration
    if 'function' not in components:
        return 0
    # It has a function declaration, evaluate the function here

    # Check the name of the function, if enabled
    if check_name:
        components.remove('function')
        str_no_spaces = ''.join(components)
        names = str_no_spaces.split('(', maxsplit=1)[0] # Get rid of anything after parenthesis
        func_name = names.split('=')[-1] # Get rid of the return variable
        if not func_name.isalnum() or not func_name[0].isupper():
            print('On line ' + str(line_num) + ' the function name ' + func_name + \
                    ' does not conform to CapitialCamelCase naming')
    # Check the docstrings
    comment_line = file.readline()
    line_num += 1 # Keep track of line numbers
    if comment_line != "%\n":
        print('Missing comment spacer line after function declaration on line ' + \
                str(line_num + 1))
        return -1
    complaint_model = '" incorrectly formatted on line '
    next_line = ''

    # Check the Input/Output Arguments
    docstring_section = ['% Inputs:  ', '% Outputs: ']
    for i in enumerate(docstring_section):
        input_line = file.readline()
        line_num += 1
        if input_line[0:11] not in docstring_section[i[0]] or '=' not in input_line:
            print('First Function Input/Output line: "' + input_line + complaint_model + str(line_num))
            return -1
        while next_line := file.readline().replace('\n', ''): # Read all lines in the Input section
            line_num += 1
            if next_line == '%':
                break
            if next_line[0] != '%':
                print('Function Line: "' + next_line + complaint_model + str(line_num))
                return -1
            if next_line[0:9] in ['% Outputs', '% Inputs:', '% Methodo']:
                print('Insufficient spacing between docstring sections on line ' + \
                        str(line_num))
                return -1

    # Check only the first Methodology Line
    methodology_line = file.readline()
    line_num += 1
    if methodology_line[0:15] != '% Methodology: ':
        print('Methodology line on ' + str(line_num) + ' not formatted correctly')
        line_num = -1 # Return error
    return line_num

def main():
    """ Controls all logic flow and reads the file and commands """

    # Parse commands from terminal
    parser = argparse.ArgumentParser(
            prog='matlab_lilnter',
            description = 'Check that matlab files conform to lab function header requirements')

    parser.add_argument('filename',
            help = 'relative or absolute path, including extension, to the target file')
    parser.add_argument('-v', '--novarchecking', action='store_true',
            help = 'Disable checking of var and function name styles')
    parser.add_argument('-n', '--coursenumber', default='ASEN 3801',
            help = 'Check a class number other than ASEN 3801, if the same syntax can be' + \
                    ' used for MATLAB files in a different class, where COURSENUMBER would be' + \
                    '"DEPT XXXX" in place of "ASEN 3801"')

    user_args = parser.parse_args()

    var_errors = 0

    try:
        with open(user_args.filename, 'r', encoding='utf-8') as matlab_file:
            if check_file_header(matlab_file, user_args):
                sys.exit(2)
            linenum = 5
            while raw_line := matlab_file.readline():
                # Remove newlines and indentation
                analysis_line = remove_comment_and_strings(raw_line.replace('\n', '').strip())
                if not user_args.novarchecking:
                    var_errors += check_vars(analysis_line, linenum)
                is_f = check_func(analysis_line, matlab_file, not user_args.novarchecking, linenum)
                if is_f < 0:
                    sys.exit(3)
                elif is_f > 0:
                    if not user_args.novarchecking:
                        var_errors += check_func_vars(analysis_line, linenum)
                    linenum = is_f + 1
                else:
                    linenum += 1
            if var_errors > 0:
                print('Total number of variables with non-comforming names is ' + str(var_errors))
                sys.exit(4)
        print('Everything looks good! Submit it!')
    except FileNotFoundError:
        print('File ' + user_args.filename + ' not found')
        sys.exit(1)

if __name__ == "__main__":
    main()
