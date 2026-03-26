import os
import random
from datetime import datetime


# 清理旧的准考证文本，避免历史结果残留。


def clear_admission_ticket_files(folder_name):
    if not os.path.isdir(folder_name):
        return

    for entry in os.scandir(folder_name):
        if entry.is_file() and entry.name.lower().endswith(".txt"):
            os.remove(entry.path)


class Student:
    # 保存单个学生的基础信息。
    def __init__(self, student_id, name, gender, class_name, college):
        self.student_id = student_id
        self.name = name
        self.gender = gender
        self.class_name = class_name
        self.college = college

    def __str__(self):
        return (
            f"学号：{self.student_id}，姓名：{self.name}，性别：{self.gender}，"
            f"班级：{self.class_name}，学院：{self.college}"
        )


class StudentDataConflictError(ValueError):
    # 同一学号对应信息不一致时抛出此异常。
    pass


class ExamSystem:
    # 考试管理系统：负责导入、查询、排座和生成文件。
    def __init__(self, file_name="人工智能编程语言学生名单.txt"):
        self.file_name = file_name
        self.students = []
        self.exam_arrangement = []

    @staticmethod
    def validate_student_id(student_id):
        # 学号必须是非空数字字符串。
        if not student_id:
            return False
        return student_id.isdigit()

    def parse_student_line(self, line):
        # 将名单中的一行解析为 Student 对象。
        line = line.strip()
        if not line:
            raise ValueError("学生信息不能为空")

        parts = line.split("\t")
        if len(parts) != 6:
            raise ValueError("学生信息格式不合法")

        _, name, gender, class_name, student_id, college = parts
        if not self.validate_student_id(student_id):
            raise ValueError("学号格式不合法")

        return Student(student_id, name, gender, class_name, college)

    @staticmethod
    def get_student_conflict_fields(existing_student, current_student):
        # 找出两条同学号记录中内容不一致的字段。
        field_pairs = [
            ("姓名", existing_student.name, current_student.name),
            ("性别", existing_student.gender, current_student.gender),
            ("班级", existing_student.class_name, current_student.class_name),
            ("学院", existing_student.college, current_student.college),
        ]
        return [
            field_name
            for field_name, existing_value, current_value in field_pairs
            if existing_value != current_value
        ]

    def load_students(self):
        # 读取名单文件，并跳过无效数据与重复记录。
        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                self.students = []
                students_by_id = {}
                duplicate_student_ids = set()
                loaded_count = 0
                skipped_invalid_count = 0
                skipped_duplicate_count = 0
                next(file, None)

                for line_number, line in enumerate(file, start=2):
                    try:
                        student = self.parse_student_line(line)
                        existing_student = students_by_id.get(student.student_id)
                        if existing_student is not None:
                            # 同一学号再次出现时，先判断是简单重复还是数据冲突。
                            conflict_fields = self.get_student_conflict_fields(
                                existing_student, student
                            )
                            if conflict_fields:
                                conflict_fields_text = "、".join(conflict_fields)
                                raise StudentDataConflictError(
                                    f"第 {line_number} 行数据冲突：学号 "
                                    f"{student.student_id} 的{conflict_fields_text}不一致"
                                )

                            duplicate_student_ids.add(student.student_id)
                            skipped_duplicate_count += 1
                            print(
                                f"第 {line_number} 行已跳过：学号 {student.student_id} 重复"
                            )
                            continue

                        students_by_id[student.student_id] = student
                        self.students.append(student)
                        loaded_count += 1
                    except StudentDataConflictError as error:
                        print(f"导入失败：{error}")
                        raise SystemExit(1)
                    except ValueError as error:
                        # 单行格式出错时只跳过当前行，不影响后续导入。
                        skipped_invalid_count += 1
                        print(f"第 {line_number} 行已跳过：{error}")
                skipped_count = skipped_invalid_count + skipped_duplicate_count
                print(
                    f"导入完成：成功导入 {loaded_count} 条，跳过 {skipped_count} 条。"
                )
                if duplicate_student_ids:
                    duplicate_list = ", ".join(sorted(duplicate_student_ids))
                    print(f"发现重复学号，已跳过重复记录：{duplicate_list}")
        except FileNotFoundError:
            print(f"文件不存在：{self.file_name}")

    def find_student_by_id(self, student_id):
        # 按学号顺序查找学生。
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None

    def random_pick_students(self, count):
        # 随机抽取指定数量的学生用于点名。
        if count <= 0:
            raise ValueError("抽取人数必须大于 0")

        if count > len(self.students):
            raise ValueError("抽取人数不能超过学生总人数")

        return random.sample(self.students, count)

    def generate_exam_seating(self):
        # 打乱学生顺序后为每位学生分配座位号。
        shuffled_students = self.students[:]
        random.shuffle(shuffled_students)

        seating_arrangement = []
        for seat_number, student in enumerate(shuffled_students, start=1):
            seating_arrangement.append((seat_number, student))

        self.exam_arrangement = seating_arrangement
        return seating_arrangement

    def save_exam_arrangement(self, output_file="考场安排.txt"):
        if not self.exam_arrangement:
            raise ValueError("暂无考场安排可保存")

        # 将排座结果导出到文本文件。
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(f"生成时间：{current_time}\n")
            file.write("座位号\t姓名\t学号\n")

            for seat_number, student in self.exam_arrangement:
                file.write(
                    f"{seat_number}\t{student.name}\t{student.student_id}\n"
                )

    def generate_admission_tickets(self, folder_name="准考证"):
        if not self.exam_arrangement:
            raise ValueError("暂无考场安排可生成准考证")

        os.makedirs(folder_name, exist_ok=True)
        # 先删除旧文件，保证目录里只保留本次结果。
        clear_admission_ticket_files(folder_name)

        for seat_number, student in self.exam_arrangement:
            file_name = f"{seat_number:02d}.txt"
            file_path = os.path.join(folder_name, file_name)

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(f"座位号：{seat_number}\n")
                file.write(f"姓名：{student.name}\n")
                file.write(f"学号：{student.student_id}\n")


def main():
    # 主程序入口：加载数据并循环处理菜单操作。
    exam_system = ExamSystem()
    exam_system.load_students()

    print("欢迎使用考试管理系统！")
    if not exam_system.students:
        print("当前未加载到学生信息，请检查学生名单文件。")

    while True:
        print("\n===== 主菜单 =====")
        print("1. 查找学生")
        print("2. 随机点名")
        print("3. 生成考场安排表")
        print("4. 生成准考证")
        print("5. 退出系统")

        try:
            choice = input("请输入功能编号：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出系统。")
            break

        if choice == "1":
            # 查询功能：按学号精确查找学生。
            student_id = input("请输入要查找的学号：").strip()
            if not ExamSystem.validate_student_id(student_id):
                print("输入的学号格式不正确。")
                continue

            student = exam_system.find_student_by_id(student_id)
            if student is None:
                print("未找到该学生。")
            else:
                print(student)
        elif choice == "2":
            # 点名功能：随机抽取指定人数。
            try:
                count = int(input("请输入随机点名人数：").strip())
                picked_students = exam_system.random_pick_students(count)
                print("随机点名结果：")
                for student in picked_students:
                    print(student)
            except ValueError as error:
                print(f"输入有误：{error}")
        elif choice == "3":
            # 先生成座位表，再把结果保存到文件中。
            try:
                seating_arrangement = exam_system.generate_exam_seating()
                exam_system.save_exam_arrangement()
                print("考场安排表已生成并保存到 考场安排.txt")
                for seat_number, student in seating_arrangement:
                    print(
                        f"座位号：{seat_number}，姓名：{student.name}，"
                        f"学号：{student.student_id}"
                    )
            except ValueError as error:
                print(f"生成失败：{error}")
        elif choice == "4":
            # 准考证依赖当前座位表，因此要先完成排座。
            try:
                exam_system.generate_admission_tickets()
                print("准考证已生成到 准考证 文件夹。")
            except ValueError as error:
                print(f"生成失败：{error}")
        elif choice == "5":
            print("已退出系统。")
            break
        else:
            print("无效的菜单选项，请重新输入。")


if __name__ == "__main__":
    main()
