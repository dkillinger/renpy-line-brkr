import os
import re 
import sys
import argparse
import tempfile

'''
From repo: https://github.com/dkillinger/renpy-line-brkr
    last updated on: 2024-03-27
    Author: https://github.com/dkillinger
    Consult README.md for User Guide
    Consult LICENSE for License Information
'''

'''
******************************************************************
Author: https://github.com/dkillinger
The Program_Variables class stores all the variables provided to 
Argv_Parser (and checked by Argv_Handler) at runtime to be used in 
the Run_Manager class.
'''
class Program_Variables:
    def __init__(self, read_path: str, write_path: str, text_length : int, data_length : float, image_length: float, space_length: int) -> None:
        self.read_path = read_path
        self.write_path = write_path
        self.text_length = text_length
        self.data_length = data_length
        self.image_length = image_length
        self.space_length = space_length
        self.is_exclude = None
        self.line_list = None
    
    def set_is_exclude(self, is_extrude: bool) -> None:
        self.is_exclude = is_extrude
    
    def set_line_list(self, list_string: str) -> None:
        set_list = list_string.split(',')
        print(set_list)
        for i in range(0, len(set_list)):
            set_list[i] = set_list[i].split('-')
        for i in range(0, len(set_list)):
            if len(set_list[i]) >= 2:
                if set_list[i][0] > set_list[i][1]:
                    raise Exception ('POTENTIAL MISTAKEN: range \'' + set_list[i][0] + '-' + set_list[i][1] + '\' is useless. Did you make a mistake?')
                set_list[i] = [set_list[i][0], set_list[i][1]]
            for j in range(0, len(set_list[i])):
                try:
                    set_list[i][j] = int(set_list[i][j])
                except:
                    raise Exception('INVALID ARG: item \'' + str(set_list[i][j]) + '\' in list \'' + list_string + '\' is not an integer')
        self.line_list = set_list


'''
******************************************************************
Author: https://github.com/dkillinger
The File_Validator class handels all the file validation before 
the program runs successfully. Raises expections when files cannot 
be accessed with the desired permisions, and if the file does not
contain the desired extension.
'''
class File_Validator:
    def __init__(self) -> None:
        return None
    
    def is_valid_mode(file: str, input_mode: str) -> None:
        valid_modes = ['r', 'a', 'w']
        valid_handle = ['', 't', 'b']
        valid_plus = ['', '+']
        for mode in valid_modes:
            for handle in valid_handle:
                for plus in valid_plus:
                    curr_mode = mode + handle + plus
                    if curr_mode == input_mode:
                        return None
        if input_mode == 'x':
            return None
        raise Exception('INVALID MODE: mode \"' + input_mode + '\" is not a valid mode to open the file \"' + file + '\"')
    
    def is_valid_access(file: str, mode: str) -> None:
        if mode == 'r' and not os.access(file, os.R_OK):
            raise Exception('INVALID ACCESS: file \"' + file + '\" does not allow read access')
        elif mode in ['a', 'w']:
            if os.path.exists(file) and not os.access(file, os.W_OK):
                raise Exception('INVALID ACCESS: file \"' + file + '\" does not allow write access')
            else:
                pass
        elif mode == 'x' and os.access(file, os.F_OK):
            raise Exception('INVALID ACCESS: file \"' + file + '\" already exists')
        
    def is_valid_file(file: str, extension: str, mode: str) -> None:
        if (file == ''):
            raise Exception('INVALID FILE: file \"' + file + '\" cannot be an empty string')
        if not os.path.exists(file) and mode not in ['a', 'w']:
            raise Exception('INVALID FILE: file \"' + file + '\" does not exist')
        File_Validator.is_valid_mode(file, mode)
        File_Validator.is_valid_access(file, mode)
        if not file.endswith(extension):
            raise Exception('INVALID FILE: file \"' + file + '\" is not a \"' + extension + '\" file')



'''
******************************************************************
Author: https://github.com/dkillinger
The Line_Breaker class does many things all pertaining to 
adding newlines '\n' to any text within a Ren'Py Text Displayable.
Namely, it validates that the line given is a Text Displayable,
extracts the text from within Text Displayable, and adds newlines 
when char count exceeds text_length until it reaches the end of the 
Text Displayable. This new modified text is reassembled and 
returned for Run_Manager to write.
'''
class Line_Breaker:
    def __init__(self) -> None:
        return None
    
    def prep_word_list(string: str) -> list:
        word_list = re.split(r'(?<!\\)\s+', string.replace(r'\n',' '))
        
        tag_regex = re.compile(r'^{(?!{).+?}')
        data_regex = re.compile(r'^\[(?!\[).+?\]')
        ruby_regex = re.compile(r'^【(?!【)[^\s]+?(?:\||｜)[^\s]+?】')
        text_regex = re.compile(r'^.*?((?=(?<!{){(?!{))|(?=(?<!\[)\[(?!\[))|(?=(?<!【)【(?!【)))')
        for index, word in enumerate(word_list):
            word_split = []
            split_end: str = word
            while split_end != '':
                curr_match: re.Match = None
                match_end: int = None
                if curr_match := tag_regex.match(split_end): # if start is a text tag
                    match_end = curr_match.end(0)
                elif curr_match := data_regex.match(split_end): # if start is a data block
                    match_end = curr_match.end(0)
                elif curr_match := ruby_regex.match(split_end): # if start is a ruby block
                    match_end = curr_match.end(0)
                elif curr_match := text_regex.match(split_end): # if start is a text block
                    match_end = curr_match.end(0)
                match_start = split_end[:match_end]
                match_end = split_end[match_end:]
                if curr_match == None: match_end = '' # the end is a text block
                
                split_end = match_end # grab remaining string
                word_split.append(match_start)
            word_list[index] = word_split
        return word_list
    
    def break_space_tag(space_tag: str, start_len: int, text_length: int, pixel_mult: int) -> tuple[str, int]:
        rem_pixel = (int(re.match(r'^{space=([\d]+)}$', space_tag).group(1)) / pixel_mult) - start_len
        break_space = r'{space=' + str(int(start_len * pixel_mult)) + r'}\n'
        if rem_pixel > text_length:
            while rem_pixel >= text_length:
                rem_pixel -= text_length
                break_space = break_space + r'{space=' + str(int(text_length * pixel_mult)) + r'}\n'
            if rem_pixel > 0:
                break_space = break_space + r'{space=' + str(int(rem_pixel * pixel_mult)) + r'}'
        else:
            break_space = break_space + r'{space=' + str(int(rem_pixel * pixel_mult)) + r'}'
        return break_space, rem_pixel
    
    def break_text(input_text: str, start_len: int, text_length: int) -> tuple[str, int]:
        escape_regex = re.compile(r'(\\[\"\'%\s\\]|%%|{{|\[\[|【【)')
        break_text = r''
        char_count = start_len
        while input_text != '':
            curr_text = ''
            is_escape = False
            curr_escape = escape_regex.search(input_text)
            if curr_escape == None: # we only have regular text left
                curr_text = input_text
                input_text = ''
            elif curr_escape.start(0) == 0:
                curr_text = input_text[:curr_escape.end(0)]
                input_text = input_text[curr_escape.end(0):]
                is_escape = True
            else:
                curr_text = input_text[:curr_escape.start(0)]
                input_text = input_text[curr_escape.start(0):]
            curr_length = 0
            if is_escape: 
                curr_length = 1
            else: 
                curr_length = len(curr_text)
            if curr_length + char_count == text_length:
                break_text = break_text + curr_text + r'\n'
                char_count = 0
            elif curr_length + char_count > text_length:
                rem_length = int(text_length - char_count)
                break_text = break_text + curr_text[:rem_length] + r'\n'
                input_text = curr_text[rem_length:] + input_text
                char_count = 0
            else:
                break_text = break_text + curr_text
                char_count += curr_length
        return break_text, char_count
    
    def break_lines(word_list: list, prog_vars: Program_Variables) -> str:
        rtrn_string = ''
        if prog_vars.text_length > 0:
            char_count = 0
            in_alt = False # within unrendered text-to-speech tag {alt}
            alt_start = re.compile(r'^{alt}$')
            alt_end = re.compile(r'^{/alt}$')
            in_rt = False # within ruby top text tag {rt} or {art}
            rt_start = re.compile(r'^{(?:a)?rt}$')
            rt_end = re.compile(r'^{/(?:a)?rt}$')
            vspace_regex = re.compile(r'^{vspace=[\d]+}$')
            space_regex = re.compile(r'^{space=([\d]+)}$')
            image_regex = re.compile(r'^{image=.+}$')
            tag_regex = re.compile(r'^{(?!{).+?}$')
            data_regex = re.compile(r'^\[(?!\[).+?\]$')
            ruby_regex = re.compile(r'^【(?!【)([^\s]+?)(?:\||｜)([^\s]+?)】$')
            escape_regex = re.compile(r'\\[\"\'%\s\\]|%%|{{|\[\[|【【')
            for word in word_list:
                curr_word = ''
                for word_part in word:
                    temp_part = word_part
                    curr_count = 0
                    is_space = False
                    is_unbreakable = False # word_part cannot be broken (image, data, or ruby)
                    if alt_start.match(word_part): # entry is the beginning of an ALT block!
                        in_alt = True 
                    elif alt_end.match(word_part): # entry is the end of an ALT block
                        in_alt = False
                    elif in_alt: # we're in an ALT block
                        pass # so text won't be rendered (do nothing)
                    elif rt_start.match(word_part): # entry is the beginning of an RT block!
                        in_rt = True
                    elif rt_end.match(word_part): # entry is the end of an RT block
                        in_rt = False
                    elif in_rt: # we're in an RT block
                        pass # so text won't be longer than text preceding it (hopefully)
                    elif vspace_regex.match(word_part): # entry is VSPACE
                        char_count = 0
                    elif space_match := space_regex.match(word_part):
                        if (prog_vars.space_length != 0):
                            curr_count = int(space_match.group(1)) / prog_vars.space_length
                            is_space = True
                        else:
                            curr_count = 0
                    elif image_regex.match(word_part): # entry is IMAGE
                        curr_count = prog_vars.image_length
                        is_unbreakable = True
                    elif tag_regex.match(word_part): # entry is a TAG
                        pass # so tag text won't be rendered (do nothing)
                    elif data_regex.match(word_part): # entry is DATA
                        curr_count = prog_vars.data_length
                        is_unbreakable = True
                    elif ruby_match := ruby_regex.match(word_part): # entry is RUBY
                        curr_count = len(ruby_match.group(1))
                        is_unbreakable = True
                    else: # entry is TEXT
                        escape_list = escape_regex.findall(temp_part)
                        curr_count = len(temp_part) - len(escape_list)
                    
                    if curr_count == 0:
                        pass
                    elif (char_count + curr_count) == prog_vars.text_length:
                        temp_part = temp_part + r'\n'
                        char_count = 0
                    elif (char_count + curr_count) > prog_vars.text_length:
                        if curr_count < prog_vars.text_length:
                            temp_part = r'\n' + temp_part
                            char_count = 0 + curr_count
                        elif is_unbreakable:
                            temp_part = (r'\n' if not rtrn_string.endswith(r'\n') else '') + temp_part + r'\n'
                            char_count = 0
                        elif is_space:
                            temp_part, rem_pixel = Line_Breaker.break_space_tag(word_part, char_count, prog_vars.text_length, prog_vars.space_length)
                            char_count = 0 + (rem_pixel / prog_vars.space_length)
                        else:
                            break_text, rem_len = Line_Breaker.break_text(temp_part, char_count, prog_vars.text_length)
                            temp_part = break_text
                            char_count = 0 + rem_len
                    else: # (char_count + curr_count) < prog_vars.text_length
                        char_count += curr_count
                    curr_word = curr_word + temp_part
                add_space = (' ' if not curr_word.endswith(r'\n') else '')
                char_count += (1 if add_space == ' ' and not (in_alt or in_rt) else 0)
                rtrn_string = rtrn_string + curr_word + add_space     
        else:
            rtrn_string = ' '.join(''.join(word) for word in word_list)
        rtrn_string = re.sub(r'(?<!\\)\s+$', '', re.sub(r'(?<!\\)\s\\n', r'\\n', rtrn_string))
        return rtrn_string
    
    
    def run(string: str, prog_vars: Program_Variables) -> str:
        is_text_disp = re.match(r'^\s*show\s+text\s*\".*\".*$', string) != None
        if not is_text_disp:
            return string
        
        string_start = string[0:string.find('"')+1]
        string_body = string[string.find('"')+1:string.rfind('"')]
        string_end = string[string.rfind('"'):len(string)]
        
        word_list = Line_Breaker.prep_word_list(string_body)
        new_body = Line_Breaker.break_lines(word_list, prog_vars)
        
        return string_start + new_body + string_end



'''
******************************************************************
Author: https://github.com/dkillinger
Run_Manager is a class that manages the read and write files
passed into the Argv_Parser after being checked by Argv_Handler.
Run_Manager also makes sure that, if any -e/--exclude-line or 
-i/--include-line are given, lines are properly included/excluded
before being passed to Line_Breaker for transformation.
'''
class Run_Manager:
    def __init__(self) -> None:
        return None
    
    def handle_files(prog_vars: Program_Variables) -> None:
        tmp = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8')
        with open(prog_vars.read_path, 'r', encoding='utf-8') as read_file:
            try:
                curr_line = 0
                for line in read_file:
                    curr_line += 1
                    if prog_vars.line_list != None:
                        line_found = False
                        for check_lines in prog_vars.line_list:
                            if curr_line == check_lines[0]:
                                line_found = True
                                break
                            elif len(check_lines) == 2 and (check_lines[0] < curr_line <= check_lines[1]):
                                line_found = True
                                break
                        if prog_vars.is_exclude == None:
                            raise Exception('UNKNOWN ERROR: Program_Variables.line_list != None while Program_Variables.is_exclude == None')
                        elif (prog_vars.is_exclude == True) and (line_found == True): # line must be excluded
                            tmp.write(line)
                            continue 
                        elif (prog_vars.is_exclude == False) and (line_found == False): # line cannot be included
                            tmp.write(line)
                            continue
                    line_break_string = Line_Breaker.run(line, prog_vars)
                    tmp.write(line_break_string)
            finally:
                read_file.close()
        tmp.seek(0)
        with open(prog_vars.write_path, 'w', encoding='utf-8') as write_file:
            try:
                for line in tmp:
                    write_file.write(line)
            finally:
                write_file.close()
        tmp.close()



'''
******************************************************************
Author: https://github.com/dkillinger
The Help_Formatter class changes the format of the 
ArgumentParser's help menu (accessed via -h) to NOT show the 
metavar instead of showing it after every flag. Useful for visual 
clarity, and maintains metavar for access.
'''
class Help_Formatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        return ', '.join(action.option_strings)



'''
******************************************************************
Author: https://github.com/dkillinger
The Argv_Parser class stores all of the flags used on the command 
line by using an ArgumentParser. Also adds flag information which 
can be accessed when entering the -h or --help flag on the command
line.
'''
class Argv_Parser:
    def __init__(self):
        # lambda for formatting help menu in argparser
        fmt = lambda prog: Help_Formatter(prog)
        self.parser = argparse.ArgumentParser(usage=sys.argv[0] + ' -r [file options] -t [prog params] [prog options]', description='A collection of flags used by ' + sys.argv[0] + ' for the command line interface.', formatter_class=fmt)
        self.parser._optionals.title = 'flags' # risky line of code, can break ArgumentParser in a future update
        
        self.parser.add_argument('-r', '--read-file', dest='READ', help='(REQUIRED) file program will read from', required=True)
        self.parser.add_argument('-w', '--write-file', dest='WRITE', help='(SEMI-REQUIRED) if not overwriting the read file, set file program will write to')
        self.parser.add_argument('-o', '--overwrite-file', dest='OVERWRITE', help='(SEMI-REQUIRED) if not writing to a set file, overwrite read file with program output', action='store_true')
        self.parser.add_argument('-t', '--text-length', dest='TXT_LEN', type=int, help='set max length of text (in characters) before breaking line', default=0)
        self.parser.add_argument('-d', '--data-length', dest='DATA_LEN', type=float, help='set max length of interpolated data (in characters)', default=0)
        self.parser.add_argument('-i', '--image-length', dest='IMG_LEN', type=float, help='set max length of in text images (in characters)', default=0)
        self.parser.add_argument('-s', '--space-length', dest='SPC_LEN', type=int, help='set max length of space characters (in pixels)', default=0)
        self.parser.add_argument('-x', '--exclude-line', dest='EXCLUDE', help='if not using --include-line, set line(s) in file you want the program to include')
        self.parser.add_argument('-n', '--include-line', dest='INCLUDE', help='if not using --exclude-line, set line(s) in file you want the program to exclude')



'''
******************************************************************
Author: https://github.com/dkillinger
The Argv_Handler class checks all the arguments parsed into
main.py using the Argv_Parser() class. This class guarantees that 
all arguments passed into the program are valid and ready for 
their use in Run_Manager.
'''
class Argv_Handler:
    def __init__(self) -> None:
        return None
    
    def check_args(args: argparse.Namespace) -> Program_Variables:
        prog_vars = None
    
        File_Validator.is_valid_file(args.READ, '.rpy', 'r')
        if args.WRITE == None and args.OVERWRITE == False:
            raise Exception('MISSING ARG: no -w/--write or -o/--overwrite flag is present')
        elif args.WRITE != None and args.OVERWRITE == True:
            raise Exception('INVALID ARGS: both -w/--write and -o/--overwrite cannot be used at the same time')
        elif args.TXT_LEN < 0:
            raise Exception('INVALID ARG: integer value for -t/--text-length cannot be negative')
        elif args.DATA_LEN < -1:
            raise Exception('INVALID ARG: float value for -d/--data-length cannot be less than -1.0')
        elif args.IMG_LEN < -1:
            raise Exception('INVALID ARG: float value for -i/--image-length cannot be less than -1.0')
        elif args.SPC_LEN < 0:
            raise Exception('INVALID ARG: integer value for -s/--space-length cannot be negative')
        else:
            if args.DATA_LEN < 0:
                args.DATA_LEN = args.TXT_LEN
            if args.IMG_LEN < 0:
                args.IMG_LEN = args.TXT_LEN
            if args.WRITE != None:
                File_Validator.is_valid_file(args.WRITE, '.rpy', 'w')
                prog_vars = Program_Variables(args.READ, args.WRITE, args.TXT_LEN, args.DATA_LEN, args.IMG_LEN, args.SPC_LEN)
            else: # args.OVERWRITE == True
                prog_vars = Program_Variables(args.READ, args.READ, args.TXT_LEN, args.DATA_LEN, args.IMG_LEN, args.SPC_LEN)
        
        if args.EXCLUDE != None and args.INCLUDE != None:
            raise Exception('INVALID ARGS: both -e/--exclude-line and -i/--include-line cannot be present')
        elif args.EXCLUDE != None:
            prog_vars.set_is_exclude(True)
            prog_vars.set_line_list(args.EXCLUDE)
        elif args.INCLUDE != None:
            prog_vars.set_is_exclude(False)
            prog_vars.set_line_list(args.INCLUDE)
        else: pass # args.EXCLUDE == None and args.INCLUDE == None
        
        return prog_vars



def main():
    arg_parse = Argv_Parser()
    args = arg_parse.parser.parse_args()
    prog_vars = Argv_Handler.check_args(args)
    Run_Manager.handle_files(prog_vars)



if __name__ == '__main__':
    main()
