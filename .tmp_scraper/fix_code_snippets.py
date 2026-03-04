import os
import re

def fix_code_snippets(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    
    in_code_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this line is the start of a line number sequence
        if not in_code_block and re.match(r'^1\s*$', line):
            is_line_number_sequence = True
            j = i + 1
            expected_num = 2
            while j < len(lines):
                if re.match(r'^' + str(expected_num) + r'\s*$', lines[j]):
                    expected_num += 1
                    j += 1
                elif lines[j].strip() == '':
                    j += 1
                    break
                else:
                    is_line_number_sequence = False
                    break
            
            if is_line_number_sequence:
                i = j
                in_code_block = True
                new_lines.append('```java')
                continue
        
        if in_code_block:
            if line.startswith('Figure ') or line.startswith('图 ') or line.startswith('Listing ') or line.startswith('清单 '):
                in_code_block = False
                new_lines.append('```')
                new_lines.append(line)
            # if we see Chinese characters and not a comment
            elif re.search(r'[\u4e00-\u9fff]', line) and not line.strip().startswith('//') and not line.strip().startswith('>'):
                in_code_block = False
                new_lines.append('```')
                new_lines.append(line)
            # if it's a completely empty line or starts a normal paragraph
            elif line.strip() == '':
                # peek ahead
                k = i + 1
                next_non_empty = ""
                while k < len(lines):
                    if lines[k].strip() != '':
                        next_non_empty = lines[k]
                        break
                    k += 1
                
                if next_non_empty and not next_non_empty.startswith(' ') and not next_non_empty.startswith('\t'):
                    code_keywords = ['public ', 'private ', 'protected ', 'class ', 'var ', 'int ', 'double ', 'string ', 'bool ', 'decimal ', 'void ', 'return ', '@Test', '@Inject', '@BeforeEach', '@Nested', 'context.', 'assert', 'import ', 'package ', 'interface ', 'super(', 'this.', '}']
                    if not any(next_non_empty.strip().startswith(kw) for kw in code_keywords) and not next_non_empty.startswith('//'):
                        in_code_block = False
                        new_lines.append('```')
                        new_lines.append(line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                un_escaped = line.replace('\\_', '_').replace('\\[', '[').replace('\\]', ']')
                new_lines.append(un_escaped)
        else:
            new_lines.append(line)
            
        i += 1

    if in_code_block:
        new_lines.append('```')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

fix_code_snippets("../src/data/post/spring-di.md")
