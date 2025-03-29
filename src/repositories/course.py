from src.models.course import CourseModel

class CourseRepository:

    @staticmethod
    def get_all_courses():
        return CourseModel.find_all()

    @staticmethod
    def create_course(course_data):
        return CourseModel.create(course_data)
