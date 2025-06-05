from pathlib import Path
import json
#from datetime import datetime -직접 날자 받는 걸로 변경경
import matplotlib.pyplot as plt
from collections import Counter
import random
import requests

name = input("이름을 입력해주세요.:")


def get_summary(diary):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer <OPENROUTER_API_KEY>",
            "Content-Type": "application/json"
  },
        data=json.dumps({
            "model": "meta-llama/llama-3.3-8b-instruct:free",
            "messages": [
            {
                "role": "user",
                "content": f"다음 일기를 분석하고 그를 토대로 요약해줘. \n{diary}"
            } 
    ],
    
  })
)
    if response.ok:
        result = response.json()
        output = result["choices"][0]["message"]["content"]
        return output
    else:
        print("요청실패")

def get_advice(diary):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer <OPENROUTER_API_KEY>",
            "Content-Type": "application/json"
  },
        data=json.dumps({
            "model": "meta-llama/llama-3.3-8b-instruct:free",
            "messages": [
            {
                "role": "user",
                "content": f"다음 일기를 요약하고 감정 분석과 조언을 해줘.\n{diary}"
            } 
    ],
    
  })
)
    if response.ok:
        result = response.json()
        output = result["choices"][0]["message"]["content"]
        return output
    else:
        print("요청실패")


        date_str = input("오늘의 날짜를 입력해주세요.(예: 2025-00-00): ").strip()
        print("\n오늘의 일기를 작성해주세요.")
        diary = input("\n오늘의 일기를 입력: ")

        summary = get_summary(diary)
        advice = get_advice(diary)
        print("\n 요약:",summary)
        print("\n 조언:",advice)

        emotion ={}

        save_diary_dta(date_str, name, diary, summary, advice, emotion)
    
    
        date = input("언제 일기를 확인하시겠습니까?(2025-00-00)")
        file_path = DATA_SAVE / f"{date_str}_{name}.json"
        
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            print(f"\n날짜: {data['data']}")
            print(f"\n작성자: {data['name']}")
            print(f"\n일기: {data['diary']}")
            print(f"\n요약: {data['summary']}")
            print(f"\n조언: {data['advice']}")
            print(f"\n감정 분석 결과: ")
            for emotion, score in data["emotion"].items():
                print(f" -{emotion}:{score}")
            else:
                print(f"\n {date_str}의 일기가 존재하지 않습니다.")