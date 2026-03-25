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

# 删除后缀
# 既然有删除前缀就有对应的删除后缀
print(nostarch_url.removesuffix(".com"))  # 删除URL的后缀


# 如何在使用字符串时避免语法错误
# 如何在字符串中使用单引号或双引号
# 1. 使用双引号包裹字符串，字符串中可以包含单引号
message = "One of Python's strengths is its diverse community."
print(message)  # 输出字符串，包含单引号
# 2. 使用单引号包裹字符串，字符串中可以包含双引号
message = 'She said, "Python is my favorite language!"'
print(message)  # 输出字符串，包含双引号
# 3. 使用转义字符（\）来在字符串中包含引号
message = 'It\'s important to escape characters in strings.'
print(message)  # 输出字符串，包含单引号
message = "She said, \"Python is my favorite language!\""
print(message)  # 输出字符串，包含双引号

# 数

# 整数
# 整数 数据处理逻辑 + - * /
print(2 + 3)  # 输出5
print(10 - 4)  # 输出6
print(5 * 6)  # 输出30
print(8 / 2)  # 输出4.0
print(8 // 2)  # 输出4，整数除法（floor division）
print(7 // 3)  # 输出2，整数除法（floor division）
print(7 % 3)  # 输出1，取模（modulo）运算，返回除法的余数
print(2 ** 3)  # 输出8，幂运算，2的3次方
print( (2 + 3) * 4) # 输出20，使用括号改变运算顺序

# 浮点数
# 浮点数 是带有小数部分的数字，使用小数点来表示
print(0.1 + 0.2)  # 输出0.30000000000000004，浮点数的精度问题
print(3.14 * 2)  # 输出6.28，浮点数的乘法运算
print(5.0 / 2)  # 输出2.5，浮点数的除法运算
print(5.0 // 2)  # 输出2.0，浮点数的整数除法（floor division）
print(5.0 % 2)  # 输出1.0，浮点数的取模（modulo）运算
print(2.5 ** 3)  # 输出15.625，浮点数的幂运算，2.5的3次方

# 任意两个数相除，结果总是一个浮点数
print(5 / 2)  # 输出2.5，整数除法的结果
print(5.0 / 2)  # 输出2.5，浮点数除法的结果
print(5 / 2.0)  # 输出2.5，浮点数除法的结果
print(5.0 / 2.0)  # 输出2.5，浮点数除法的结果

# 数字运算中，又一个操作数是浮点数，结果也总是一个浮点数
print(5 + 2.0)  # 输出7.0，整数和浮点数的加法运算
print(5 - 2.0)  # 输出3.0，整数和浮点数的减法运算
print(5 * 2.0)  # 输出10.0，整数和浮点数的乘法运算
print(5 / 2.0)  # 输出2.5，整数和浮点数的除法运算
print(5 // 2.0)  # 输出2.0，整数和浮点数的整数除法

# 数字中的下划线
# 在数字中使用下划线可以提高可读性，Python会忽略下划线
universe_age = 14_000_000_000  # 使用下划线来分隔数字，提高可读性
print(universe_age)  # 输出140000000000，Python会忽略下划线

# 同时给多个变量赋值
x, y, z = 0, 0, 0
print(x,y,z)

# 常量
# 在程序的整个生命周期内都保持不变的变量
# python没有内置的常量类型
# 约定俗成的做法是使用全大写字母来命名常量，以表示它们不应该被修改
MAX_CONNECTIONS = 100  # 定义一个常量，表示最大连接数
print(MAX_CONNECTIONS)  # 输出100

# 注释
# 井号后面到行尾的内容都是注释，注释是给人看的，不会被python解释器执行
# 这是一个单行注释，解释代码的作用
print("Hello, World!")  # 这是一个行内注释，解释这一行代码的作用

# 注释的目的/作用
# 1. 解释代码的作用，帮助自己和他人理解代码
# （阐述代码要做什么，以及是如何做的）
# 2. 提供额外的信息，如作者、日期、版本等
# 3. 临时禁用代码，调试代码时使用
# print("This line is commented out and will not be executed.")

# Python之禅
# Python之禅是Python的设计哲学，包含了19条指导原则，由Tim Peters在1999年提出，旨在指导Python的设计和开发
# Python之禅的内容如下：
# 1. 美丽胜于丑陋
# 2. 明了胜于晦涩
# 3. 简洁胜于复杂
# 4. 复杂胜于凌乱
# 5. 扁平胜于嵌套
# 6. 稀疏胜于密集
# 7. 可读性很重要
# 8. 特例不特例到足以破坏规则
# 9. 虽然实用性胜于纯粹性，但不要牺牲美丽和明了
# 10. 错误永远不应该悄无声息地过去
# 11. 除非明确地沉默了它们
# 12. 面对模棱两可的情况，拒绝猜测的诱惑
# 13. 应该有一种--而且最好只有一种--明显的方式来做一件事
# 14. 虽然这并不适用于所有情况
# 15. 做也比不做好
# 16. 如果实现很难解释，那一定是个坏主意
# 17. 如果实现很容易解释，那可能是个好主意
# 18. 命名空间是一种绝妙的主意，我们应该多加利用它

# Python之缠英文
# Simple is better than complex.
# Complex is better than complicated.
# Readability counts.
# Errors should never pass silently.
# Now is better than never.

# 简单点
# 现在就做


# 第三章 列表


# 列表list
# 由一系列特定顺序排列的元素组成

# * 有序
# * 可变
# * 允许重复元素

# 列表使用方括号（[]）来创建，元素之间用逗号分隔
bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles)  # 输出列表
print(bicycles[0])  # 输出列表的第一个元素，索引从0开始
print(bicycles[1])  # 输出列表的第二个元素
print(bicycles[2])  # 输出列表的第三个元素
print(bicycles[3])  # 输出列表的第四个元素

# 索引从0开始

# 修改、添加和删除元素

# 修改列表元素
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)  # 输出列表
motorcycles[0] = 'ducati'  # 修改列表的第一个元素
print(motorcycles)  # 输出修改后的列表

# 在列表中添加元素
# 在列表末尾添加元素
# 使用append()方法在列表末尾添加元素
motorcycles.append('ducati')  # 在列表末尾添加元素
print(motorcycles)  # 输出修改后的列表

# 创建一个空列表
motorcycles = []  # 创建一个空列表

motorcycles.append('honda')  # 在列表末尾添加元素
motorcycles.append('yamaha')  # 在列表末尾添加元素
motorcycles.append('suzuki')  # 在列表末尾添加元素
print(motorcycles)  # 输出列表

# 在列表中插入元素
# 使用insert()方法在列表的指定位置插入元素
motorcycles.insert(0, 'ducati')  # 在列表的第一个位置插入元素
print(motorcycles)  # 输出修改后的列表

# 从列表中删除元素
# 使用del语句根据索引删除列表中的元素
del motorcycles[0]  # 删除列表的第一个元素
print(motorcycles)  # 输出修改后的列表
# 使用pop()方法根据索引删除列表中的元素，并返回被删除的元素
popped_motorcycle = motorcycles.pop(0)  # 删除列表的第一个元素，并返回被删除的元素
print(motorcycles)  # 输出修改后的列表
print(popped_motorcycle)  # 输出被删除的元素
# pop()方法默认删除列表中的最后一个元素
last_owned = motorcycles.pop()  # 删除列表中的最后一个元素，并返回被删除的元素
print(motorcycles)  # 输出修改后的列表
print(last_owned)  # 输出被删除的元素
# 使用remove()方法根据值删除列表中的元素
motorcycles.remove('yamaha')  # 删除列表中值为'suzuki'的元素
print(motorcycles)  # 输出修改后的列表

# 管理列表
# 使用sort()方法永久排序列表
cars = ['bmw', 'audi', 'toyota', 'subaru']
print(cars)  # 输出原始列表
cars.sort()  # 永久排序列表，默认升序
print(cars)  # 输出排序后的列表
cars.sort(reverse=True)  # 永久排序列表，降序
print(cars)  # 输出排序后的列表

# 使用sorted()函数临时排序列表
cars = ['bmw', 'audi', 'toyota', 'subaru']
print("Here is the original list:")
print(cars)  # 输出原始列表
print("\nHere is the sorted list:")
print(sorted(cars))  # 输出临时排序后的列表，默认升序
print("\nHere is the original list again:")
print(cars)  # 输出原始列表，未被修改
# sorted() 函数降序排序
print("\nHere is the sorted list in reverse:")
print(sorted(cars, reverse=True))  # 输出临时排序后的列表，降序

# 反向打印列表 - 永久修改列表的顺序
cars = ['bmw', 'audi', 'toyota', 'subaru']
print(cars)  # 输出原始列表
cars.reverse()  # 反向列表
print(cars)  # 输出反向后的列表

# 确定列表的长度
cars = ['bmw', 'audi', 'toyota', 'subaru']
print(len(cars))  # 输出列表的长度

# !!!！！！
# 使用列表时避免索引错误
# 索引错误是指访问列表中不存在的索引位置时发生的错误
# 1. 确保索引在列表的范围内
# 2. 使用负数索引访问列表中的元素，负数索引从列表的末尾开始计数，-1表示最后一个元素，-2表示倒数第二个元素，以此类推
# 3. 使用len()函数获取列表的长度
# 4. 使用条件语句检查索引是否在列表的范围内
my_list = ['a', 'b', 'c']
index = 3
if index < len(my_list):
    print(my_list[index])  # 输出列表中的元素
else:
    print("Index out of range")  # 输出索引超出范围的提示信息


# 第四章 操作列表






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