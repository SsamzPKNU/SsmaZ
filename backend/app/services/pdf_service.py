"""
PDF 생성 서비스
"""

from io import BytesIO
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from app.models.assignment import Assignment, Question
from app.models.submission import Submission
from app.models.student import Student
import os

# 한글 폰트 등록 시도
FONT_NAME = "Helvetica"
FONT_NAME_BOLD = "Helvetica-Bold"

# 한글 폰트 경로 (시스템에 따라 다름)
KOREAN_FONT_PATHS = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux
    "C:/Windows/Fonts/malgun.ttf",  # Windows
    "/System/Library/Fonts/AppleGothic.ttf",  # macOS
]

for font_path in KOREAN_FONT_PATHS:
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('Korean', font_path))
            FONT_NAME = "Korean"
            FONT_NAME_BOLD = "Korean"
            break
        except:
            pass


def generate_assignment_pdf(db: Session, assignment_id: int) -> bytes:
    """
    과제 문제지 PDF 생성
    """
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()

    if not assignment:
        raise ValueError("과제를 찾을 수 없습니다")

    questions = db.query(Question).filter(
        Question.assignment_id == assignment_id
    ).order_by(Question.question_number).all()

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # 제목
    p.setFont(FONT_NAME_BOLD, 18)
    p.drawString(20 * mm, height - 25 * mm, assignment.title)

    # 과제 정보
    p.setFont(FONT_NAME, 10)
    if assignment.due_date:
        p.drawString(20 * mm, height - 35 * mm, f"마감일: {assignment.due_date}")

    if assignment.description:
        p.drawString(20 * mm, height - 42 * mm, f"설명: {assignment.description[:50]}...")

    # 구분선
    p.line(20 * mm, height - 48 * mm, width - 20 * mm, height - 48 * mm)

    # 문제 출력
    y = height - 60 * mm
    p.setFont(FONT_NAME, 11)

    for q in questions:
        # 페이지 넘김 체크
        if y < 50 * mm:
            p.showPage()
            y = height - 30 * mm
            p.setFont(FONT_NAME, 11)

        # 문제 번호 및 내용
        question_text = q.question_text
        if len(question_text) > 80:
            question_text = question_text[:80] + "..."

        p.setFont(FONT_NAME_BOLD, 11)
        p.drawString(20 * mm, y, f"{q.question_number}.")
        p.setFont(FONT_NAME, 11)
        p.drawString(28 * mm, y, question_text)
        y -= 8 * mm

        # 객관식 보기
        if q.options and q.question_type.value == "CHOICE":
            for i, opt in enumerate(q.options):
                if y < 40 * mm:
                    p.showPage()
                    y = height - 30 * mm
                    p.setFont(FONT_NAME, 11)

                option_text = opt if len(opt) <= 60 else opt[:60] + "..."
                p.drawString(28 * mm, y, f"{chr(9312 + i)} {option_text}")  # ①②③④
                y -= 6 * mm

        # 배점 표시
        p.setFont(FONT_NAME, 9)
        p.drawString(width - 35 * mm, y + 6 * mm, f"({q.points}점)")
        p.setFont(FONT_NAME, 11)

        y -= 8 * mm

    # 답안 작성란
    p.showPage()
    p.setFont(FONT_NAME_BOLD, 14)
    p.drawString(20 * mm, height - 25 * mm, "답안 작성란")
    p.line(20 * mm, height - 30 * mm, width - 20 * mm, height - 30 * mm)

    y = height - 45 * mm
    p.setFont(FONT_NAME, 11)

    for q in questions:
        if y < 40 * mm:
            p.showPage()
            y = height - 30 * mm

        p.drawString(20 * mm, y, f"{q.question_number}번: ____________________")
        y -= 12 * mm

    p.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_result_pdf(db: Session, submission_id: int) -> bytes:
    """
    채점 결과지 PDF 생성
    """
    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id
    ).first()

    if not submission:
        raise ValueError("제출 기록을 찾을 수 없습니다")

    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == submission.assignment_id
    ).first()

    student = db.query(Student).filter(
        Student.student_id == submission.student_id
    ).first()

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # 제목
    p.setFont(FONT_NAME_BOLD, 18)
    p.drawString(20 * mm, height - 25 * mm, "채점 결과")

    # 기본 정보
    p.setFont(FONT_NAME, 11)
    p.drawString(20 * mm, height - 38 * mm, f"과제: {assignment.title}")
    p.drawString(20 * mm, height - 46 * mm, f"학생: {student.name if student else 'Unknown'}")
    p.drawString(20 * mm, height - 54 * mm, f"제출일: {submission.submitted_at or '-'}")

    # 점수 (강조)
    p.setFont(FONT_NAME_BOLD, 16)
    percentage = round((submission.total_score / submission.max_score) * 100, 1) if submission.max_score > 0 else 0
    p.drawString(width - 70 * mm, height - 38 * mm, f"점수: {submission.total_score} / {submission.max_score}")
    p.drawString(width - 70 * mm, height - 48 * mm, f"({percentage}%)")

    # 구분선
    p.line(20 * mm, height - 62 * mm, width - 20 * mm, height - 62 * mm)

    # 문제별 결과
    y = height - 75 * mm
    p.setFont(FONT_NAME, 10)

    for answer in submission.answers:
        question = db.query(Question).filter(
            Question.question_id == answer.question_id
        ).first()

        if not question:
            continue

        if y < 50 * mm:
            p.showPage()
            y = height - 30 * mm
            p.setFont(FONT_NAME, 10)

        # 정답 여부 표시
        if answer.is_correct is True:
            status = "O"
            p.setFillColorRGB(0, 0.5, 0)  # 초록색
        elif answer.is_correct is False:
            status = "X"
            p.setFillColorRGB(0.8, 0, 0)  # 빨간색
        else:
            status = "-"
            p.setFillColorRGB(0.5, 0.5, 0.5)  # 회색

        # 문제 번호 + 정답여부
        p.setFont(FONT_NAME_BOLD, 12)
        p.drawString(20 * mm, y, f"[{status}]")
        p.setFillColorRGB(0, 0, 0)  # 검정색으로 복원

        # 문제 내용
        p.setFont(FONT_NAME, 10)
        question_text = question.question_text[:50] + "..." if len(question.question_text) > 50 else question.question_text
        p.drawString(32 * mm, y, f"{question.question_number}. {question_text}")
        y -= 6 * mm

        # 학생 답안
        p.drawString(35 * mm, y, f"학생 답: {answer.student_answer or '-'}")
        y -= 6 * mm

        # 오답일 경우 정답 표시
        if answer.is_correct is False:
            p.setFillColorRGB(0, 0, 0.8)  # 파란색
            p.drawString(35 * mm, y, f"정답: {question.correct_answer}")
            p.setFillColorRGB(0, 0, 0)
            y -= 6 * mm

        # 획득 점수
        p.drawString(width - 40 * mm, y + 12 * mm, f"{answer.points_earned}/{question.points}점")

        y -= 10 * mm

    p.save()
    buffer.seek(0)
    return buffer.getvalue()
