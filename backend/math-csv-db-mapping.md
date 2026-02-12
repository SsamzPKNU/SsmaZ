# math_classification.csv → DB 매핑 문서

> 중학교 수학 유리수/순환소수 단원 CSV 데이터를 DB 스키마에 매핑하기 위한 가이드

## 1. 개요

### CSV 파일 정보
- **파일**: `math_classification.csv`
- **내용**: 중학교 수학 유리수·순환소수 단원 문제
- **규모**: 41개 대문제(problem_id 1~41), 총 200개 소문항 (CSV 201행 = 헤더 1행 + 데이터 200행)
- **컬럼 수**: 5개 (`problem_id`, `sub_id`, `value_display`, `question`, `answer`)

### 매핑 대상 DB 테이블

| 테이블 | 용도 | 핵심 역할 |
|--------|------|-----------|
| **QuestionBank** | 문제 은행 | CSV 문제를 학원별 재사용 가능한 문제 풀로 저장 |
| **Questions** | 과제 내 문항 | 특정 과제(Assignment)에 배정된 개별 문항 |
| **Assignments** | 과제/시험 | 문항들을 묶는 상위 과제 단위 |

### 데이터 흐름

```
CSV → QuestionBank (문제 은행에 등록)
       ↓
    Assignments (과제 생성)
       ↓
    Questions (과제에 문항 배정)
```

---

## 2. CSV 컬럼 → DB 컬럼 매핑표

### 2-1. 직접 매핑

| CSV 컬럼 | QuestionBank | Questions | Assignments | 비고 |
|----------|-------------|-----------|-------------|------|
| `problem_id` | category (일부) | question_number | — | 대문제 번호 (1~41) |
| `sub_id` | — | question_number (세부) | — | 소문항 식별자 |
| `value_display` | question_text (일부) | question_text (일부) | — | 문제에 제시되는 값/식 |
| `question` | question_text (일부), question_type | question_text (일부), question_type_id | title (참고) | 문제 유형/지시사항 |
| `answer` | correct_answer | correct_answer | — | 정답 (`/` 구분 다단계) |

### 2-2. sub_id 변환 규칙

CSV의 `sub_id`는 한글 자음(ㄱ~ㅇ) 또는 숫자(1~8) 형식입니다.

**한글 자음 → 숫자 변환**:

| sub_id | 변환값 | sub_id | 변환값 |
|--------|--------|--------|--------|
| ㄱ | 1 | ㅁ | 5 |
| ㄴ | 2 | ㅂ | 6 |
| ㄷ | 3 | ㅅ | 7 |
| ㄹ | 4 | ㅇ | 8 |

- problem_id 1만 한글 자음(ㄱ~ㅇ) 사용, 나머지는 숫자(1~8)
- DB 저장 시 `question_number`는 `{problem_id}-{변환된 sub_id}` 형식 권장 (예: `1-1`, `5-3`)

### 2-3. question 컬럼 파싱 규칙

`question` 컬럼의 `/` 구분자는 **다단계 지시사항**을 나타냅니다.

| 패턴 | 의미 | 예시 |
|------|------|------|
| `A/B/C/D` | 분류 카테고리 목록 | `자연수/음의정수/정수가아닌유리수/유리수` |
| `A/B` | 2단계 변환 과제 | `소수로나타내기/유한소수·무한소수` |
| `A/B/C` | 3단계 변환 과제 | `소수/순환마디/순환소수표현` |
| `A○/×` | 판별 문제 | `순환소수○/×` |

### 2-4. answer 컬럼 파싱 규칙

`answer` 컬럼의 `/`는 **다단계 정답**을 나타냅니다.

| 패턴 | 의미 | 예시 |
|------|------|------|
| `단일값` | 정답이 하나 | `○`, `7`, `0.25` |
| `A/B` | 2단계 정답 | `0.25/유` (소수 변환 결과 / 유한소수 여부) |
| `A/B/C` | 3단계 정답 | `25/0.2̇5̇` → 순환마디 / 순환소수표현 |
| `A/B/C/D/E/F` | 다단계 풀이 과정 | `100/26.2626…/99x=26/26/99` |

DB 저장 시 `correct_answer`에는 **최종 정답**만 저장하거나, JSON 배열로 전체 과정을 저장할 수 있습니다.

---

## 3. 문제 유형 분류

CSV의 `question` 컬럼 패턴을 기준으로 6가지 유형으로 분류합니다.

| # | 유형명 | problem_id | question 패턴 | DB question_type | 문제 수 |
|---|--------|-----------|---------------|-----------------|---------|
| 1 | 분류형 | 1 | `자연수/음의정수/정수가아닌유리수/유리수` | **CHOICE** | 1 |
| 2 | 판별형 ○/× | 4, 6, 16, 17, 40, 41 | `~○/×` | **SHORT_ANSWER** | 6 |
| 3 | 유한/순환 판별 | 2, 15, 18 | `유한소수/무한소수`, `유한소수여부` | **SHORT_ANSWER** | 3 |
| 4 | 변환/계산형 | 3, 5, 7~14, 19~34, 37 | `소수로나타내기`, `순환마디`, `기약분수` 등 | **SHORT_ANSWER** | 26 |
| 5 | 부등호 비교형 | 35, 36 | `부등호비교` | **SHORT_ANSWER** | 2 |
| 6 | 보기 선택형 | 38, 39 | `보기에서알맞은값`, `유리수가아닌것모두고르기` | **CHOICE** | 3 |

### QuestionType Enum 매핑 요약

| DB Enum | 해당 유형 | 비율 |
|---------|----------|------|
| **CHOICE** | 분류형, 보기 선택형 | 3/41 (7%) |
| **SHORT_ANSWER** | 판별형, 유한/순환 판별, 변환/계산형, 부등호 비교형 | 37/41 (90%) |
| **ESSAY** | 해당 없음 | 0/41 (0%) |

> 대부분의 문제가 SHORT_ANSWER 유형입니다. 수학 연산 결과나 ○/×를 직접 입력하는 형태이기 때문입니다.

---

## 4. 유형별 상세 매핑

### 유형 1: 분류형 (CHOICE)

주어진 값을 여러 카테고리 중에서 분류하는 문제입니다.

**CSV 예시** (problem_id=1, sub_id=ㄷ):
```
problem_id: 1
sub_id: ㄷ
value_display: 2.5
question: 자연수/음의정수/정수가아닌유리수/유리수
answer: 정수가아닌유리수/유리수
```

**DB 변환 (QuestionBank)**:
```json
{
  "question_text": "다음 수를 분류하시오: 2.5",
  "question_type": "CHOICE",
  "options": ["자연수", "음의정수", "정수가아닌유리수", "유리수"],
  "correct_answer": "정수가아닌유리수/유리수",
  "category": "유리수-분류"
}
```

> 이 유형은 복수 정답이 가능합니다 (예: 2.5는 "정수가아닌유리수"이면서 "유리수"). `correct_answer`에 `/`로 구분하여 저장합니다.

---

### 유형 2: 판별형 ○/× (SHORT_ANSWER)

주어진 명제나 조건의 참/거짓을 ○ 또는 ×로 판별하는 문제입니다.

**CSV 예시** (problem_id=4, sub_id=2):
```
problem_id: 4
sub_id: 2
value_display: 0.1010010001…
question: 순환소수○/×
answer: ×
```

**DB 변환 (QuestionBank)**:
```json
{
  "question_text": "다음이 순환소수인지 판별하시오 (○/×): 0.1010010001…",
  "question_type": "SHORT_ANSWER",
  "options": null,
  "correct_answer": "×",
  "category": "순환소수-판별"
}
```

**같은 유형의 다른 예시** (problem_id=6, sub_id=3):
```
value_display: 0.444…=0.4̇4̇
question: 순환소수표현○/×
answer: ×/0.4̇
```
> 오답일 경우 올바른 표현을 함께 제공합니다. `correct_answer`에 `×/0.4̇` 형태로 저장합니다.

---

### 유형 3: 유한/순환 판별 (SHORT_ANSWER)

소수가 유한소수인지 무한소수(순환소수)인지 판별하는 문제입니다.

**CSV 예시** (problem_id=2, sub_id=1):
```
problem_id: 2
sub_id: 1
value_display: 0.5
question: 유한소수/무한소수
answer: 유
```

**DB 변환 (QuestionBank)**:
```json
{
  "question_text": "다음 소수가 유한소수인지 무한소수인지 판별하시오: 0.5",
  "question_type": "SHORT_ANSWER",
  "options": null,
  "correct_answer": "유",
  "category": "소수-판별"
}
```

**CSV 예시** (problem_id=15, sub_id=2):
```
value_display: 1/27=1/3³
question: 분모소인수/유한소수여부
answer: 3/없다
```

**DB 변환**: `correct_answer`에 `3/없다` (분모 소인수: 3, 유한소수 여부: 없다)

---

### 유형 4: 변환/계산형 (SHORT_ANSWER)

소수 변환, 순환마디 찾기, 기약분수 변환 등 수학적 계산을 수행하는 문제입니다.

**CSV 예시 — 순환마디/순환소수표현** (problem_id=5, sub_id=4):
```
problem_id: 5
sub_id: 4
value_display: 5.714081408…
question: 순환마디/순환소수표현
answer: 1408/5.71̇408̇
```

**DB 변환 (QuestionBank)**:
```json
{
  "question_text": "다음 순환소수의 순환마디와 순환소수 표현을 구하시오: 5.714081408…",
  "question_type": "SHORT_ANSWER",
  "options": null,
  "correct_answer": "1408/5.71̇408̇",
  "category": "순환소수-변환"
}
```

**CSV 예시 — 순환소수→기약분수** (problem_id=23, sub_id=3):
```
value_display: 0.4̇32̇
question: 순환소수→기약분수
answer: 16/37
```

**DB 변환**: `correct_answer` = `16/37`

**CSV 예시 — 10의 거듭제곱 변환** (problem_id=12, sub_id=4):
```
value_display: 21/(2²×3×5³)
question: 10의거듭제곱으로유한소수변환
answer: 7/(2²×5³)/2/14/1000/0.014
```

**DB 변환**: 다단계 풀이 과정이 포함됨. `correct_answer`에 최종 정답 `0.014`을 저장하거나, 전체 과정을 JSON으로 저장.

```json
{
  "correct_answer": "0.014",
  "category": "유한소수-변환"
}
```

**CSV 예시 — 순환소수→분수 공식 과정** (problem_id=21, sub_id=1):
```
value_display: 0.2̇6̇
question: 순환소수→기약분수과정
answer: 100/26.2626…/99x=26/26/99
```

**DB 변환**: 풀이 과정 단계가 `/`로 구분됨.
```json
{
  "correct_answer": "26/99",
  "category": "순환소수-분수변환"
}
```

---

### 유형 5: 부등호 비교형 (SHORT_ANSWER)

두 수의 크기를 비교하여 부등호(`<`, `>`, `=`)를 입력하는 문제입니다.

**CSV 예시** (problem_id=35, sub_id=2):
```
problem_id: 35
sub_id: 2
value_display: 0.54̇ □ 0.5̇4̇
question: 부등호비교
answer: <
```

**DB 변환 (QuestionBank)**:
```json
{
  "question_text": "두 수의 크기를 비교하시오: 0.54̇ □ 0.5̇4̇",
  "question_type": "SHORT_ANSWER",
  "options": null,
  "correct_answer": "<",
  "category": "순환소수-비교"
}
```

---

### 유형 6: 보기 선택형 (CHOICE)

주어진 보기에서 조건에 맞는 값을 선택하는 문제입니다.

**CSV 예시** (problem_id=38, sub_id=1):
```
problem_id: 38
sub_id: 1
value_display: 0.4̇26̇=426×□
question: 보기에서알맞은값
answer: ㅈ(999)/1/999
```

**DB 변환 (QuestionBank)**:
```json
{
  "question_text": "보기에서 알맞은 값을 고르시오: 0.4̇26̇ = 426 × □",
  "question_type": "CHOICE",
  "options": ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", "ㅈ"],
  "correct_answer": "ㅈ(999)",
  "category": "순환소수-보기선택"
}
```

**CSV 예시** (problem_id=39, sub_id=1):
```
value_display: ㄱ0/ㄴ0.101001000…/ㄷ-23÷3/ㄹ1.2̇8̇/ㅁ-0.85/ㅂπ
question: 유리수가아닌것모두고르기
answer: ㄴ,ㅂ
```

**DB 변환**:
```json
{
  "question_text": "다음 중 유리수가 아닌 것을 모두 고르시오: ㄱ) 0  ㄴ) 0.101001000…  ㄷ) -23÷3  ㄹ) 1.2̇8̇  ㅁ) -0.85  ㅂ) π",
  "question_type": "CHOICE",
  "options": ["ㄱ 0", "ㄴ 0.101001000…", "ㄷ -23÷3", "ㄹ 1.2̇8̇", "ㅁ -0.85", "ㅂ π"],
  "correct_answer": "ㄴ,ㅂ",
  "category": "유리수-보기선택"
}
```

---

## 5. 전체 데이터 목록

41개 problem_id별 소문항 수, question 유형, DB question_type 매핑입니다.

| problem_id | 소문항 수 | sub_id 형식 | question 유형 | DB question_type | category (권장) |
|:----------:|:---------:|:-----------:|--------------|:----------------:|----------------|
| 1 | 8 | ㄱ~ㅇ | 자연수/음의정수/정수가아닌유리수/유리수 | CHOICE | 유리수-분류 |
| 2 | 4 | 1~4 | 유한소수/무한소수 | SHORT_ANSWER | 소수-판별 |
| 3 | 6 | 1~6 | 소수로나타내기/유한소수·무한소수 | SHORT_ANSWER | 소수-변환 |
| 4 | 8 | 1~8 | 순환소수○/× | SHORT_ANSWER | 순환소수-판별 |
| 5 | 8 | 1~8 | 순환마디/순환소수표현 | SHORT_ANSWER | 순환소수-변환 |
| 6 | 6 | 1~6 | 순환소수표현○/× | SHORT_ANSWER | 순환소수표현-판별 |
| 7 | 4 | 1~4 | 소수/순환마디/순환소수표현 | SHORT_ANSWER | 순환소수-변환 |
| 8 | 4 | 1~4 | 소수점아래50번째자리숫자 | SHORT_ANSWER | 순환소수-자릿수 |
| 9 | 3 | 1~3 | 순환소수로나타내기/순환마디숫자개수/소수점아래n번째자리 | SHORT_ANSWER | 순환소수-자릿수 |
| 10 | 3 | 1~3 | 순환소수로나타내기/순환마디숫자개수/소수점아래n번째자리 | SHORT_ANSWER | 순환소수-자릿수 |
| 11 | 5 | 1~5 | 기약분수/분모소인수 | SHORT_ANSWER | 유한소수-기약분수 |
| 12 | 4 | 1~4 | 10의거듭제곱으로유한소수변환 | SHORT_ANSWER | 유한소수-변환 |
| 13 | 4 | 1~4 | 10의거듭제곱유한소수변환 | SHORT_ANSWER | 유한소수-변환 |
| 14 | 5 | 1~5 | 유한소수로나타내기 | SHORT_ANSWER | 유한소수-변환 |
| 15 | 5 | 1~5 | 분모소인수/유한소수여부 | SHORT_ANSWER | 유한소수-판별 |
| 16 | 5 | 1~5 | 유한소수○/× | SHORT_ANSWER | 유한소수-판별 |
| 17 | 6 | 1~6 | 순환소수로만나타낼수있는것○/× | SHORT_ANSWER | 순환소수-판별 |
| 18 | 6 | 1~6 | 유한소수유/순환소수순 | SHORT_ANSWER | 소수-판별 |
| 19 | 4 | 1~4 | 유한소수만들기위해곱할가장작은자연수 | SHORT_ANSWER | 유한소수-계산 |
| 20 | 4 | 1~4 | 유한소수만들기위해곱할가장작은자연수 | SHORT_ANSWER | 유한소수-계산 |
| 21 | 4 | 1~4 | 순환소수→기약분수과정 | SHORT_ANSWER | 순환소수-분수변환 |
| 22 | 6 | 1~6 | 분수변환에필요한식 | SHORT_ANSWER | 순환소수-분수변환 |
| 23 | 6 | 1~6 | 순환소수→기약분수 | SHORT_ANSWER | 순환소수-분수변환 |
| 24 | 4 | 1~4 | 순환소수→기약분수과정 | SHORT_ANSWER | 순환소수-분수변환 |
| 25 | 6 | 1~6 | 분수변환에필요한식 | SHORT_ANSWER | 순환소수-분수변환 |
| 26 | 6 | 1~6 | 순환소수→기약분수 | SHORT_ANSWER | 순환소수-분수변환 |
| 27 | 4 | 1~4 | 순환소수→분수공식과정 | SHORT_ANSWER | 순환소수-분수변환 |
| 28 | 5 | 1~5 | 순환소수→기약분수 | SHORT_ANSWER | 순환소수-분수변환 |
| 29 | 4 | 1~4 | 순환소수→분수공식과정 | SHORT_ANSWER | 순환소수-분수변환 |
| 30 | 5 | 1~5 | 순환소수→기약분수 | SHORT_ANSWER | 순환소수-분수변환 |
| 31 | 3 | 1~3 | 순환소수→분수공식과정 | SHORT_ANSWER | 순환소수-분수변환 |
| 32 | 5 | 1~5 | 순환소수→기약분수 | SHORT_ANSWER | 순환소수-분수변환 |
| 33 | 3 | 1~3 | 순환소수→분수공식과정 | SHORT_ANSWER | 순환소수-분수변환 |
| 34 | 5 | 1~5 | 순환소수→기약분수 | SHORT_ANSWER | 순환소수-분수변환 |
| 35 | 5 | 1~5 | 부등호비교 | SHORT_ANSWER | 순환소수-비교 |
| 36 | 5 | 1~5 | 부등호비교 | SHORT_ANSWER | 순환소수-비교 |
| 37 | 5 | 1~5 | 계산 | SHORT_ANSWER | 순환소수-계산 |
| 38 | 4 | 1~4 | 보기에서알맞은값 | CHOICE | 순환소수-보기선택 |
| 39 | 1 | 1 | 유리수가아닌것모두고르기 | CHOICE | 유리수-보기선택 |
| 40 | 5 | 1~5 | x=3.4252525…설명○/× | SHORT_ANSWER | 순환소수-판별 |
| 41 | 7 | 1~7 | 설명○/× | SHORT_ANSWER | 유리수-종합판별 |

**합계**: 41개 대문제, 200개 소문항

---

## 6. Import 시 고려사항

### 6-1. CSV에 없는 필드 처리

| DB 컬럼 | 테이블 | 기본값 제안 | 비고 |
|---------|--------|-----------|------|
| `academy_id` | QuestionBank | import 시 지정 필수 | 학원별로 다르므로 import 파라미터로 전달 |
| `difficulty` | QuestionBank, Questions | `MEDIUM` | 기본값으로 설정 후, 추후 선생님이 조정 |
| `points` | Questions | `1.0` (소문항당) | problem_id당 소문항 수에 따라 배점 조정 가능 |
| `usage_count` | QuestionBank | `0` | 신규 등록이므로 0으로 초기화 |
| `assignment_id` | Questions | import 시 지정 | Assignment 먼저 생성 후 FK 연결 |
| `teacher_id` | Assignments | import 시 지정 | 출제 선생님 ID |
| `class_id` | Assignments | import 시 지정 | 대상 반 ID |
| `assignment_type` | Assignments | `NORMAL` | 일반 과제로 등록, 필요 시 `QUIZ` 등으로 변경 |
| `due_date` | Assignments | import 시 지정 | 과제 마감일 |
| `options` | QuestionBank, Questions | 유형에 따라 다름 | CHOICE → JSON 배열, SHORT_ANSWER → `null` |

### 6-2. question_text 생성 규칙

CSV의 `value_display`와 `question`을 조합하여 `question_text`를 생성합니다.

```
question_text = "{question에서 파생한 지시문}: {value_display}"
```

**예시**:
| question | value_display | 생성된 question_text |
|----------|--------------|---------------------|
| `순환소수○/×` | `0.121212…` | `다음이 순환소수인지 판별하시오 (○/×): 0.121212…` |
| `유한소수/무한소수` | `0.5` | `다음 소수가 유한소수인지 무한소수인지 판별하시오: 0.5` |
| `순환마디/순환소수표현` | `0.252525…` | `다음 순환소수의 순환마디와 순환소수 표현을 구하시오: 0.252525…` |
| `부등호비교` | `0.54̇ □ 0.5̇4̇` | `두 수의 크기를 비교하시오: 0.54̇ □ 0.5̇4̇` |
| `순환소수→기약분수` | `0.6̇` | `다음 순환소수를 기약분수로 나타내시오: 0.6̇` |

### 6-3. correct_answer 저장 전략

| 전략 | 설명 | 예시 |
|------|------|------|
| **최종 정답만** | `/`로 구분된 마지막 값만 저장 | `0.25/유` → `유` |
| **전체 과정** | `/`로 구분된 전체를 그대로 저장 | `100/26.2626…/99x=26/26/99` |
| **JSON 배열** | 단계별로 분리하여 JSON 저장 | `["100", "26.2626…", "99x=26", "26/99"]` |

**권장**: 단순 정답 문제는 최종 정답만, 풀이 과정이 중요한 문제(problem_id 12, 13, 21, 24, 27, 29, 31, 33)는 전체 과정을 저장합니다.

### 6-4. Import 순서

```
1. QuestionBank에 200개 문항 등록
   └─ academy_id 지정 필수
   └─ category는 섹션 5의 권장값 사용

2. Assignments 생성 (과제 단위)
   └─ class_id, teacher_id, due_date 지정
   └─ assignment_type: NORMAL (기본)
   └─ title: "유리수와 순환소수" 등

3. Questions에 문항 배정
   └─ assignment_id FK 연결
   └─ QuestionBank에서 복제하여 등록
   └─ question_number: problem_id 기준 순번

4. (선택) difficulty 일괄 업데이트
   └─ problem_id 1~6: EASY (기초 개념)
   └─ problem_id 7~20: MEDIUM (변환/계산)
   └─ problem_id 21~41: HARD (심화 문제)
```

### 6-5. 특수 문자 처리

CSV에 포함된 수학 특수 표기에 주의가 필요합니다.

| 표기 | 의미 | 저장 방법 |
|------|------|----------|
| `0.2̇5̇` | 순환소수 (2와 5 위에 점) | UTF-8 결합 문자 그대로 저장 |
| `2²×5²` | 거듭제곱 | UTF-8 위첨자 그대로 저장 |
| `…` | 무한 반복 | 말줄임표(U+2026) 사용 |
| `□` | 빈칸 (부등호 입력) | U+25A1 그대로 저장 |
