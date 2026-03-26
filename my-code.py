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
    def __init__(self, file_name):
        self.file_name = file_name
        self.students = []

    def parse_student_line(self, line):
        line = line.strip()
        if not line:
            raise ValueError("学生信息不能为空")

        parts = line.split("\t")
        if len(parts) != 6:
            raise ValueError("学生信息格式不合法")

        _, name, gender, class_name, student_id, college = parts
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
