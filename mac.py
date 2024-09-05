
import os
import re

#TODO: Order of defines is random? Use orderedDict?

file_in_path = r".\test.mac"
file_out_path = ""
DEFAULT_OUT_PATH = r".\test.cs"

RE_DEFINE = f"^#DEFINE\s+(\w+)\s+([^\s].*$)"
RE_DEFINE_P = f"^#DEFINE\(\)\s+(\w+)\s+([^\s].*$)"
RE_DEFINE_PP = f"^#DEFINE\(\(\)\)\s+(\w+)\s+([^\s].*$)"
RE_DEFINE_FUNC = f"^#DEFINE\s+(\w+)\(([^\)]*)\)\s+([^\s].*$)"
RE_DEFINE_FUNC_P = f"^#DEFINE\(\)\s+(\w+)\(([^\)]*)\)\s+([^\s].*$)"
RE_DEFINE_FUNC_PP = f"^#DEFINE\(\(\)\)\s+(\w+)\(([^\)]*)\)\s+([^\s].*$)"

RE_FOR = f"^#FOR (\w+): \[([^\s,]+(,\s*[^\s,]+)*)\]"
RE_ENDFOR = f"^#ENDFOR"

RE_OUTPUT = f"^#OUTPUT (\.\w+)"
RE_COMMENT = f"^##"

class For:
	def __init__(self, _find_text, _params, _return_line):
		self.find_text = _find_text
		self.params = _params
		if(self.params):
			self.cur_param = 0
		else:
			print(f"NOT_IMPEMENTED_ERROR: For class with no params?")
			self.cur_param = None
		self.return_line = _return_line
		return
	
	def __repr__(self):
		return f"[For: Replacing >{self.find_text}< with each of {self.params}]"

class Define:
	def __init__(self, _find_text, _replace_text, _params, _parens):
		self.find_text = _find_text
		self.replace_text = _replace_text
		self.params = _params
		self.parens = _parens
		return
	
	def __repr__(self):
		if(not self.params):
			return f"[Find: >{self.find_text}< \tReplace: >{self.replace_text}< \tParams: >{self.params}< \tParens: >{self.parens}<]"
		else:
			return f"[Find: >{self.find_expr()}< \tReplace: >{self.replace_expr()}< \tParams: >{self.params}< \tParens: >{self.parens}<]"
	
	def find_expr(self):
		if(not self.params):
			return self.find_text
		s = self.find_text + "\\("
		i = 1
		for _ in self.params:
			#s += f"\\${i}, "
			s += f"(\w+), "
			i += 1
		s = s[:-2]
		s += "\\)"
		return s

	def replace_expr(self):
		if(not self.params):
			if(self.parens == 2):
				return f"({self.replace_text})"
			elif(self.parens == 1):
				return f"({self.replace_text})"
			else:
				return self.replace_text
		s = self.replace_text
		i = 1
		for param in self.params:
			if(self.parens == 2):
				s = re.sub(param, f"(\\\\{i})", s)
			else:
				s = re.sub(param, f"\\\\{i}", s)
			i += 1
		if((self.parens == 1) or (self.parens == 2)):
			return f"({s})"
		else:
			return s

#End of class Define

def check_re_define(line, defines):
	match_define = re.search(RE_DEFINE, line)
	if(match_define):
		find_text = match_define.group(1)
		replace_text = strip_newlines(match_define.group(2))
		define = Define(find_text, replace_text, None, 0)
		defines[find_text] = define
		#print(f">>>FOUND A DEFINE: {define}")
		return True
	match_define_p = re.search(RE_DEFINE_P, line)
	if(match_define_p):
		find_text = match_define_p.group(1)
		replace_text = strip_newlines(match_define_p.group(2))
		define = Define(find_text, replace_text, None, 1)
		defines[find_text] = define
		#print(f">>>FOUND A DEFINE: {define}")
		return True
	match_define_pp = re.search(RE_DEFINE_PP, line)
	if(match_define_pp):
		find_text = match_define_pp.group(1)
		replace_text = strip_newlines(match_define_pp.group(2))
		define = Define(find_text, replace_text, None, 2)
		defines[find_text] = define
		#print(f">>>FOUND A DEFINE: {define}")
		return True
	return False

def check_re_define_func(line, defines):
	match_define_func = re.search(RE_DEFINE_FUNC, line)
	if(match_define_func):
		find_text = match_define_func.group(1)
		params_text = match_define_func.group(2)
		params = re.split("[, ]+", params_text)
		replace_text = strip_newlines(match_define_func.group(3))
		define = Define(find_text, replace_text, params, 0)
		defines[find_text] = define
		#print(f">>>FOUND A DEFINE FUNC: {define}")
		return True
	match_define_func_p = re.search(RE_DEFINE_FUNC_P, line)
	if(match_define_func_p):
		find_text = match_define_func_p.group(1)
		params_text = match_define_func_p.group(2)
		params = re.split("[, ]+", params_text)
		replace_text = strip_newlines(match_define_func_p.group(3))
		define = Define(find_text, replace_text, params, 1)
		defines[find_text] = define
		#print(f">>>FOUND A DEFINE FUNC: {define}")
		return True
	match_define_func_pp = re.search(RE_DEFINE_FUNC_PP, line)
	if(match_define_func_pp):
		find_text = match_define_func_pp.group(1)
		params_text = match_define_func_pp.group(2)
		params = re.split("[, ]+", params_text)
		replace_text = strip_newlines(match_define_func_pp.group(3))
		define = Define(find_text, replace_text, params, 2)
		defines[find_text] = define
		#print(f">>>FOUND A DEFINE FUNC: {define}")
		return True
	return False

def check_re_for(line, i, fors):
	for_define = re.search(RE_FOR, line)
	if(for_define):
		return_line = i + 1
		find_text = for_define.group(1)
		params_text = for_define.group(2)
		params = re.split("[, ]+", params_text)
		for_ = For(find_text, params, return_line)
		fors.append(for_)
		#print(f">>>FOUND A FOR: {for_}")
		return True
	return False

def check_re_endfor(line, i, fors):
	endfor_define = re.search(RE_ENDFOR, line)
	if(endfor_define):
		last_for = fors[len(fors) - 1]
		if(last_for.cur_param != len(last_for.params) - 1):
			#Not the last line, recurse
			last_for.cur_param += 1
			return last_for.return_line
		#TODO: Remove all defines this FOR added?
		fors.remove(last_for)
		return i + 1
	return None

def preprocess(file_in, lines):
	global file_out_path
	first_line = True
	for line in file_in:
		if(first_line):
			first_line = False
			output_ext = re.search(RE_OUTPUT, line)
			if(output_ext):
				dirname = os.path.dirname(file_in_path)
				basename = os.path.basename(file_in_path)
				basename_no_ext = "".join(basename.split(".")[:-1])
				new_ext = output_ext.group(1)
				file_out_path = f"{dirname}\\{basename_no_ext}{new_ext}"
				print(f"OUTPUT: >{file_out_path}<")
				continue
		lines.append(line)
	return

def do_replacements(line, defines, fors):
	last_line = line + "!"
	while(last_line != line):
		last_line = line
		for for_ in fors:
			find_text = for_.find_text
			replace_text = for_.params[for_.cur_param]
			line = re.sub(find_text, replace_text, line)
		for define_name in defines.keys():
			define = defines[define_name]
			line = re.sub(define.find_expr(), define.replace_expr(), line)
	return line

def main():
	global file_out_path
	lines = list()
	with open(file_in_path, "r", newline="\r\n") as file_in:
		preprocess(file_in, lines)
		if(not file_out_path):
			file_out_path = DEFAULT_OUT_PATH

		with open(file_out_path, "w") as file_out:
			i = 0
			defines = dict()
			fors = list()
			while(i < len(lines)):
				line = lines[i]
				if(check_re_define(line, defines)):
					i += 1
					continue
				if(check_re_define_func(line, defines)):
					i += 1
					continue
				if(check_re_for(line, i, fors)):
					i += 1
					continue
				do_endfor = check_re_endfor(line, i, fors)
				if(do_endfor is not None):
					i = do_endfor
					continue

				#Do replacements!
				if(not re.search(RE_COMMENT, line)):
					line = do_replacements(line, defines, fors)
					print(line, end="")
					line_fixed = line.replace("\r\n", "\n")
					file_out.write(line_fixed)
				i += 1
				continue
		#End with open(file_out_path)
	return

def strip_newlines(s):
	s = s.replace("\r", "")
	s = s.replace("\n", "")
	return s

if __name__ == "__main__":
	main()
