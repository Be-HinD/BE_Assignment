# 📌 포팅 매뉴얼 - 시험 일정 예약 시스템

## 🏷️ 개요 (Introduction)

BE 개발자 과제 관련 문서입니다.

<br>

## ⚙️ 디렉토리 구조

```bash
BE/
├── app/
│   ├── api/ # API 엔드포인트
│   │   ├── main.py
│   │   └── routes/
│   │       ├── admin
│   │           ├── admin_reservation.py
│   │       └── user
│   │           ├── reservation.py
│   │           ├── token.py
│   │           ├── users.py
│   ├── core/ # 애플리케이션의 설정
│   │   ├── config.py
│   │   ├── exceptions.py.py
│   │   └── security.py
│   ├── database/ # 데이터베이스 관련 코드
│   │   ├── base.py
│   │   └── dependencies.py
│   │   └── session.py
│   ├── models/ # 데이터베이스 모델 (ORM)
│   │   └── exam_schedule.py
│   │   └── reservation.py
│   │   └── user.py
│   └── schemas/ # 데이터 검증 및 API 응답 모델
│       ├── reservation_schema.py
│       └── user_schema.py
├── .env  # 환경변수 파일 (DATABASE_URL 등)
├── main.py
├── requirements.txt  # 프로젝트 의존성 목록
└── README.md

```

<br>

# 🚀 FastAPI 프로젝트 실행 가이드

## ✅ 1. 서버 환경

| 항목        | 버전                    |
| ----------- | ----------------------- |
| OS          | Windows 11              |
| DBMS        | PostgreSQL 15.12        |
| Framework   | FastAPI 0.103.2         |
| Language    | Python 3.7.9            |
| Editor      | VSCode                  |
| 의존성 관리 | `requirements.txt` 참조 |

---

## ✅ 2. 프로젝트 실행 방법

### 📌 1) 프로젝트 루트 경로 이동

```bash
cd BE
```

### 📌 2) 가상 환경 생성 및 활성화

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

💡 Mac/Linux의 경우

```bash
source venv/bin/activate
```

### 📌 3) 프로젝트 의존성 설치

```bash
pip install -r requirements.txt
```

### 📌 4) 환경 변수 파일 (.env) 설정

> 첨부한 .env파일을 루트 경로에 넣고, DB 접속 정보 및 환경 설정을 추가해야 합니다.

💡 .env 파일이 없는 경우 DB 연결 오류가 발생할 수 있음.

### 📌 6) 서버 실행

```bash
uvicorn app.main:app --reload
```

<br>

# 📝 테스트 및 검증 방법 (Testing & Verification)

## ✅ 1. API 테스트 방법

### 📌 1) Swagger UI (자동 API 문서)

FastAPI는 Swagger UI를 기본 제공하여, API를 쉽게 테스트할 수 있습니다.

📍 Swagger UI 접속: <br>
👉 http://127.0.0.1:8000/docs

📍 Redoc 접속: <br>
👉 http://127.0.0.1:8000/redoc

### 📌 2) Postman으로 API 테스트

원할한 Postman 테스트를 위해 관련 JSON파일 첨부하였으니 import하여 참고바랍니다.

```bash
BE/exec/postman/BE_Assignment.postman_collection.json
```

## ✅ 2. 테스트 참고사항

> 엔드포인트에 대한 접근 권한 처리를 JWT 토큰을 통해 진행했습니다. API 테스트에 문제가 없도록 다음을 참고해주시면 감사하겠습니다.

### 📌 1) 유저 등록 (/v1/users/register)

- RequestBody에 다음을 참고하여 유저를 등록해주세요.

```bash
{
  "username": "홍길동",
  "email": "aa@naver.com",
  "password": "1q2w3e4r",
  "role": "user" //or admin
}
```

### 📌 2) 토큰 발급 (/v1/token)

- 모든 엔드포인트 요청에 토큰이 필요합니다. 다음 API를 통해 토큰 발급 후 <b> Authorization Bearer {Token} </b>을 헤더에 넣고 요청해주세요.

```bash
url : http://localhost:8000/v1/token
```

```bash
form-data 방식으로 BODY에 보내주세요.
username:value
password:value
```
