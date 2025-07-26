# 탐구보고서 도서관

과학 탐구보고서를 쉽고 빠르게 검색하고 열람할 수 있는 웹 애플리케이션입니다.
보고서의 제목 및 본문 내용을 검색하면 AI 임베딩 기반의 유사도 검색을 통해 관련 탐구보고서를 표시해주며, 요약된 내용과 함께 PDF 파일도 다운로드할 수 있습니다.

## 주요 기능

* Vertex AI 임베딩 모델을 통한 다국어 검색
* Couchbase 벡터 검색 기반 유사도 매칭
* PocketBase에서 보고서 메타데이터 및 이미지 불러오기
* Streamlit 기반의 간편한 UI 구성
* 보고서, 요약서 미리보기 및 다운로드 기능

## 실행 환경

* Python 3.10 이상
* Streamlit
* Google Vertex AI (텍스트 임베딩)
* Couchbase Server + Search Index + Vector Search
* PocketBase (메타데이터 관리용)

## 필수 패키지 설치

```bash
pip install streamlit pocketbase python-dotenv google-cloud-aiplatform google-generativeai couchbase extra-streamlit-components
```

## 환경 변수 설정 (`.env`)

```env
DB_CONN_STR=couchbase://localhost
DB_USERNAME=admin
DB_PASSWORD=password
DB_BUCKET=your_bucket
DB_SCOPE=your_scope
DB_COLLECTION=your_collection
INDEX_NAME=your_index
GOOGLE_API_KEY=your_google_api_key
EMBEDDING_MODEL=text-multilingual-embedding-002
```

## 디렉토리 구조 예시

```
report_library/
├── app.py                          # 메인 실행 파일
├── .env                            # 환경 변수
├── reports/                        # PDF 보고서 저장 폴더
│   └── <report_id>/               # 개별 보고서 디렉토리
│       ├── 원본.pdf
│       ├── 요약.pdf
│       └── 기타파일.pdf
└── README.md
```

## 사용법

```bash
streamlit run app.py
```

1. 메인 페이지에서 탐구보고서를 검색하거나 랜덤으로 표시된 보고서를 확인할 수 있습니다.
2. 각 카드에서 'Show Detail'을 클릭하면:

   * 대표 이미지, 요약 텍스트, PDF 미리보기 및 다운로드 제공

## 세션 상태 관리

Streamlit `st.session_state`를 사용하여:

* 현재 페이지 번호
* 검색어
* 선택된 보고서의 제목/텍스트/이미지
* PDF 파일 경로 및 ID

등의 정보를 유지합니다.

## 라이선스

MIT License
