"""
수학 문제 데이터 마이그레이션 스크립트
- 기존 Answers, Submissions, Questions, Assignments, QuestionBank 데이터 삭제
- math_classification (1).csv → QuestionBank 임포트 (200행)
- Assignment 4개 생성 + Question 매핑
"""

import sys
import os
import csv

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.academy import Academy  # noqa: F401 - FK 참조용
from app.models.user import User  # noqa: F401 - FK 참조용
from app.models.assignment import Assignment, Question, QuestionType, Difficulty, AssignmentType
from app.models.submission import Submission, Answer
from app.models.question_bank import QuestionBank

# CSV 파일 경로
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "math_classification (1).csv")

# Assignment 분할 설정: (제목, problem_id 범위)
ASSIGNMENT_SPLITS = [
    ("수학 유리수와 순환소수 (1)", 1, 10),
    ("수학 유리수와 순환소수 (2)", 11, 20),
    ("수학 유리수와 순환소수 (3)", 21, 30),
    ("수학 유리수와 순환소수 (4)", 31, 41),
]

ACADEMY_ID = 1
TEACHER_ID = 2


def load_csv(path: str) -> list[dict]:
    """CSV 파일을 읽어 딕셔너리 리스트로 반환"""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"[CSV] {len(rows)}행 로드 완료: {path}")
    return rows


def build_question_text(row: dict) -> str:
    """CSV 행에서 question_text 생성: (problem_id-sub_id) value_display : question"""
    return f"({row['problem_id']}-{row['sub_id']}) {row['value_display']} : {row['question']}"


def step1_delete_existing(db):
    """1단계: 기존 데이터 삭제 (FK 순서)"""
    print("\n=== 1단계: 기존 데이터 삭제 ===")

    counts = {}
    for model, name in [
        (Answer, "Answers"),
        (Submission, "Submissions"),
        (Question, "Questions"),
        (Assignment, "Assignments"),
        (QuestionBank, "QuestionBank"),
    ]:
        count = db.query(model).delete()
        counts[name] = count
        print(f"  {name}: {count}건 삭제")

    return counts


def step2_import_question_bank(db, rows: list[dict]) -> list[QuestionBank]:
    """2단계: QuestionBank 임포트"""
    print("\n=== 2단계: QuestionBank 임포트 ===")

    qb_list = []
    for row in rows:
        qb = QuestionBank(
            academy_id=ACADEMY_ID,
            category=row["question"],
            question_text=build_question_text(row),
            question_type=QuestionType.SHORT_ANSWER,
            options=None,
            correct_answer=row["answer"],
            difficulty=Difficulty.MEDIUM,
        )
        db.add(qb)
        qb_list.append(qb)

    db.flush()  # ID 할당을 위해 flush
    print(f"  QuestionBank: {len(qb_list)}건 추가")
    return qb_list


def step3_create_assignments(db, rows: list[dict]):
    """3단계: Assignment 4개 + Question 생성"""
    print("\n=== 3단계: Assignment & Question 생성 ===")

    for title, pid_start, pid_end in ASSIGNMENT_SPLITS:
        # Assignment 생성
        assignment = Assignment(
            academy_id=ACADEMY_ID,
            teacher_id=TEACHER_ID,
            title=title,
            assignment_type=AssignmentType.NORMAL,
            is_active=True,
        )
        db.add(assignment)
        db.flush()  # assignment_id 할당

        # 해당 problem_id 범위의 CSV 행 필터링
        filtered = [r for r in rows if pid_start <= int(r["problem_id"]) <= pid_end]

        # Question 생성
        for idx, row in enumerate(filtered, start=1):
            question = Question(
                assignment_id=assignment.assignment_id,
                question_number=idx,
                question_text=build_question_text(row),
                question_type=QuestionType.SHORT_ANSWER,
                options=None,
                correct_answer=row["answer"],
                points=1,
                category=row["question"],
                difficulty=Difficulty.MEDIUM,
            )
            db.add(question)

        print(f"  Assignment '{title}' (id={assignment.assignment_id}): {len(filtered)}문제")


def step4_verify(db):
    """4단계: 결과 검증"""
    print("\n=== 4단계: 결과 검증 ===")

    for model, name in [
        (QuestionBank, "QuestionBank"),
        (Assignment, "Assignments"),
        (Question, "Questions"),
        (Submission, "Submissions"),
        (Answer, "Answers"),
    ]:
        count = db.query(model).count()
        print(f"  {name}: {count}건")


def main():
    print("=" * 60)
    print("수학 문제 데이터 마이그레이션 시작")
    print("=" * 60)

    # CSV 로드
    rows = load_csv(CSV_PATH)

    db = SessionLocal()
    try:
        step1_delete_existing(db)
        step2_import_question_bank(db, rows)
        step3_create_assignments(db, rows)

        db.commit()
        print("\n[OK] 커밋 완료!")

        step4_verify(db)

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] 롤백됨: {e}")
        raise
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("마이그레이션 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
