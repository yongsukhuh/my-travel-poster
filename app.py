import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageDraw, ImageFont, ImageOps

st.set_page_config(page_title="Travel Poster Studio", page_icon="🎨", layout="centered")

st.title("📸 Travel Poster AI Studio")
st.markdown("스마트 하이브리드 렌더링 (원본 100% 보존 + AI 화풍 변환)")

with st.sidebar:
    st.header("⚙️ 시스템 설정")
    saved_key = st.secrets.get("FAL_KEY", "")
    fal_api_key = st.text_input("Fal.ai API 키를 입력하세요", type="password", value=saved_key)

# AI에게는 레이아웃 분할 명령을 빼고, 오직 '화풍(Style)'에 관한 사용자 원문만 전달합니다.
ai_prompts = {
    "Style A: 실사 + 레트로 카툰 (Rubber Hose)": "동일한 인물을 고해상도 사진 컷아웃 형태로 간결한 단색 빈 필드에 배치하세요. 원본 사진에서 이미 실제로 존재하며 인물과 가장 밀접한 관계가 있는 한 가지 물건을 선택하여 유일한 개성화된 만화 파트너로 변환하세요. 물건의 원래 형태, 색상, 인식 특징을 유지한 채, 거친 검은 고무 튜브 스타일의 손발, 타원형 눈, 흰 장갑, 소량의 베니어 점, 그리고 절제된 복고 애니메이션 인쇄 질감을 추가하세요. 만화 물건은 실제 인물과 명확한 공간적 상호작용(예: 손을 잡거나 안아주는 등)을 일으켜야 합니다.",
    "Style B: 파스텔 과슈 회화 (Pastel Gouache)": "人物から最も認識しやすい顔、髪型、帽子、マフラー、服の色、持ち物、姿勢を抽出し、大胆にトリミングされたパステルとガッシュの旅行ポートレートに再構成します。マットな不透明ガッシュ、パステルのドライブラシ、太い筆のタッチ、少し粗い木炭の輪郭を使用します。紙の質感、粗いエッジ、塗り残しを保持し、滑らかなデジタルイラストは避けてください。配色は元の写真から5〜7色の柔らかな色を抽出します。(Text translated for AI optimization)",
    "Style C: 단색 건축 에칭 판화 (Monochrome Etching)": "건축의 가장 식별 가능한 윤곽, 구조와 공간 관계를 추출해 고도의 디테일을 가진 세련된 단색 동판화(에칭)나 고전 건축 판화로 재구성합니다. 극도로 가는 에칭 선, 평행 음영선, 교차 음영선, 점묘, 단속선과 약간의 드라이 포인트 긁힘으로 석재, 조각, 공간 그림자를 형성합니다. 딱딱한 직사각형 테두리를 피하고 종이로 자연스럽게 흩어지게 하세요. 따뜻한 아이보리 배경을 사용하며, 먹색은 한 가지만 허용합니다.",
    "Style D: 여백 크레용 스케치 (Sparse Crayon)": "피사체를 극단적으로 축소하여 매우 단순화되고 여백이 많은 크레용 스케치로 재구성합니다. 망설이고, 끊기며, 약간의 멈춤이 있는 검은색 크레용 윤곽선을 사용하고, 1~2개의 연한 색 크레용 스케치로 표현합니다. 종이의 55% 이상을 따뜻한 흰 종이 여백으로 남겨두세요. 정교한 묘사나 완전 채색을 피하세요.",
    "Style E: 고무도장 여행 들판 노트 (Rubber Stamp)": "주체 윤곽과 핵심 시각 관계를 추출해 작고 여러 색상이 들어간 다색 고무도장 이미지로 압축하세요. 진짜 고무도장 조각 질감, 수작업 칼자국, 굵기가 고르지 않은 선, 윤곽의 결손, 마른 잉크 부족, 압력 불균형, 1~2mm의 가벼운 오차 색상 오프셋을 구현하세요. 따뜻한 베이지색 오래된 무광 종이를 배경으로 사용하세요.",
    "Style F: 문자 하프톤 콜라주 (ASCII Halftone)": "피사체를 아스키 문자(. : / | + = # @)와 검은 복사 하프톤 도트가 섞인 실험적인 콜라주 형태로 재구성하세요. 찢어진 사진 조각, 등폭 ASCII 문자, 오버프린트 선으로 화면을 구성하며, 문자는 피사체의 명암과 부피를 따라 배열되어야 합니다. 따뜻한 회색 종이색과 검은 잉크, 소량의 교정용 빨간색 마크만 사용하세요."
}

uploaded_file = st.file_uploader("변환할 스냅 사진을 올려주세요 (JPG, PNG)", type=["jpg", "png", "jpeg"])
selected_style = st.selectbox("포스터 화풍 선택:", list(ai_prompts.keys()))

st.header("📝 텍스트 설정")
col1, col2 = st.columns(2)
with col1:
    custom_title = st.text_input("메인 타이틀", "CAMERA PAL")
with col2:
    custom_subtitle = st.text_input("서브 타이틀/번호", "PHOTO PLAY 01")
custom_desc = st.text_input("관찰 문구 / 설명", "A small lens follows every curious step.")

def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def call_fal_api(base64_img, prompt, api_key):
    url = "https://fal.run/fal-ai/flux/dev/image-to-image"
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "image_url": f"data:image/jpeg;base64,{base64_img}",
        "prompt": prompt,
        "strength": 0.65, # 원본의 형태(사람, 건물 등)를 적당히 유지하면서 화풍만 완벽히 바꾸는 최적의 수치
        "guidance_scale": 7.5
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['images'][0]['url']
    else:
        st.error(f"API 에러 발생: {response.text}")
        return None

if st.button("✨ 포스터 생성하기", type="primary"):
    if not uploaded_file:
        st.warning("사진을 업로드해주세요!")
    elif not fal_api_key:
        st.warning("사이드바에 Fal.ai API 키를 입력해주세요!")
    else:
        with st.spinner("파이썬이 레이아웃을 구성하고, AI가 화풍을 변환하고 있습니다..."):
            try:
                # 1. 원본 이미지 준비
                orig_img = Image.open(uploaded_file).convert("RGB")
                
                # 가로/세로 비율에 맞춰 1200x900(상단용 4:3 비율)으로 예쁘게 자르기
                top_img = ImageOps.fit(orig_img, (1200, 900), Image.Resampling.LANCZOS)
                
                # 2. 하단용 AI 화풍 이미지 생성
                # AI가 레이아웃 고민 없이 온전히 그림 퀄리티에만 집중하도록 사용자 원문의 화풍 지시만 보냄
                b64_img = image_to_base64(top_img)
                ai_prompt = ai_prompts[selected_style]
                ai_img_url = call_fal_api(b64_img, ai_prompt, fal_api_key)
                
                if ai_img_url:
                    ai_response = requests.get(ai_img_url)
                    ai_img = Image.open(io.BytesIO(ai_response.content)).convert("RGB")
                    # AI 결과물도 완벽한 합성을 위해 1200x900으로 맞춤
                    ai_img = ImageOps.fit(ai_img, (1200, 900), Image.Resampling.LANCZOS)
                    
                    # 3. 스마트 파이썬 조립 (1200 x 2000 고해상도 갤러리 포스터 캔버스)
                    # 상단 900 (원본), 하단 900 (AI 화풍), 밑바닥 여백 200 (텍스트용)
                    final_canvas = Image.new('RGB', (1200, 2000), color="#F7F5F0") # 따뜻한 갤러리 종이색
                    
                    # 원본 100% 훼손 없이 상단 부착
                    final_canvas.paste(top_img, (0, 0))
                    # AI 화풍 온전하게 하단 부착 (잘림 방지)
                    final_canvas.paste(ai_img, (0, 900))
                    
                    # 4. 하단 여백에 타이포그래피 예쁘게 인쇄
                    draw = ImageDraw.Draw(final_canvas)
                    try:
                        font_large = ImageFont.truetype("Arial", 45) # 기본 폰트 시도
                        font_small = ImageFont.truetype("Arial", 28)
                    except:
                        font_large = ImageFont.load_default()
                        font_small = ImageFont.load_default()
                        
                    draw.text((80, 1840), custom_title, fill="#222222", font=font_large)
                    draw.text((80, 1910), custom_subtitle, fill="#555555", font=font_small)
                    draw.text((500, 1910), custom_desc, fill="#333333", font=font_small)
                    
                    st.success("스마트 합성 포스터 생성 완료!")
                    st.image(final_canvas, caption="원본 보존 + AI 화풍이 완벽하게 공존하는 포스터", use_container_width=True)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
