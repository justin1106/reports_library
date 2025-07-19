from typing import Any, Dict, List, Tuple
import streamlit as st
from pocketbase import PocketBase
import extra_streamlit_components as stx
import os
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions
import couchbase.search as search
from couchbase.options import SearchOptions
from couchbase.vector_search import VectorQuery, VectorSearch
from datetime import timedelta
import google.generativeai as genai
from dotenv import load_dotenv
from pprint import pprint
import time
import vertexai
from vertexai.language_models import TextEmbeddingModel
from google.cloud import aiplatform

total_reports = 622

vertexai.init(project="my-first-project-446101")

st.set_page_config(
    page_title="Report Library",
    layout="centered",
    initial_sidebar_state="auto",
)


def init_router():
    initial_route = "/detail" if st.session_state.get("show_detail", False) else "/"
    router = stx.Router({"/": home, "/list": show_list, "/detail": detail})
    
    if st.session_state.get("show_detail", False):
        st.session_state["show_detail"] = False
    
    return router


whole_page = total_reports // 30 + 1
client = PocketBase("https://pocketbase.learnsteam.kr")

if "all_data" not in st.session_state:
    st.session_state["all_data"] = []
    for p in range(whole_page):
        per_page = 30
        datalist = (
            client.collection("cu_report_library").get_list(p + 1, per_page).items
        )
        for d in datalist:
            st.session_state["all_data"].append(d)
if "title" not in st.session_state:
    st.session_state["title"] = ""
if "text" not in st.session_state:
    st.session_state["text"] = ""
if "images" not in st.session_state:
    st.session_state["images"] = []
if "record" not in st.session_state:
    st.session_state["record"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = 0
if "report_path" not in st.session_state:
    st.session_state["report_path"] = None
if "report_id" not in st.session_state:
    st.session_state["report_id"] = None
if "pdf_files" not in st.session_state:
    st.session_state["pdf_files"] = []
if "search_keyword" not in st.session_state:
    st.session_state["search_keyword"] = ""
if "show_detail" not in st.session_state:
    st.session_state["show_detail"] = False

DB_CONN_STR = os.getenv("DB_CONN_STR")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_BUCKET = os.getenv("DB_BUCKET")
DB_SCOPE = os.getenv("DB_SCOPE")
DB_COLLECTION = os.getenv("DB_COLLECTION")
INDEX_NAME = os.getenv("INDEX_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")


def home():
    router.route("/list")


@st.cache_data(ttl=3600)
def generate_embeddings(input_data):
    """Google Generative AI를 사용하여 입력 데이터의 임베딩을 생성합니다"""
    # result = genai.embed_content(
    #     model=EMBEDDING_MODEL,
    #     content=input_data,
    #     task_type="retrieval_query",
    # )
    # return result["embedding"]
    model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")
    result = model.get_embeddings(texts=[input_data])
    return [embedding.values for embedding in result][0]


@st.cache_data(ttl=3600)
def translate_text(text: str, target_lang: str) -> str:
    """텍스트 번역을 위한 캐시된 함수"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"Translate the following text to {target_lang}. Only return the translated text without any additional comments: {text}",
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=100,
                temperature=0.2,
            ),
        )
        return response.text.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text


@st.cache_resource(show_spinner="Connecting to Couchbase")
def connect_to_couchbase(connection_string, db_username, db_password):
    """Connect to couchbase"""

    auth = PasswordAuthenticator(db_username, db_password)
    options = ClusterOptions(auth)
    connect_string = connection_string
    cluster = Cluster(connect_string, options)

    # Wait until the cluster is ready for use.
    cluster.wait_until_ready(timedelta(seconds=5))

    return cluster


def search_couchbase(
    db_scope: Any,
    index_name: str,
    embedding_key: str,
    search_text: str,
):
    """Hybrid search using Python SDK in couchbase"""
    # Generate vector embeddings to search with
    search_embedding = generate_embeddings(search_text)

    # Create the search request
    search_req = search.SearchRequest.create(
        VectorSearch.from_vector_query(VectorQuery(embedding_key, search_embedding, 30))
    )

    docs_with_score = []

    try:
        # Perform the search
        search_iter = db_scope.search(
            index_name,
            search_req,
        )

        # Parse the results
        for row in search_iter.rows():
            score = row.score
            docs_with_score.append([row.id, score])
    except Exception as e:
        raise e
    # print(docs_with_score)
    return docs_with_score


def fetch_random_datas(db_scope: Any, limit: int = 30) -> List[Dict[str, Any]]:
    try:
        query = (
            f"SELECT * FROM `{DB_BUCKET}`.`{DB_SCOPE}`.`{DB_COLLECTION}` LIMIT {limit}"
        )
        query_result = db_scope.query(query)
        datas = [row[DB_COLLECTION] for row in query_result]
        return datas
    except Exception as e:
        pprint(f"Error fetching random reports: {e}")
        return []


def detail():
    print(">>>>>>>>> detail func called")
    st.title(st.session_state["title"])
    st.write("<hr>", unsafe_allow_html=True)
    cols = []
    for idx, img in enumerate(st.session_state["images"]):
        image = client.collection("cu_report_library").get_file_url(
            st.session_state["record"], img
        )
        cols.append(image)
        if len(st.session_state["images"]) == 1:
            st.image(image)
        elif len(img) % 2 == 1 and len(st.session_state["images"]) - idx == 1:
            st.image(cols[0])
        elif idx % 2 == 1:
            col1, col2 = st.columns(2)
            col1.image(cols[0])
            col2.image(cols[1])
            cols = []

    st.write("<hr>", unsafe_allow_html=True)
    st.subheader("보고서 요약")
    st.write(st.session_state["text"])
    st.write("<hr>", unsafe_allow_html=True)
    st.subheader("다운로드")
    folder = st.session_state["report_path"] + str(st.session_state["report_id"])
    pdf_files = os.listdir(folder)
    if len(pdf_files) == 3:
        report_file = pdf_files[2]
        summary_file = pdf_files[1]
    else:
        report_file = pdf_files[1]
        summary_file = None
    with open(folder + "\\" + report_file, "rb") as file:
        report = client.collection("cu_report_library").get_file_url(
            st.session_state["record"],
            st.session_state["pdf_files"][1],
        )
        name, btn, prev = st.columns(3)
        name.write(report_file)
        report_btn = btn.download_button("보고서 다운로드", file, file_name=report_file)
        prev.write(f"<a href={report}>미리보기</a>", unsafe_allow_html=True)
    with open(folder + "\\" + summary_file, "rb") as file:
        summary = client.collection("cu_report_library").get_file_url(
            st.session_state["record"], st.session_state["pdf_files"][0]
        )
        name2, btn2, prev2 = st.columns(3)
        name2.write(summary_file)
        if summary_file == None:
            st.write("There is no file")
        else:
            summary_btn = btn2.download_button(
                "작품요약서 다운로드",
                file,
                file_name=summary_file,
            )
        prev2.write(f"<a href={summary}>미리보기</a>", unsafe_allow_html=True)
    st.write("<hr>", unsafe_allow_html=True)
    home = st.button("Back")
    if home:
        router.route("/list")


def show_list():
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    cluster = connect_to_couchbase(DB_CONN_STR, DB_USERNAME, DB_PASSWORD)
    bucket = cluster.bucket(DB_BUCKET)
    scope = bucket.scope(DB_SCOPE)
    collection = scope.collection(DB_COLLECTION)

    st.title("탐구보고서 도서관")
    search_text = st.text_input("검색", placeholder="제목 또는 본문 내용으로 검색")
    results = []
    if search_text:
        st.session_state["search_keyword"] = search_text
    # st.session_state["search_keyword"] = translate_text(st.session_state["search_keyword"], "english")
    if st.session_state["search_keyword"]:
        st.session_state["current_page"] = 0
        with st.spinner("Searching..."):
            st.write(f"Search Text: " + st.session_state["search_keyword"])
            datas = search_couchbase(
                db_scope=scope,
                index_name=INDEX_NAME,
                embedding_key="text_embedding",
                search_text=st.session_state["search_keyword"],
            )
            results = []
            for data in datas:
                result = client.collection("cu_report_library").get_list(
                    query_params={"filter": f"report_id = {data[0]}"}
                )
                if result.items:  # 결과가 있는 경우에만 추가
                    results.append(result.items[0])
    else:
        # 초기 데이터 로딩 방식 수정
        results = []
        datas = fetch_random_datas(scope, limit=30)
        for data in datas:
            try:
                result = client.collection("cu_report_library").get_list(
                    query_params={"filter": f"report_id = {data['id']}"}
                ).items
                if result:  # 결과가 있는 경우에만 추가
                    results.append(result[0])
            except Exception as e:
                print(f"Error fetching data for id {data['id']}: {e}")
                continue

    # 결과가 있는지 확인
    if not results:
        st.warning("검색 결과가 없습니다.")
        return

    print(">>>>> results:", results)
    # print(search_keyword)
    st.write("<hr>", unsafe_allow_html=True)
    results = [results[i : i + 30] for i in range(0, len(results))]
    result = results[st.session_state["current_page"]]
    print(">>>>> result:", result, ", current page:", st.session_state["current_page"])
    for idx, d in enumerate(result):
        id = d.id
        pdf_files = d.pdf
        title = d.title
        images = d.pdf_image
        t, i, b = st.columns(3)
        t.write(f"<h5>{title}<h5>", unsafe_allow_html=True)
        if len(images) != 0:
            image = client.collection("cu_report_library").get_file_url(d, images[0])
            i.image(image)
        else:
            image = None
            st.write("There is no image")

        button_key = f"detail_button_{id}_{idx}"
        detail_button = b.button("Show Detail", key=button_key)
        
        st.write("<hr>", unsafe_allow_html=True)
        if detail_button:
            st.session_state["show_detail"] = True
            st.session_state["text"] = d.text_summary
            st.session_state["title"] = title
            st.session_state["images"] = images
            st.session_state["record"] = d
            st.session_state["report_path"] = "..\\reports"
            st.session_state["report_id"] = d.report_id
            st.session_state["pdf_files"] = pdf_files
            st.rerun()

    # b1, page, b2 = st.columns(3)
    # if st.session_state["search_keyword"]:
    #     back = b1.button("<=", use_container_width=True, key="back")
    #     next = b2.button("=>", use_container_width=True, key="next")
    # else:
    #     back = b1.button("<=", use_container_width=True, key="back", disabled=True)
    #     next = b2.button("=>", use_container_width=True, key="next", disabled=True)
    # page.button(
    #     str(st.session_state["current_page"] + 1),
    #     use_container_width=True,
    #     disabled=True,
    # )

    # if back and st.session_state["current_page"] > 0:
    #     st.session_state["current_page"] -= 1
    #     st.rerun()
    # if next and st.session_state["current_page"] < len(results):
    #     st.session_state["current_page"] += 1
    #     st.rerun()


router = init_router()
router.show_route_view()
