import os

# 1. 获取脚本的绝对路径（含文件名）
script_path = os.path.abspath(__file__)
# 2. 提取脚本所在的目录（去掉文件名，只保留目录）
script_dir = os.path.dirname(script_path)

print(f"脚本绝对路径：{script_path}")
print(f"脚本所在目录：{script_dir}")