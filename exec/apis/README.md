# 📌 사용자 등록 API (Register User)

## 1️⃣ 설명

- 새로운 사용자를 등록하는 API입니다.
- 이메일이 이미 존재하는 경우, **400 Bad Request** 오류를 반환합니다.
- 비밀번호는 해싱(`bcrypt`) 후 저장됩니다.

---

## 2️⃣ 요청 형식 (Request)

### **📌 Method & URL**

```
POST /v1/users/register
```

### **📌 Body (JSON)**

| 필드명   | 타입   | 필수 여부 | 설명                         |
| -------- | ------ | --------- | ---------------------------- |
| username | string | ✅ 필수   | 사용자의 닉네임              |
| email    | string | ✅ 필수   | 사용자의 이메일              |
| password | string | ✅ 필수   | 사용자의 비밀번호            |
| role     | string | ❌ 선택   | 사용자의 역할 (기본: `user`) |

#### ✅ **예시**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword",
  "role": "user"
}
```

## 3️⃣ 응답 형식 (Response)

### 📌 성공 응답 (201 Created)

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "created_at": "2025-03-19T12:34:56.789Z"
}
```

<br>

# 📌 사용자 로그인 및 토큰 발급 API (Login for Access Token)

## 1️⃣ 설명

- 사용자가 이메일과 비밀번호를 입력하여 로그인하면, **JWT 액세스 토큰**을 발급하는 API입니다.
- 사용자가 존재하지 않거나 비밀번호가 틀릴 경우 **400 Bad Request** 오류를 반환합니다.
- 발급된 토큰은 인증이 필요한 API 호출 시 사용됩니다.

---

## 2️⃣ 요청 형식 (Request)

### **📌 Method & URL**

POST /v1/token

### **📌 Body (Form-Data)**

> ⚠️ **이 API는 `application/x-www-form-urlencoded` 형식으로 요청해야 합니다.**

| 필드명   | 타입   | 필수 여부 | 설명                                                 |
| -------- | ------ | --------- | ---------------------------------------------------- |
| username | string | ✅ 필수   | 사용자의 이메일 (OAuth2 표준에 따라 `username` 사용) |
| password | string | ✅ 필수   | 사용자의 비밀번호                                    |

#### ✅ **예시 (x-www-form-urlencoded)**

```
username=john@example.com
password=securepassword
```

---

## 3️⃣ 응답 형식 (Response)

### 📌 성공 응답 (200 OK)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}
```

## 4️⃣ 참고

- OAuth2PasswordRequestForm을 사용하기 때문에, 요청을 JSON이 아닌 x-www-form-urlencoded 형식으로 전송해야 합니다.

<br>

# 📌 [사용자] 예약 조회 API (Get User Reservations)

## 1️⃣ 설명

- 현재 로그인한 사용자의 예약 목록을 조회하는 API입니다.
- 예약은 **예약 그룹별로 묶어서 반환**됩니다.
- 날짜, 승인 여부, 과거/미래 필터링이 가능합니다.

---

## 2️⃣ 요청 형식 (Request)

### **📌 Method & URL**

```
GET /v1/users
```

### **📌 Query Parameters**

| 필드명       | 타입   | 필수 여부 | 설명                                                  |
| ------------ | ------ | --------- | ----------------------------------------------------- |
| date         | string | ❌ 선택   | 특정 날짜(YYYY-MM-DD) 기준으로 필터링                 |
| is_confirmed | bool   | ❌ 선택   | 승인 여부(`true` 또는 `false`) 필터링                 |
| past         | bool   | ❌ 선택   | `true` = 과거 예약만 조회, `false` = 미래 예약만 조회 |

#### ✅ **예시**

```json
GET /?date=2025-03-19&is_confirmed=true&past=false
```

---

## 3️⃣ 응답 형식 (Response)

### 📌 성공 응답 (200 OK)

```json
[
  {
    "reservation_group_id": 1,
    "reservations": [
      {
        "reservation_id": 10,
        "date": "2025-03-19",
        "start_hour": 14,
        "end_hour": 16,
        "reserved_count": 2,
        "is_confirmed": true
      },
      {
        "reservation_id": 11,
        "date": "2025-03-19",
        "start_hour": 16,
        "end_hour": 18,
        "reserved_count": 3,
        "is_confirmed": true
      }
    ]
  }
]
```

<br>

# 📌 예약 신청 API (Create Reservation)

## 1️⃣ 설명

- 특정 날짜(`start_date`)의 특정 시간(`start_hour`) ~ 특정 날짜(`end_date`)의 특정 시간(`end_hour`)에 예약을 신청하는 API입니다.
- 예약은 **최소 3일 이전에 신청**해야 합니다.
- **1시간 단위로만 예약 가능**하며, 하루 최대 50,000명까지 예약 가능합니다.
- 예약은 **예약 그룹 단위**로 생성됩니다.

---

## 2️⃣ 요청 형식 (Request)

### **📌 Method & URL**

```
POST /v1/reservations
```

### **📌 Body (JSON)**

| 필드명         | 타입   | 필수 여부 | 설명                        |
| -------------- | ------ | --------- | --------------------------- |
| start_date     | string | ✅ 필수   | 예약 시작 날짜 (YYYY-MM-DD) |
| end_date       | string | ✅ 필수   | 예약 종료 날짜 (YYYY-MM-DD) |
| start_hour     | int    | ✅ 필수   | 예약 시작 시간 (0 ~ 23)     |
| end_hour       | int    | ✅ 필수   | 예약 종료 시간 (1 ~ 24)     |
| reserved_count | int    | ✅ 필수   | 예약 인원 수 (최대 50,000)  |

#### ✅ **예시**

```json
{
  "start_date": "2025-04-01",
  "end_date": "2025-04-03",
  "start_hour": 10,
  "end_hour": 12,
  "reserved_count": 10
}
```

## 3️⃣ 응답 형식 (Response)

### 📌 성공 응답 (201 Created)

```json
[
  {
    "reservation_group_id": 1,
    "reservation_id": 1001,
    "date": "2025-04-01",
    "start_hour": 10,
    "end_hour": 12,
    "reserved_count": 10,
    "is_confirmed": false
  },
  {
    "reservation_group_id": 1,
    "reservation_id": 1002,
    "date": "2025-04-02",
    "start_hour": 0,
    "end_hour": 24,
    "reserved_count": 10,
    "is_confirmed": false
  },
  {
    "reservation_group_id": 1,
    "reservation_id": 1003,
    "date": "2025-04-03",
    "start_hour": 0,
    "end_hour": 12,
    "reserved_count": 10,
    "is_confirmed": false
  }
]
```

<br>

# 📌 예약 수정 API (Update Reservation)

## 1️⃣ 설명

- 사용자가 **본인의 예약을 수정**하는 API입니다.
- 예약 수정 시, 기존 예약 데이터를 삭제하고 새로운 예약 데이터를 삽입합니다.
- 다음과 같은 경우 수정이 불가능합니다:
  - **본인의 예약이 아닌 경우**
  - **이미 확정된 예약인 경우**
  - **예약 시작 시간이 현재 날짜 기준 3일 이내인 경우**

---

## 2️⃣ 요청 형식 (Request)

### **📌 Method & URL**

```
PUT /v1/reservations/{reservation_group_id}
```

> **`reservation_group_id`**: 수정할 예약 그룹의 ID

### **📌 Body (JSON)**

| 필드명         | 타입   | 필수 여부 | 설명                                 |
| -------------- | ------ | --------- | ------------------------------------ |
| start_date     | string | ✅ 필수   | 수정할 예약의 시작 날짜 (YYYY-MM-DD) |
| end_date       | string | ✅ 필수   | 수정할 예약의 종료 날짜 (YYYY-MM-DD) |
| start_hour     | int    | ✅ 필수   | 수정할 예약의 시작 시간 (0 ~ 23)     |
| end_hour       | int    | ✅ 필수   | 수정할 예약의 종료 시간 (1 ~ 24)     |
| reserved_count | int    | ✅ 필수   | 수정할 예약 인원 수                  |

#### ✅ **예시**

```json
{
  "start_date": "2025-04-05",
  "end_date": "2025-04-07",
  "start_hour": 9,
  "end_hour": 12,
  "reserved_count": 5
}
```

## 3️⃣ 응답 형식 (Response)

### 📌 성공 응답 (200 OK)

```json
{
  "message": "예약 수정 완료",
  "reservation_group_id": 123
}
```

<br>

# 📌 예약 삭제 API (Delete Reservation)

## 1️⃣ 설명

- 사용자가 **본인의 예약을 삭제**하는 API입니다.
- 다음과 같은 경우 예약을 삭제할 수 없습니다:
  - **본인의 예약이 아닌 경우 (`403 Forbidden`)**
  - **이미 확정된 예약인 경우 (`400 Bad Request`)**
- 예약 그룹 단위로 삭제되며, 해당 `reservation_group_id`에 속한 모든 예약이 삭제됩니다.

---

## 2️⃣ 요청 형식 (Request)

### **📌 Method & URL**

```
DELETE /v1/reservations/{reservation_group_id}
```

> **`reservation_group_id`**: 삭제할 예약 그룹의 ID

#### ✅ **예시 요청**

```
DELETE /v1/reservations/2 Authorization: Bearer {access_token}
```

---

## 3️⃣ 응답 형식 (Response)

### 📌 성공 응답 (200 OK)

```json
{
  "message": "예약이 성공적으로 삭제되었습니다.",
  "reservation_group_id": 123
}
```

<br>

# 📌 관리자 예약 조회 API (Get Admin Reservations)

## 1️⃣ 설명

- **관리자가 전체 예약을 조회**하는 API입니다.
- 특정 조건(`user_id`, `reservation_group_id`, `start_date`, `end_date` 등)에 따라 필터링할 수 있습니다.
- **예약 그룹(`reservation_group_id`)을 기준으로 데이터를 그룹화**하여 반환합니다.
- **관리자 권한이 필요한 API입니다.**

---

## 2️⃣ 요청 형식 (Request)

### **📌 Method & URL**

```
GET /v1/admin/reservations
```

### **📌 Query Parameters**

| 필드명               | 타입   | 필수 여부 | 설명                                                  |
| -------------------- | ------ | --------- | ----------------------------------------------------- |
| user_id              | int    | ❌ 선택   | 특정 사용자 ID의 예약만 조회                          |
| reservation_group_id | int    | ❌ 선택   | 특정 예약 그룹 ID의 예약만 조회                       |
| start_date           | string | ❌ 선택   | 조회 시작 날짜 (YYYY-MM-DD)                           |
| end_date             | string | ❌ 선택   | 조회 종료 날짜 (YYYY-MM-DD)                           |
| is_confirmed         | bool   | ❌ 선택   | 확정된 예약(`true`) 또는 미확정 예약(`false`)만 조회  |
| past                 | bool   | ❌ 선택   | `true` = 과거 예약만 조회, `false` = 미래 예약만 조회 |

#### ✅ **예시**

```
GET /?user_id=10&start_date=2025-04-01&end_date=2025-04-30&is_confirmed=true
```

---

## 3️⃣ 응답 형식 (Response)

### 📌 성공 응답 (200 OK)

```json
[
  {
    "reservation_group_id": 1,
    "user_id": 10,
    "start_date": "2025-04-01",
    "end_date": "2025-04-03",
    "start_hour": 9,
    "end_hour": 12,
    "reserved_count": 10,
    "is_confirmed": true,
    "reservations": [
      {
        "reservation_id": 1001,
        "date": "2025-04-01",
        "start_hour": 9,
        "end_hour": 12,
        "reserved_count": 10
      },
      {
        "reservation_id": 1002,
        "date": "2025-04-02",
        "start_hour": 9,
        "end_hour": 12,
        "reserved_count": 10
      }
    ]
  }
]
```

<br>

# 📌 관리자 예약 확정 API (Confirm Reservation)

## 1️⃣ 설명

- **관리자가 특정 예약 그룹을 확정**하는 API입니다.
- **이미 시작된 예약은 확정할 수 없습니다.**
- 확정된 예약은 **시험 일정(`exam_schedules`)에 반영**됩니다.
- 같은 시간대의 예약이 **50,000명을 초과할 경우 확정 불가**합니다.

---

## 2️⃣ 요청 형식 (Request)

### **📌 Method & URL**

```
POST /v1/admin/reservations/confirm/{reservation_group_id}
```

> **`reservation_group_id`**: 확정할 예약 그룹의 ID

#### ✅ **예시 요청**

```
POST /v1/admin/reservations/confirm/2 Authorization: Bearer {access_token}
```

---

## 3️⃣ 응답 형식 (Response)

### 📌 성공 응답 (200 OK)

```json
{
  "message": "예약 확정 완료",
  "reservation_group_id": 2
}
```

<br>

# 📌 관리자 예약 삭제 API (Delete Admin Reservation)

## 1️⃣ 설명

- **관리자가 특정 예약 그룹을 삭제**하는 API입니다.
- **확정된 예약도 삭제할 수 있습니다.**
- **확정된 예약을 삭제할 경우, 관련된 `exam_schedule`의 `total_reserved_count`가 업데이트**됩니다.
- `total_reserved_count`가 0이 되면 해당 `exam_schedule`도 삭제됩니다.

---

## 2️⃣ 요청 형식 (Request)

### **📌 Method & URL**

```
DELETE /v1/admin/reservations/{reservation_group_id}
```

> **`reservation_group_id`**: 삭제할 예약 그룹의 ID

#### ✅ **예시 요청**

```
DELETE /v1/admin/reservations/2 Authorization: Bearer {access_token}
```

---

## 3️⃣ 응답 형식 (Response)

### 📌 성공 응답 (200 OK)

```json
{
  "message": "관리자가 예약을 삭제하였습니다.",
  "reservation_group_id": 123
}
```

<br>
# 📌 관리자 예약 수정 API (Update Admin Reservation)

## 1️⃣ 설명

- **관리자가 특정 예약 그룹을 수정**하는 API입니다.
- **확정 여부와 관계없이 날짜, 시간, 인원을 수정할 수 있습니다.**
- 다음 조건을 충족해야 수정이 가능합니다:
  - **현재 날짜 기준 3일 이내 예약은 수정할 수 없음.**
  - **변경 후 예약 인원이 50,000명을 초과할 수 없음.**
  - **확정된 예약을 수정할 경우, 관련된 `exam_schedule`도 업데이트됨.**

---

## 2️⃣ 요청 형식 (Request)

### **📌 Method & URL**

```
PUT /v1/admin/reservations/{reservation_group_id}
```

> **`reservation_group_id`**: 수정할 예약 그룹의 ID

### **📌 Body (JSON)**

| 필드명         | 타입   | 필수 여부 | 설명                                  |
| -------------- | ------ | --------- | ------------------------------------- |
| start_date     | string | ✅ 필수   | 수정할 예약의 시작 날짜 (YYYY-MM-DD)  |
| end_date       | string | ✅ 필수   | 수정할 예약의 종료 날짜 (YYYY-MM-DD)  |
| start_hour     | int    | ✅ 필수   | 수정할 예약의 시작 시간 (0 ~ 23)      |
| end_hour       | int    | ✅ 필수   | 수정할 예약의 종료 시간 (1 ~ 24)      |
| reserved_count | int    | ✅ 필수   | 수정할 예약 인원 수                   |
| is_confirmed   | bool   | ❌ 선택   | 수정 후 예약 확정 여부 (기본값: 유지) |

#### ✅ **예시**

```json
{
  "start_date": "2025-04-05",
  "end_date": "2025-04-07",
  "start_hour": 9,
  "end_hour": 12,
  "reserved_count": 50,
  "is_confirmed": true
}
```

## 3️⃣ 응답 형식 (Response)

### 📌 성공 응답 (200 OK)

```json
{
  "message": "예약 수정 완료",
  "reservation_group_id": 123
}
```
