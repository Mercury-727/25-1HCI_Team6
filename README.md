# HCI Team 6 — Phase 3 & 4 Implementation and Evaluation

## 프로젝트 개요
- **목표**: Phase 1~2에서 정의한 페르소나와 작업 목표를 바탕으로, Phase 3에서 핵심 기능을 실제 동작 가능한 수준으로 구현하고, Phase 4에서 사용자 평가를 통해 인터페이스의 사용성을 검증합니다.
- **핵심 페르소나**:
  - **학생 A** (계획적 학습자): 시간 관리와 달성률 기록 기능 중시
  - **학생 B** (즉흥 학습자): AI 추천 플랜과 피드백 기능 중시

---

## 핵심 기능 구현
### 🛠️ 기능 리스트
1. **일정 추가/수정/삭제** – 드래그·리사이징으로 5분 단위 편집 가능
2. **AI 플랜 생성 및 적용** – AI 추천 플랜 뷰, 플랜 적용 버튼
3. **목표 달성 타이머** – SVG 진행바, 초과시간 계산, 일시정지/재개
4. **오늘의 학습 피드백** – 달성률·총 학습시간 요약, 분석·제안·응원 메시지
5. **학습 성향 검사** – EDT 검사 결과 저장 및 학습 유형별 맞춤 요약
6. **헤더/푸터 UI** – 반응형 네비게이션 및 푸터 링크 구성
---

## 사용된 기술 스택
- **프론트엔드**: React 17/18, Lucide Icons
- **백엔드**: Flask, gunicorn, OpenAI API
- **빌드**: Babel (CDN based)
- **배포**: Docker compose

---

## 평가 및 검증
### 🔍 평가 대상과 방법
- **참여자**: 페르소나 대표 사용자 4명
- **테스트 기법**: 관찰(Think-Aloud), 사후 설문, 디브리핑
- **테스트 시나리오**:
  1. 일정 추가 후 AI 플랜 적용
  2. 타이머로 목표 시간 측정 및 달성률 입력
  3. 오늘의 피드백 확인 및 만족도 평가

### ✅ 주요 발견 사항
- **긍정적 피드백**:
  - 드래그·리사이징 UX 직관적
  - AI 추천 플랜이 학습 동기를 높임
- **개선 필요**:
  - 피드백 텍스트 가독성(폰트 크기 조정 권장)
  - 모바일 터치 영역 최적화


## 설치 및 실행 방법
   ```bash
   git clone https://github.com/your-org/hci-team6.git
   cd hci-team6

   # setup nginx/conf.d/default.d appropriately
   # ensure certificate is installed under certbot
   # modify html files' API endpoint to your origin
   cat $OPENAI_API_KEY > .openai-api-key

   docker compose up

   # open your origin in web browser
   ```
