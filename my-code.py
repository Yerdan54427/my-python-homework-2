import os
import random
from datetime import datetime


class Student:
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


class ExamSystem:
    def __init__(self, file_name="人工智能编程语言学生名单.txt"):
        self.file_name = file_name
        self.students = []
        self.exam_arrangement = []

    @staticmethod
    def validate_student_id(student_id):
        if not student_id:
            return False
        return student_id.isdigit()

    def parse_student_line(self, line):
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

    def load_students(self):
        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                self.students = []
                next(file, None)

                for line in file:
                    try:
                        student = self.parse_student_line(line)
                        self.students.append(student)
                    except ValueError:
                        continue
        except FileNotFoundError:
            print(f"文件不存在：{self.file_name}")

    def find_student_by_id(self, student_id):
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None

    def random_pick_students(self, count):
        if count <= 0:
            raise ValueError("抽取人数必须大于 0")

        if count > len(self.students):
            raise ValueError("抽取人数不能超过学生总人数")

        return random.sample(self.students, count)

    def generate_exam_seating(self):
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

        for seat_number, student in self.exam_arrangement:
            file_name = f"{seat_number:02d}.txt"
            file_path = os.path.join(folder_name, file_name)

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(f"座位号：{seat_number}\n")
                file.write(f"姓名：{student.name}\n")
                file.write(f"学号：{student.student_id}\n")
