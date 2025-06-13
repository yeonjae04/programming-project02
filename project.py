from pathlib import Path
import json
import matplotlib.pyplot as plt
from collections import Counter
import random
import requests

name = input("이름을 입력해주세요.:")

#사용자의 일기 데이터 저장 함수
DATA_SAVE = Path("diary_data")
DATA_SAVE.mkdir(exist_ok = True)

def save_diary_dta(date, name, diary, summary, advice, emotion):
    """
    하루치 일기 데이터를 JSON 파일로 저장합니다
    
    Parameters:
    -date_str (str): 날짜 (예: 2025-06-01)
    -name (str): 사용자 이름
    -diary (str): 원본 일기 텍스트
    -summary (str): 요약 텍스트
    -advice (str): 조언 텍스트
    -emotion(dict): 감정 분석 결과 
    """
    data = {
        "name": name,
        "data": date,
        "diary": diary,
        "summary": summary,
        "advice": advice,
        "emotion": emotion
    }
    file_path = DATA_SAVE / f"{date}_{name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"{date} 일기가 저장되었습니다!->{file_path}")

#사용자 일기 요약 함수
def get_summary(diary):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
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

#사용자 일기 조언 함수
def get_advice(diary):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
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

       
emotion ={}

#사용자 감정 분석 함수
def get_emotion_scores(diary):
    """
    사용자의 일기를 바탕으로 감정을 분석하여 숫자(0~10)을 반환합니다.
    감정은 기쁨, 슬픔, 분노, 불안, 혐오, 놀람 6가지입니다.
    """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": "meta-llama/llama-3.3-8b-instruct:free",
            "messages": [
            {
                "role": "user",
                "content": (f"다음 일기를 읽고 감정 점수를 0부터 10까지 숫자로 분석해줘.\n"
                f"다음과 같은 JSON 형태로 정확하게 출력해줘."
                f'{{"기쁨":숫자, "슬픔":숫자, "분노":숫자, "불안":숫자, "혐오":숫자, "놀람":숫자}}'
                f"{diary}"
                )
            } 
         ]
     })
    )
    if response.ok:
        try:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            emotion_data = json.loads(content)
            return emotion_data
        except Exception as e:
            print("감정 분석을 불러오는 데 문제가 있어요:", e)
            return {}
    else:
        print("감정 분석 요청실패")

#감정분석 시각화 함수
emotion_colors = {
    "기쁨": "#FFD700",   # 노랑
    "슬픔": "#1E90FF",   # 파랑
    "분노": "#FF4500",   # 빨강
    "불안": "#9370DB",   # 보라
    "혐오": "#2E8B57",   # 초록
    "놀람": "#E97E0B"    # 주황황
}

def visualize_emotion_scores(emotion_scores, date_str):
    """
    감정 점수를 막대그래프로 시각화하고 파일로 저장합니다.
    
    Parameters:
    emotion scores(dict) : 감정별 점수
    date (str): 날짜
    """
    emotions = ['기쁨', '슬픔', '분노', '불안', '혐오', '놀람']
    scores = [emotion_scores.get(emotion,0) for emotion in emotions]
    colors= [ emotion_colors[emotion] for emotion in emotions]

    plt.figure(figsize=(8,6))
    bars = plt.bar(emotions, scores, color = colors)

    plt.ylim(0,10)
    plt.title(f"{date_str} 감정 분석 결과")
    plt.xlabel("감정")
    plt.ylabel("점수(0~10)")

    for bar, score in zip (bars, scores):
        plt.text(bar.get_x() + bar.get_width()/2, score + 0.3, f"{score}", ha='center', va='bottom', fontsize=10)
    
    img_path = DATA_SAVE / f"{date_str}_emotion.png"
    plt.tight_layout()
    plt.savefig(img_path)
    plt.close()
    print(f"감정 이미지 저장됨: {img_path}")


#사용자 선택 처리 함수
def get_choices(choice:str):
    if choice == '1':
        date = input("오늘 날짜를 입력해주세요. (예: 2025-06-09): ").strip()
        print("\n오늘의 일기를 작성해주세요.")
        diary = input("\n오늘의 일기를 입력: ")

        summary = get_summary(diary)
        advice = get_advice(diary)
        emotion = get_emotion_scores(diary)

        print("\n 요약:",summary)
        print("\n 조언:",advice)

        save_diary_dta(date, name, diary, summary, advice, emotion)
        visualize_emotion_scores(emotion, date)

    elif choice == '2':
        date = input("언제 일기를 확인하시겠습니까?(2025-00-00)")
        #print(llm에게 전달해서 그날 일기 요약하게 하기)
        file_path = DATA_SAVE / f"{date}_{name}.json"
        
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
                print(f"\n {date}의 일기가 존재하지 않습니다.")
    
    elif choice == '3':
        print("\n과거 일기를 분석합니다.")
        #여기서 과거 저장 데이터 바탕으로 분석된 그래프 꺼내기

        img_path = DATA_SAVE / f"{name}_전체감정분석.png"

        if img_path.exists():
            print(f"\n감정 분석 이미지가 존재합니다: {img_path}")
            try:
                from PIL import Image
                img = Image.open(img_path)
                img.show()
            except ImportError:
                print("이미지를 보려면 PIL(pillow) 라이브러리가 필요합니다. 설치: pip install pillow")

        else:
            print(f"\n감정 분석 이미지가 존재하기 않습니다.")
            print("먼저 전체 감정 분석을 생성하세요.")

    else:
        print("잘못된 입력입니다. 1~3번 중 하나를 선택하여 주세요.")

#사용자 질문 함수
def main():

    while True:
        print("\n무엇을 하시겠습니까?")
        print("\n1. 오늘 일기 작성")
        print("\n2. 과거 일기 확인")
        print("\n3. 과거 일기 분석 보기")
        choice = input("번호를 선택하세요: ").strip()
        get_choices(choice)

if __name__ == "__main__":
    main()
