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

## 환경 변수 설정 (.env)

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

1. 페이지 상단에서 보고서를 검색하거나 랜덤으로 표시된 보고서를 탐색합니다.
2. 각 결과에서 'Show Detail'을 클릭하면:

   * 이미지, 요약, 보고서 및 요약서 PDF 미리보기/다운로드 제공
3. 상세 페이지에서 'Back' 버튼을 누르면 목록으로 돌아갑니다.

## 세션 상태 관리

Streamlit `st.session_state`를 사용하여 다음 정보를 관리합니다:

* 검색어 (`search_keyword`)
* 현재 페이지 (`current_page`)
* 선택된 보고서 제목/텍스트/이미지 (`title`, `text`, `images`)
* PDF 파일 경로 및 ID (`report_path`, `report_id`, `pdf_files`)
* PocketBase의 현재 record 객체 (`record`)

## 라우팅 구조

* `/`: 초기 진입점이며 내부적으로 `/list`로 이동
* `/list`: 보고서 검색 및 목록 출력
* `/detail`: 선택된 보고서 상세 내용 표시

## 주의 사항

* PDF 파일은 `report_path` 경로 하위의 `<report_id>` 폴더에 있어야 합니다.
* PocketBase에서 불러온 파일 URL로 PDF 및 이미지 미리보기를 제공합니다.

## 라이선스

MIT License
