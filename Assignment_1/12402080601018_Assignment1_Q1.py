
"""
Q1: Campus Merit Analyzer
Uses lists, tuples, dictionaries, sorting and aggregation.
Python 3.10+
"""

import sys


def analyze_students():
    """Read student records and display semester rankings and toppers."""
    try:
        first_line = sys.stdin.readline().split()

        if len(first_line) != 3:
            raise ValueError("First line must contain n, k and m.")

        n, k, m = map(int, first_line)

        if not (1 <= n <= 100000):
            raise ValueError("Number of students must be between 1 and 100000.")
        if not (1 <= k <= 50):
            raise ValueError("K must be between 1 and 50.")
        if not (1 <= m <= 12):
            raise ValueError("Number of subjects must be between 1 and 12.")

        # Each record is stored as a dictionary.
        students = []
        semester_groups = {}
        subject_top_marks = [-1] * m
        subject_toppers = [[] for _ in range(m)]

        for _ in range(n):
            line = sys.stdin.readline().split()

            if len(line) != m + 4:
                raise ValueError(
                    f"Each student record must contain {m + 4} fields."
                )

            enrollment, name = line[0], line[1]
            semester = int(line[2])
            cpi = float(line[3])
            marks = list(map(int, line[4:]))

            if not (1 <= semester <= 8):
                raise ValueError("Semester must be between 1 and 8.")
            if not (0.0 <= cpi <= 10.0):
                raise ValueError("CPI must be between 0 and 10.")
            if any(mark < 0 or mark > 100 for mark in marks):
                raise ValueError("Each mark must be between 0 and 100.")

            # Tuple stores subject marks; average is used to break CPI ties.
            marks_tuple = tuple(marks)
            average = sum(marks_tuple) / m

            student = {
                "enrollment": enrollment,
                "name": name,
                "semester": semester,
                "cpi": cpi,
                "marks": marks_tuple,
                "average": average,
            }
            students.append(student)

            semester_groups.setdefault(semester, []).append(student)

            # Update the highest marks and retain all tied toppers.
            for subject_index, mark in enumerate(marks_tuple):
                if mark > subject_top_marks[subject_index]:
                    subject_top_marks[subject_index] = mark
                    subject_toppers[subject_index] = [enrollment]
                elif mark == subject_top_marks[subject_index]:
                    subject_toppers[subject_index].append(enrollment)

        # Rank students within each semester.
        for semester in sorted(semester_groups):
            ranked = sorted(
                semester_groups[semester],
                key=lambda student: (
                    -student["cpi"],
                    -student["average"],
                    student["enrollment"],
                ),
            )

            top_students = ranked[:min(k, len(ranked))]
            enrollments = " ".join(
                student["enrollment"] for student in top_students
            )
            print(f"Semester {semester}: {enrollments}")

        # Display every student tied for the highest mark per subject.
        for subject_index, toppers in enumerate(subject_toppers, start=1):
            toppers.sort()
            print(f"S{subject_index}: {' '.join(toppers)}")

    except (ValueError, IndexError) as error:
        print(f"Input Error: {error}")


if __name__ == "__main__":
    analyze_students()
