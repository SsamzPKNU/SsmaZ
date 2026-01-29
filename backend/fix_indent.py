import json

# ipynb 파일 읽기
with open(r'c:\Users\001\SsmaZ\backend\app\services\text_review\ollama.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# 각 셀의 소스 코드 정리
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source_lines = cell['source']
        
        # 모든 줄을 합쳐서 하나의 문자열로 만들기
        code = ''.join(source_lines)
        
        # 들여쓰기 정리된 코드로 분리
        fixed_lines = []
        for line in code.split('\n'):
            fixed_lines.append(line + '\n')
        
        # 마지막 줄에서 불필요한 개행 제거
        if fixed_lines and fixed_lines[-1] == '\n':
            fixed_lines[-1] = fixed_lines[-1].rstrip('\n')
        
        cell['source'] = fixed_lines

# 수정된 내용을 다시 저장
with open(r'c:\Users\001\SsmaZ\backend\app\services\text_review\ollama.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print("들여쓰기 정리 완료!")
