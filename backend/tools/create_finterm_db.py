from pymilvus import model
from pymilvus import MilvusClient
import pandas as pd
from tqdm import tqdm
import logging
from dotenv import load_dotenv
load_dotenv()
import torch    
from pymilvus import MilvusClient, DataType, FieldSchema, CollectionSchema

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化 OpenAI 嵌入函数
embedding_function = model.dense.SentenceTransformerEmbeddingFunction(
            # model_name='nvidia/NV-Embed-v2', 
            # model_name='dunzhang/stella_en_1.5B_v5',
            # model_name='all-mpnet-base-v2',
            # model_name='intfloat/multilingual-e5-large-instruct',
            # model_name='Alibaba-NLP/gte-Qwen2-1.5B-instruct',
            model_name='BAAI/bge-m3',
            # model_name='jinaai/jina-embeddings-v3',
            device='cuda:0' if torch.cuda.is_available() else 'cpu',
            trust_remote_code=True
        )
# embedding_function = model.dense.OpenAIEmbeddingFunction(model_name='text-embedding-3-large')

# 文件路径
file_path = "backend/data/万条金融标准术语.csv" 
db_path = "backend/db/finterm_bge_m3.db"

# 连接到 Milvus
client = MilvusClient(db_path)

collection_name = "finterm_only"

# 加载数据
logging.info("Loading data from CSV")
df = pd.read_csv(file_path, 
                 dtype=str, 
                low_memory=False,
                 ).fillna("NA")

# 获取向量维度（使用一个样本文档）
sample_doc = "Sample Text"
sample_embedding = embedding_function([sample_doc])[0]
vector_dim = len(sample_embedding)

# 构造Schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=vector_dim), # BGE-m3 最重要
    FieldSchema(name="finterm_name", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="input_file", dtype=DataType.VARCHAR, max_length=500),
]
schema = CollectionSchema(fields, 
                          "Finance Terms", 
                          enable_dynamic_field=True)

# 如果集合不存在，创建集合
if not client.has_collection(collection_name):
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        # dimension=vector_dim
    )
    logging.info(f"Created new collection: {collection_name}")

# # 在创建集合后添加索引
index_params = client.prepare_index_params()
index_params.add_index(
    field_name="vector",  # 指定要为哪个字段创建索引，这里是向量字段
    index_type="AUTOINDEX",  # 使用自动索引类型，Milvus会根据数据特性选择最佳索引
    metric_type="COSINE",  # 使用余弦相似度作为向量相似度度量方式
    params={"nlist": 1024}  # 索引参数：nlist表示聚类中心的数量，值越大检索精度越高但速度越慢
)

client.create_index(
    collection_name=collection_name,
    index_params=index_params
)

# 批量处理
batch_size = 1024

for start_idx in tqdm(range(0, len(df), batch_size), desc="Processing batches"):
    end_idx = min(start_idx + batch_size, len(df))
    batch_df = df.iloc[start_idx:end_idx]

    # 准备文档
    # docs = [f"Term: {row['concept_name']}; Synonyms: {row['Synonyms']}" for _, row in batch_df.iterrows()]
    docs = []
    for _, row in batch_df.iterrows():
        doc_parts = [row['finterm_name']]

        # if row['Full Name'] != "NA" and row['Full Name'] != row['concept_name']:
        #     doc_parts.append(",Full Name: " + row['Full Name'])

        # if row['Synonyms'] != "NA" and row['Synonyms'] != row['concept_name']:
        #     doc_parts.append(", Synonyms: " + row['Synonyms'])

        # if row['Definitions'] != "NA" and row['Definitions'] not in [row['concept_name'], row.get('Full Name', '')]:
        #     doc_parts.append(", Definitions: " + row['Definitions'])

        docs.append(" ".join(doc_parts))

    # 生成嵌入
    try:
        embeddings = embedding_function(docs)
        logging.info(f"Generated embeddings for batch {start_idx // batch_size + 1}")
    except Exception as e:
        logging.error(f"Error generating embeddings for batch {start_idx // batch_size + 1}: {e}")
        continue

    # 准备数据
    data = [
        {
            # "id": idx + start_idx,
            "vector": embeddings[idx],
            "finterm_name": str(row['finterm_name']),
            "input_file": file_path
        } for idx, (_, row) in enumerate(batch_df.iterrows())
    ]

    # 插入数据 - 1024个向量条目，即1024个医疗术语（标准概念）
    try:
        res = client.insert(
            collection_name=collection_name,
            data=data
        )
        logging.info(f"Inserted batch {start_idx // batch_size + 1}, result: {res}")
    except Exception as e:
        logging.error(f"Error inserting batch {start_idx // batch_size + 1}: {e}")

logging.info("Insert process completed.")

# 示例查询
# query = "somatic hallucination"
query = "Recession"
query_embeddings = embedding_function([query])


# 搜索余弦相似度最高的
search_result = client.search(
    collection_name=collection_name,
    data=[query_embeddings[0].tolist()],
    limit=5,
    output_fields=["finterm_name", 
                   ]
)
logging.info(f"Search result for 'Recession': {search_result}")

# 查询所有匹配的实体
query_result = client.query(
    collection_name=collection_name,
    filter="finterm_name == 'Recession'",
    output_fields=["finterm_name",
                   ],
    limit=5
)
logging.info(f"Query result for finterm_name == 'Recession': {query_result}")
