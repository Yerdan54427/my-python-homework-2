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
