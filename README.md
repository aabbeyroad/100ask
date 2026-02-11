# Daily Self-Reflection Q&A for Busy Parents

바쁜 부모를 위한 일일 자기성찰 Q&A 서비스입니다.

매일 하나의 성찰 질문을 제공하고, 답변을 기록하여 지난 기록을 돌아볼 수 있습니다.

## Features

- **Daily Question**: 매일 다른 성찰 질문 제공 (육아, 감정, 관계, 성장, 자기돌봄 카테고리)
- **Answer Saving**: 답변 작성 및 저장 (하루 한 번, 수정 가능)
- **History**: 지난 답변 기록 조회

## Setup

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://localhost:8000 in your browser.

## Tech Stack

- **Backend**: Python / FastAPI
- **Frontend**: Vanilla HTML / CSS / JavaScript
- **Storage**: JSON file (answers.json)
