from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from services.ner_service import NERService
from services.std_service import StdService
from services.financial_ner_service import FinancialNERService
from typing import List, Dict, Optional, Literal, Union, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI()

# 配置跨域资源共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化各个服务
logger.info("Initializing services...")
ner_service = NERService()  # 医疗命名实体识别服务
logger.info("NER service initialized")
financial_ner_service = FinancialNERService()  # 金融命名实体识别服务
logger.info("Financial NER service initialized")
standardization_service = StdService()  # 术语标准化服务
logger.info("Standardization service initialized")

# 基础模型类
class BaseInputModel(BaseModel):
    """基础输入模型，包含所有模型共享的字段"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

class TextInput(BaseInputModel):
    """文本输入模型，用于标准化和命名实体识别"""
    text: str = Field(..., description="输入文本")
    termTypes: Dict[str, bool] = Field(
        default_factory=dict,
        description="术语类型"
    )

# API 端点：术语标准化
@app.post("/api/std")
async def standardization(input: TextInput):
    try:
        # 记录请求信息
        logger.info(f"Received request: text={input.text}, termTypes={input.termTypes}")

        # 进行命名实体识别
        ner_results = financial_ner_service.process(input.text, input.termTypes)

        # 获取识别到的实体
        entities = ner_results.get('entities', [])
        if not entities:
            return {"message": "No financial terms have been recognized", "standardized_terms": []}

        # 标准化每个实体
        standardized_results = []
        for entity in entities:
            std_result = standardization_service.search_similar_terms(entity['word'])
            standardized_results.append({
                "original_term": entity['word'],
                "entity_group": entity['entity_group'],
                "standardized_results": std_result
            })

        return {
            "message": f"{len(entities)} financial terms have been recognized and standardized",
            "standardized_terms": standardized_results
        }

    except Exception as e:
        logger.error(f"Error in standardization processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# API 端点：命名实体识别
@app.post("/api/ner")
async def ner(input: TextInput):
    try:
        logger.info(f"Received NER request: text={input.text}, termTypes={input.termTypes}")
        logger.info(f"Using service: {financial_ner_service.__class__.__name__}")
        results = financial_ner_service.process(input.text, input.termTypes)
        return results
    except Exception as e:
        logger.error(f"Error in NER processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
