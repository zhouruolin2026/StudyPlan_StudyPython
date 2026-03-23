# python学习 开始

# 第一章 起步


# 安装python
# 下载安装包，下一步下一步下一步 --> 安装完成

# 运行python - python交互式环境
# 1. 打开cmd命令行窗口，输入python，回车，进入python交互式环境
# 2. 在python交互式环境中输入代码，回车，执行代码
print("Hello, World!")
# 3. 输入exit()，回车，退出python交互式环境

# 运行python文件 - 执行python文件
# 1. 使用文本编辑器（如Notepad++、Sublime Text、VS Code等）创建一个python文件，命名为文件名.py
# hello_world.py
# 2. 在文件中输入python代码，保存文件
print("Hello, World!")
# 3. 打开cmd命令行窗口，进入到python文件所在的目录
# 4. 输入python 文件名.py，回车，执行python文件
# python hello_world.py
# 或者
# 1. 在cmd命令行窗口，输入python 全路径/文件名.py，回车，执行python文件
# （如：python C:/Users/username/Desktop/文件名.py）


# 第二章 变量和简单的数据类型


# 变量 variable
# 变量是用来存储数据的容器，可以在程序中使用变量来存储和操作数据
# 变量是可以赋值的标签，变量指向特定的值

# hello_world.py
message = "Hello Python world!"
print(message)
# python hello_world.py
message = "Hello Python Crash Course world!"
print(message)

# 变量命名注意： 小写

# 基本数据类型 - 字符串
# 字符串 string
# 字符串是由一个或多个字符组成的文本数据，使用单引号（'）或双引号（"）来创建/标识字符串
# 有单引号/双引号包裹的文本 是 字符串
# 没有被包裹的 是 变量名/函数名/类名/python关键字等

message = "Hello Python world!"
# message 是 变量名
# "Hello Python world!" 是 字符串

# 使用方法修改字符串的大小写
message = "Hello Python world!"
print(message.lower())  # 将字符串转换为小写
print(message.upper())  # 将字符串转换为大写
print(message.title())  # 将字符串的每个单词的首字母大写
print(message)  # 原字符串不变

# 在字符串中使用变量
# full_name.py
first_name = "ada"
last_name = "lovelace"
full_name = first_name + " " + last_name  # 使用字符串连接符 + 将字符串连接起来
print(full_name)  # 输出完整的名字
full_name2 = f"{first_name} {last_name}"  # 使用f-string格式化字符串
# f format(设置格式) string(字符串)
print(full_name2)  # 输出完整的名字
print(f"Hello, {full_name.title()}!")  # 使用f-string格式化字符串，输出问候语

# 使用制表符或换行符来添加空白
print("Python")  # 输出Python
print("\tPython")  # 输出Python，前面有一个制表符（tab）
print("Languages:\nPython\nC\nJavaScript")  # 输出多行文本，每行一个编程语言

# 删除字符串中的空白
favorite_language = " Python "
print(favorite_language)  # 输出字符串，前后有空白
print(favorite_language.lstrip())  # 删除字符串左侧的空白
print(favorite_language.rstrip())  # 删除字符串右侧的空白
print(favorite_language.strip()) # 删除字符串两侧的空白

# 删除前缀
nostarch_url = "https://www.nostarch.com"
print(nostarch_url)  # 输出完整的URL
print(nostarch_url.removeprefix("https://"))  # 删除URL的前缀
print(nostarch_url.removeprefix("http://"))  # 删除URL的前缀（没有效果，因为URL的前缀是https://）


# 第三章
# 第四章
# 第五章
# 第六章
# 第七章
# 第八章
# 第九章
# 第十章
# 第十一章
# 第十二章
# 第十三章
# 第十四章
# 第十五章
# 第十六章
# 第十七章
# 第十八章
# 第十九章
# 第二十章
# 第二十一章
# 第二十二章
# 第二十三章
# 第二十四章
# 第二十五章
# 第二十六章
# 第二十七章
# 第二十八章