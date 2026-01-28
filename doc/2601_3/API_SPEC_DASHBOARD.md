# SSamZ Admin API - 대시보드 명세서

## 📊 대시보드 API

### 2-1. 관리자 대시보드 전체 통계


#### Endpoint
```
GET /api/admin/dashboard
```

#### Description
전체 수강생 수, 강사 수, 이번 달 예상 매출, 현재 미납 금액 등 학원 운영 핵심 지표를 조회합니다.

#### Headers
```
Authorization: Bearer {access_token}
```

#### Response (200 OK)
```json
{
  "summary": {
    "total_students": 150,
    "total_teachers": 8,
    "monthly_revenue": 45000000,
    "unpaid_amount": 2500000
  },
  "attendance_rate": {
    "today": 95.5,
    "yesterday": 94.0
  },
  "recent_activities": [
    {
      "id": 1,
      "type": "payment",
      "message": "김철수 학생 1월 수강료 납부",
      "time": "10:30 AM"
    },
    {
      "id": 2,
      "type": "join",
      "message": "신규 학생(이민호) 등록",
      "time": "11:00 AM"
    }
  ],
  "revenue_trend": [
    { "month": "2025-08", "amount": 42000000 },
    { "month": "2025-09", "amount": 43500000 },
    { "month": "2025-10", "amount": 44000000 },
    { "month": "2025-11", "amount": 44500000 },
    { "month": "2025-12", "amount": 43000000 },
    { "month": "2026-01", "amount": 45000000 }
  ]
}
```

#### Response Fields

| 필드 | 타입 | 설명 |
|------|------|------|
| **summary** | Object | 전체 요약 통계 |
| summary.total_students | Integer | 전체 수강생 수 (재원 중인 학생) |
| summary.total_teachers | Integer | 전체 강사 수 (TEACHER 역할) |
| summary.monthly_revenue | Integer | 이번 달 예상 매출 (원) |
| summary.unpaid_amount | Integer | 현재 미납 총액 (원) |
| **attendance_rate** | Object | 출석률 통계 |
| attendance_rate.today | Float | 오늘 출석률 (%) |
| attendance_rate.yesterday | Float | 어제 출석률 (%) |
| **recent_activities** | Array | 최근 활동 내역 목록 |
| recent_activities[].id | Integer | 활동 ID |
| recent_activities[].type | String | 활동 타입 (`payment`, `join`, `attendance`) |
| recent_activities[].message | String | 활동 메시지 |
| recent_activities[].time | String | 활동 시간 |
| **revenue_trend** | Array | 최근 6개월 매출 추이 |
| revenue_trend[].month | String | 년-월 (YYYY-MM) |
| revenue_trend[].amount | Integer | 매출액 (원) |

---

## 📝 프론트엔드 사용 예시

### React 예시

```javascript
async function getDashboardData() {
  const token = localStorage.getItem('access_token');
  
  try {
    const response = await fetch('http://localhost:8000/api/admin/dashboard', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error('대시보드 데이터 조회 실패');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('에러:', error);
    throw error;
  }
}

// 사용
const dashboardData = await getDashboardData();
console.log('전체 학생 수:', dashboardData.summary.total_students);
console.log('오늘 출석률:', dashboardData.attendance_rate.today);
```

### React Component 예시

```jsx
import { useState, useEffect } from 'react';

function AdminDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getDashboardData();
        setDashboard(data);
      } catch (error) {
        console.error('대시보드 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>로딩 중...</div>;
  if (!dashboard) return <div>데이터를 불러올 수 없습니다.</div>;

  return (
    <div className="dashboard">
      {/* 요약 통계 */}
      <div className="summary">
        <div className="stat-card">
          <h3>전체 수강생</h3>
          <p>{dashboard.summary.total_students}명</p>
        </div>
        <div className="stat-card">
          <h3>전체 강사</h3>
          <p>{dashboard.summary.total_teachers}명</p>
        </div>
        <div className="stat-card">
          <h3>이번 달 매출</h3>
          <p>{dashboard.summary.monthly_revenue.toLocaleString()}원</p>
        </div>
        <div className="stat-card">
          <h3>미납 금액</h3>
          <p>{dashboard.summary.unpaid_amount.toLocaleString()}원</p>
        </div>
      </div>

      {/* 출석률 */}
      <div className="attendance">
        <h2>출석률</h2>
        <p>오늘: {dashboard.attendance_rate.today}%</p>
        <p>어제: {dashboard.attendance_rate.yesterday}%</p>
      </div>

      {/* 최근 활동 */}
      <div className="activities">
        <h2>최근 활동</h2>
        <ul>
          {dashboard.recent_activities.map(activity => (
            <li key={activity.id}>
              <span className={`type-${activity.type}`}>{activity.type}</span>
              <span>{activity.message}</span>
              <span className="time">{activity.time}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* 매출 추이 차트 */}
      <div className="revenue-chart">
        <h2>매출 추이 (최근 6개월)</h2>
        {/* Chart.js나 다른 차트 라이브러리 사용 */}
        <ul>
          {dashboard.revenue_trend.map(trend => (
            <li key={trend.month}>
              {trend.month}: {trend.amount.toLocaleString()}원
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

---

## ⚠️ 주의사항

### 1. 매출 데이터 (TODO)
현재 버전에서는 **Payment 테이블이 구현되지 않아** 매출 관련 데이터는 더미 데이터로 제공됩니다:
- `monthly_revenue`: 학생 수 × 300,000원으로 계산
- `unpaid_amount`: 학생 수 × 0.1 × 250,000원으로 계산
- `revenue_trend`: 더미 데이터 (약간의 변동 추가)

**Payment 테이블 구현 후** 실제 매출 데이터로 변경될 예정입니다.

### 2. 권한 확인
현재는 모든 인증된 사용자가 대시보드에 접근할 수 있습니다.
**ADMIN 권한만 접근하도록 제한**하려면 코드의 TODO 부분을 활성화하세요.

### 3. 출석률 계산
- 재원 중인 학생만 대상으로 계산
- 출석, 지각은 출석으로 간주
- 결석, 조퇴는 미출석으로 간주

---

## 🎯 활동 타입 (Activity Types)

| 타입 | 설명 | 예시 메시지 |
|------|------|------------|
| `payment` | 수강료 납부 | "김철수 학생 1월 수강료 납부" |
| `join` | 신규 학생 등록 | "신규 학생(이민호) 등록" |
| `attendance` | 등원/하원 기록 | "김철수 학생 등원" |

---

## 🧪 테스트 방법

### curl 테스트
```bash
# 먼저 로그인
TOKEN=$(curl -X POST "http://localhost:8000/auth/login-mobile" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}' \
  | jq -r '.access_token')

# 대시보드 조회
curl -X GET "http://localhost:8000/api/admin/dashboard" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq
```

### Swagger UI
```
http://localhost:8000/docs
```
1. `/auth/login-mobile`로 로그인하여 토큰 획득
2. 우측 상단 "Authorize" 버튼 클릭
3. Bearer 토큰 입력
4. `/api/admin/dashboard` 엔드포인트 테스트

---

## 📈 차트 라이브러리 추천

### Chart.js (React)
```bash
npm install chart.js react-chartjs-2
```

```jsx
import { Line } from 'react-chartjs-2';

const RevenueChart = ({ revenue_trend }) => {
  const data = {
    labels: revenue_trend.map(t => t.month),
    datasets: [{
      label: '매출',
      data: revenue_trend.map(t => t.amount),
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  };

  return <Line data={data} />;
};
```

### Recharts (React)
```bash
npm install recharts
```

```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const RevenueChart = ({ revenue_trend }) => (
  <LineChart width={600} height={300} data={revenue_trend}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="month" />
    <YAxis />
    <Tooltip />
    <Line type="monotone" dataKey="amount" stroke="#8884d8" />
  </LineChart>
);
```

---

## 📚 관련 문서

- 인증 API: `API_SPEC_LOGIN.md`
- 프론트엔드 가이드: `FRONTEND_GUIDE.md`
- Quick Reference: `QUICK_REFERENCE.md`

---

## 💡 향후 개선 사항

1. **Payment 테이블 구현** - 실제 매출 데이터 제공
2. **실시간 업데이트** - WebSocket을 통한 실시간 통계 업데이트
3. **기간별 조회** - 원하는 기간의 통계 조회 기능
4. **상세 필터링** - 반별, 강사별 등 상세 통계 제공
5. **알림 설정** - 미납 임박, 출석률 하락 등 알림 기능

---

## 문의

API 관련 문의나 이슈가 있으면 백엔드 팀에 문의해주세요.
