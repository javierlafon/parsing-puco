file_path = 'puco_2026-05.txt'

with open(file_path, 'r', encoding='utf-8') as file:
    for i in range(10):
        line = file.readline()
        if not line:
            break
        print(f"{i+1}: {line.strip()}")