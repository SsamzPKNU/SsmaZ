# 출석 통계 API 명세서

> 2026-02-12 추가

## 엔드포인트

```
GET /attendance/stats?start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}
```

| 항목 | 내용 |
|------|------|
| **Method** | GET |
| **인증** | 필수 (쿠키 또는 Bearer 토큰) |
| **권한** | 모든 로그인 사용자 |

## Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `start_date` | `string` (YYYY-MM-DD) | O | 조회 시작일 |
| `end_date` | `string` (YYYY-MM-DD) | O | 조회 종료일 |

## 응답 (200 OK)

```json
{
  "period": {
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
  },
  "summary": {
    "total": 100,
    "present": 80,
    "late": 10,
    "absent": 5,
    "early": 5
  },
  "daily_stats": [
    {
      "date": "2026-01-01",
      "total": 20,
      "present": 15,
      "late": 3,
      "absent": 1,
      "early": 1
    }
  ],
  "class_stats": [
    {
      "class_id": 1,
      "class_name": "A반",
      "total_students": 10,
      "total_records": 50,
      "present": 40,
      "late": 5,
      "absent": 3,
      "early": 2,
      "attendance_rate": 80.0
    }
  ]
}
```

## 응답 필드 설명

### period

| 필드 | 타입 | 설명 |
|------|------|------|
| `start_date` | `string` | 조회 시작일 |
| `end_date` | `string` | 조회 종료일 |

### summary

기간 내 전체 출석 상태 집계.

| 필드 | 타입 | 설명 |
|------|------|------|
| `total` | `int` | 전체 출결 기록 수 |
| `present` | `int` | 출석 수 |
| `late` | `int` | 지각 수 |
| `absent` | `int` | 결석 수 |
| `early` | `int` | 조퇴 수 |

### daily_stats

날짜별 출석 통계 배열. 차트(월별/일별 추이) 렌더링에 사용.

| 필드 | 타입 | 설명 |
|------|------|------|
| `date` | `string` | 날짜 (YYYY-MM-DD) |
| `total` | `int` | 해당일 전체 기록 수 |
| `present` | `int` | 출석 |
| `late` | `int` | 지각 |
| `absent` | `int` | 결석 |
| `early` | `int` | 조퇴 |

> 출결 기록이 없는 날짜는 배열에 포함되지 않습니다. 프론트에서 빈 날짜는 0으로 채워주세요.

### class_stats

반별 출석 통계 배열.

| 필드 | 타입 | 설명 |
|------|------|------|
| `class_id` | `int \| null` | 반 ID (미배정 학생은 null) |
| `class_name` | `string \| null` | 반 이름 |
| `total_students` | `int` | 해당 반 학생 수 (기간 내 출결 기록이 있는) |
| `total_records` | `int` | 전체 출결 기록 수 |
| `present` | `int` | 출석 수 |
| `late` | `int` | 지각 수 |
| `absent` | `int` | 결석 수 |
| `early` | `int` | 조퇴 수 |
| `attendance_rate` | `float` | 출석률 (%, 소수점 1자리) = present / total_records * 100 |

## 에러 응답

| 상태 코드 | 설명 |
|-----------|------|
| 400 | `start_date`가 `end_date`보다 이후인 경우 |
| 401 | 인증 실패 |

## 프론트엔드 사용 예시

```typescript
// 이번 달 출석 통계 조회
const now = new Date();
const startDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
const endDate = now.toISOString().split('T')[0];

const res = await fetch(
  `/attendance/stats?start_date=${startDate}&end_date=${endDate}`,
  { credentials: 'include' }
);
const data = await res.json();

// data.summary    → 출석 상태 분포표 (도넛 차트)
// data.daily_stats → 일별 출석 추이 (막대/라인 차트)
// data.class_stats → 반별 출석률 (테이블 또는 바 차트)
```
