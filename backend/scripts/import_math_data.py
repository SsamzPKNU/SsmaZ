"""
수학 문제 데이터 마이그레이션 스크립트
- 기존 Answers, Submissions, Questions, Assignments, QuestionBank 데이터 삭제
- math_classification (1).csv → QuestionBank 임포트 (200행)
- Assignment 4개 생성 + Question 매핑
- 매핑 규칙: math-csv-db-mapping.md 기반 문제 유형/지시문/카테고리/난이도 적용
"""

import sys
import os
import csv
import re

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.academy import Academy  # noqa: F401 - FK 참조용
from app.models.user import User  # noqa: F401 - FK 참조용
from app.models.assignment import Assignment, Question, QuestionType, Difficulty, AssignmentType
from app.models.submission import Submission, Answer
from app.models.question_bank import QuestionBank

# =============================================================================
# 상수/매핑 테이블
# =============================================================================

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

# 한글 자음 → 숫자 변환
HANGUL_SUBID_MAP = {"ㄱ": 1, "ㄴ": 2, "ㄷ": 3, "ㄹ": 4, "ㅁ": 5, "ㅂ": 6, "ㅅ": 7, "ㅇ": 8}

# problem_id → 카테고리 매핑 (매핑 문서 섹션 5 기준)
CATEGORY_MAP = {
    1: "유리수-분류",
    2: "소수-판별",
    3: "소수-변환",
    4: "순환소수-판별",
    5: "순환소수-변환",
    6: "순환소수표현-판별",
    7: "순환소수-변환",
    8: "순환소수-자릿수",
    9: "순환소수-자릿수",
    10: "순환소수-자릿수",
    11: "유한소수-기약분수",
    12: "유한소수-변환",
    13: "유한소수-변환",
    14: "유한소수-변환",
    15: "유한소수-판별",
    16: "유한소수-판별",
    17: "순환소수-판별",
    18: "소수-판별",
    19: "유한소수-계산",
    20: "유한소수-계산",
    21: "순환소수-분수변환",
    22: "순환소수-분수변환",
    23: "순환소수-분수변환",
    24: "순환소수-분수변환",
    25: "순환소수-분수변환",
    26: "순환소수-분수변환",
    27: "순환소수-분수변환",
    28: "순환소수-분수변환",
    29: "순환소수-분수변환",
    30: "순환소수-분수변환",
    31: "순환소수-분수변환",
    32: "순환소수-분수변환",
    33: "순환소수-분수변환",
    34: "순환소수-분수변환",
    35: "순환소수-비교",
    36: "순환소수-비교",
    37: "순환소수-계산",
    38: "순환소수-보기선택",
    39: "유리수-보기선택",
    40: "순환소수-판별",
    41: "유리수-종합판별",
}

# CHOICE 유형 problem_id 집합
CHOICE_PIDS = {1, 38, 39}

# question 컬럼 패턴 → 한국어 지시문 매핑 (정확 일치)
QUESTION_TEXT_RULES = [
    ("자연수/음의정수/정수가아닌유리수/유리수", "다음 수를 분류하시오"),
    ("유한소수/무한소수", "다음 소수가 유한소수인지 무한소수인지 판별하시오"),
    ("소수로나타내기/유한소수·무한소수", "다음 분수를 소수로 나타내고 유한소수인지 무한소수인지 판별하시오"),
    ("순환소수○/×", "다음이 순환소수인지 판별하시오 (○/×)"),
    ("순환마디/순환소수표현", "다음 순환소수의 순환마디와 순환소수 표현을 구하시오"),
    ("순환소수표현○/×", "다음 순환소수 표현이 옳은지 판별하시오 (○/×)"),
    ("소수/순환마디/순환소수표현", "다음 분수를 소수로 나타내고 순환마디와 순환소수 표현을 구하시오"),
    ("소수점아래50번째자리숫자", "다음 순환소수의 소수점 아래 50번째 자리의 숫자를 구하시오"),
    ("순환소수로나타내기", "다음을 순환소수로 나타내시오"),
    ("순환마디숫자개수", "다음 순환소수의 순환마디 숫자 개수를 구하시오"),
    ("기약분수/분모소인수", "다음을 기약분수로 나타내고 분모의 소인수를 구하시오"),
    ("10의거듭제곱으로유한소수변환", "다음 분수를 10의 거듭제곱을 이용하여 유한소수로 변환하시오"),
    ("10의거듭제곱유한소수변환", "다음 분수를 10의 거듭제곱을 이용하여 유한소수로 변환하시오"),
    ("유한소수로나타내기", "다음 분수를 유한소수로 나타내시오"),
    ("분모소인수/유한소수여부", "다음 분수의 분모 소인수를 구하고 유한소수 여부를 판별하시오"),
    ("유한소수○/×", "다음이 유한소수인지 판별하시오 (○/×)"),
    ("순환소수로만나타낼수있는것○/×", "다음을 순환소수로만 나타낼 수 있는지 판별하시오 (○/×)"),
    ("유한소수유/순환소수순", "다음이 유한소수인지 순환소수인지 판별하시오 (유/순)"),
    ("유한소수만들기위해곱할가장작은자연수", "유한소수로 만들기 위해 곱해야 할 가장 작은 자연수를 구하시오"),
    ("순환소수→기약분수과정", "다음 순환소수를 기약분수로 나타내는 과정을 구하시오"),
    ("분수변환에필요한식", "다음 순환소수의 분수 변환에 필요한 식을 고르시오"),
    ("순환소수→기약분수", "다음 순환소수를 기약분수로 나타내시오"),
    ("순환소수→분수공식과정", "다음 순환소수를 분수로 나타내는 공식 과정을 구하시오"),
    ("부등호비교", "두 수의 크기를 비교하시오"),
    ("계산", "다음을 계산하시오"),
    ("보기에서알맞은값", "보기에서 알맞은 값을 고르시오"),
    ("유리수가아닌것모두고르기", "다음 중 유리수가 아닌 것을 모두 고르시오"),
]


# =============================================================================
# 헬퍼 함수
# =============================================================================

def load_csv(path: str) -> list[dict]:
    """CSV 파일을 읽어 딕셔너리 리스트로 반환"""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"[CSV] {len(rows)}행 로드 완료: {path}")
    return rows


def convert_sub_id(sub_id_raw: str) -> int:
    """한글 자음 sub_id를 숫자로 변환"""
    if sub_id_raw in HANGUL_SUBID_MAP:
        return HANGUL_SUBID_MAP[sub_id_raw]
    return int(sub_id_raw)


def _format_pid39_display(value_display: str) -> str:
    """pid 39의 value_display를 보기 형태로 재구성
    'ㄱ0/ㄴ0.101001000…/ㄷ-23÷3/...' → 'ㄱ) 0  ㄴ) 0.101001000…  ㄷ) -23÷3  ...'
    """
    items = value_display.split("/")
    parts = []
    for item in items:
        label = item[0]
        value = item[1:]
        parts.append(f"{label}) {value}")
    return "  ".join(parts)


def build_question_text(row: dict) -> str:
    """유형별 한국어 지시문 생성"""
    pid = int(row["problem_id"])
    value_display = row["value_display"]
    question = row["question"]

    # pid 40: x=3.4252525... 설명 판별
    if pid == 40:
        return f"x = 3.4252525...일 때, 다음 설명이 옳은지 판별하시오 (○/×): {value_display}"

    # pid 41: 일반 설명 판별
    if pid == 41:
        return f"다음 설명이 옳은지 판별하시오 (○/×): {value_display}"

    # pid 39: value_display를 보기 형태로 재구성
    if pid == 39:
        formatted = _format_pid39_display(value_display)
        return f"다음 중 유리수가 아닌 것을 모두 고르시오: {formatted}"

    # 정확 일치 패턴 매칭
    for pattern, instruction in QUESTION_TEXT_RULES:
        if question == pattern:
            return f"{instruction}: {value_display}"

    # 소수점아래N번째자리 패턴 (regex) - pid 9, 10 등
    m = re.match(r"소수점아래(\d+)번째자리", question)
    if m:
        n = m.group(1)
        return f"다음 순환소수의 소수점 아래 {n}번째 자리의 숫자를 구하시오: {value_display}"

    # 매칭 실패 시 기본 형태 (발생하지 않아야 함)
    print(f"  [WARN] 패턴 매칭 실패: pid={pid}, question='{question}'")
    return f"{question}: {value_display}"


def get_question_type(pid: int) -> QuestionType:
    """problem_id로 문제 유형 결정"""
    if pid in CHOICE_PIDS:
        return QuestionType.CHOICE
    return QuestionType.SHORT_ANSWER


def get_difficulty(pid: int) -> Difficulty:
    """problem_id로 난이도 결정"""
    if pid <= 6:
        return Difficulty.EASY
    elif pid <= 20:
        return Difficulty.MEDIUM
    else:
        return Difficulty.HARD


def get_options(pid: int, row: dict):
    """CHOICE 유형만 옵션 배열 반환, 나머지는 None"""
    if pid == 1:
        return ["자연수", "음의정수", "정수가아닌유리수", "유리수"]
    elif pid == 38:
        return ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", "ㅈ"]
    elif pid == 39:
        # value_display에서 파싱: "ㄱ0/ㄴ0.101001000…/..."
        items = row["value_display"].split("/")
        return [f"{item[0]} {item[1:]}" for item in items]
    return None


def get_correct_answer(row: dict) -> str:
    """정답 반환 (전 유형 answer 그대로 저장)"""
    return row["answer"]


# =============================================================================
# 마이그레이션 단계
# =============================================================================

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
    """2단계: QuestionBank 임포트 (매핑 규칙 적용)"""
    print("\n=== 2단계: QuestionBank 임포트 ===")

    qb_list = []
    for row in rows:
        pid = int(row["problem_id"])
        qb = QuestionBank(
            academy_id=ACADEMY_ID,
            category=CATEGORY_MAP[pid],
            question_text=build_question_text(row),
            question_type=get_question_type(pid),
            options=get_options(pid, row),
            correct_answer=get_correct_answer(row),
            difficulty=get_difficulty(pid),
        )
        db.add(qb)
        qb_list.append(qb)

    db.flush()  # ID 할당을 위해 flush
    print(f"  QuestionBank: {len(qb_list)}건 추가")
    return qb_list


def step3_create_assignments(db, rows: list[dict]):
    """3단계: Assignment 4개 + Question 생성 (매핑 규칙 적용)"""
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
            pid = int(row["problem_id"])
            question = Question(
                assignment_id=assignment.assignment_id,
                question_number=idx,
                question_text=build_question_text(row),
                question_type=get_question_type(pid),
                options=get_options(pid, row),
                correct_answer=get_correct_answer(row),
                points=1,
                category=CATEGORY_MAP[pid],
                difficulty=get_difficulty(pid),
            )
            db.add(question)

        print(f"  Assignment '{title}' (id={assignment.assignment_id}): {len(filtered)}문제")


def step4_verify(db):
    """4단계: 결과 검증 (유형별/난이도별/카테고리별 카운트)"""
    print("\n=== 4단계: 결과 검증 ===")

    # 기본 카운트
    for model, name in [
        (QuestionBank, "QuestionBank"),
        (Assignment, "Assignments"),
        (Question, "Questions"),
        (Submission, "Submissions"),
        (Answer, "Answers"),
    ]:
        count = db.query(model).count()
        print(f"  {name}: {count}건")

    # 유형별 카운트 (QuestionBank 기준)
    print("\n  --- 유형별 (QuestionBank) ---")
    for qt in QuestionType:
        count = db.query(QuestionBank).filter(QuestionBank.question_type == qt).count()
        if count > 0:
            print(f"  {qt.value}: {count}건")

    # 난이도별 카운트 (QuestionBank 기준)
    print("\n  --- 난이도별 (QuestionBank) ---")
    for diff in Difficulty:
        count = db.query(QuestionBank).filter(QuestionBank.difficulty == diff).count()
        if count > 0:
            print(f"  {diff.value}: {count}건")

    # 카테고리 종류 (QuestionBank 기준)
    categories = db.query(QuestionBank.category).distinct().all()
    print(f"\n  --- 카테고리: {len(categories)}종 ---")
    for (cat,) in sorted(categories):
        count = db.query(QuestionBank).filter(QuestionBank.category == cat).count()
        print(f"  {cat}: {count}건")


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
