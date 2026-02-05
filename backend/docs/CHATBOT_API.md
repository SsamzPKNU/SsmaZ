# Chatbot API Reference

Student Frontend 팀을 위한 FAQ 챗봇 API 문서입니다.

## API 엔드포인트

### POST /api/chat

FAQ 챗봇에 질문을 전송하고 실시간 스트리밍 응답을 받습니다.

**Request:**
```json
{
  "question": "수업료는 얼마인가요?"
}
```

**Response:**
- Content-Type: `text/event-stream`
- SSE(Server-Sent Events) 형식으로 실시간 스트리밍

**Response Headers:**
```
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

**에러 응답:**

| HTTP Status | error_code | 설명 |
|-------------|------------|------|
| 400 | `EMPTY_QUESTION` | 질문이 비어있음 |
| 503 | `CHROMADB_CONNECTION_ERROR` | ChromaDB 연결 실패 |
| 503 | `OLLAMA_CONNECTION_ERROR` | Ollama 연결 실패 |

---

### GET /api/chat/health

챗봇 서비스 상태를 확인합니다.

**Response:**
```json
{
  "status": "healthy",
  "chromadb_connected": true,
  "ollama_connected": true,
  "model_name": "llama31:latest"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| status | string | `healthy` 또는 `unhealthy` |
| chromadb_connected | boolean | ChromaDB 연결 상태 |
| ollama_connected | boolean | Ollama 연결 상태 |
| model_name | string | 사용 중인 LLM 모델명 |

---

## 에러 응답 형식

모든 에러는 아래 형식으로 반환됩니다:

```json
{
  "detail": "에러 메시지",
  "error_code": "에러코드"
}
```

---

## FAQ 데이터 (총 21개)

| 카테고리 | 개수 | ID 범위 |
|---------|------|---------|
| 수업료/결제 | 4 | `fee_01` ~ `fee_04` |
| 수업/커리큘럼 | 5 | `class_01` ~ `class_05` |
| 출결/등하원 | 3 | `attend_01` ~ `attend_03` |
| 상담/문의 | 3 | `consult_01` ~ `consult_03` |
| 시험/성적 | 2 | `test_01` ~ `test_02` |
| 기타 | 3 | `etc_01` ~ `etc_03` |

### FAQ 질문 목록

**수업료/결제**
- 수업료는 얼마인가요?
- 수업료 납부 방법은 어떻게 되나요?
- 형제 할인이 있나요?
- 환불 규정이 어떻게 되나요?

**수업/커리큘럼**
- 수업 시간은 어떻게 되나요?
- 한 반에 몇 명이 수업하나요?
- 보강은 어떻게 진행되나요?
- 교재는 어떤 것을 사용하나요?
- 온라인 수업도 가능한가요?

**출결/등하원**
- 등하원 알림을 받을 수 있나요?
- 결석 연락은 어떻게 하나요?
- 셔틀버스가 있나요?

**상담/문의**
- 상담 예약은 어떻게 하나요?
- 학부모 상담은 얼마나 자주 하나요?
- 학원 운영 시간이 어떻게 되나요?

**시험/성적**
- 모의고사나 테스트를 보나요?
- 성적표는 어떻게 받아보나요?

**기타**
- 방학 특강이 있나요?
- 학원에서 간식이 제공되나요?
- 학원 위치가 어디인가요?

---

## Frontend 구현 예시

### JavaScript (fetch + EventSource)

```javascript
async function sendChatMessage(question) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail.error_code || 'UNKNOWN_ERROR');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value);
    // 스트리밍 텍스트 처리
    console.log(text);
  }
}
```

### React Hook 예시

```typescript
const [response, setResponse] = useState('');
const [isLoading, setIsLoading] = useState(false);

const sendMessage = async (question: string) => {
  setIsLoading(true);
  setResponse('');

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    while (reader) {
      const { done, value } = await reader.read();
      if (done) break;
      setResponse(prev => prev + decoder.decode(value));
    }
  } finally {
    setIsLoading(false);
  }
};
```
