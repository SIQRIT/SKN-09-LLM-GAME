import streamlit as st
import os
import time
import random
from dotenv import load_dotenv
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="다람쥐 연대기",
    page_icon="🐿️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------- #
# 함수 정의 (기존 코드와 동일)
# -------------------- #
def calculate_alignment_score(alignment):
    """성향에 따른 점수를 계산합니다."""
    order_chaos = {"질서": 50, "중립": 0, "혼돈": -50}
    good_evil = {"선": 50, "중립": 0, "악": -50}
    return order_chaos[alignment[0]] + good_evil[alignment[1]]

def generate_alignment_matrix(companions):
    """동료 후보를 성향 매트릭스에 랜덤하게 배치합니다."""
    matrix = {
        ("질서", "선"): [], ("질서", "중립"): [], ("질서", "악"): [],
        ("중립", "선"): [], ("중립", "중립"): [], ("중립", "악"): [],
        ("혼돈", "선"): [], ("혼돈", "중립"): [], ("혼돈", "악"): []
    }
    for companion in companions:
        alignment = (random.choice(["질서", "중립", "혼돈"]), random.choice(["선", "중립", "악"]))
        matrix[alignment].append(companion)
    return matrix

def get_companion_alignment(matrix, companion):
    """동료의 성향을 매트릭스에서 찾습니다."""
    for alignment, companions in matrix.items():
        if companion in companions:
            return alignment
    return None

def calculate_party_personality(party_companions, companion_matrix):
    """파티의 인성 점수와 레벨을 계산합니다."""
    party_score = 0
    for companion in party_companions:
        alignment = get_companion_alignment(companion_matrix, companion)
        if alignment: # 성향 정보가 있을 경우에만 점수 계산
            party_score += calculate_alignment_score(alignment)

    if party_score >= 200:
        party_level = "성인군자 클럽"
    elif 100 <= party_score < 200:
        party_level = "건실한 청년들"
    elif -100 < party_score < 100:
        party_level = "일반적인 사회"
    elif -200 < party_score <= -100:
        party_level = "불효자식 모임"
    else: # party_score <= -200
        party_level = "금쪽이 짐승들"
    return party_score, party_level

# -------------------- #
# 이벤트 처리 함수 (랜덤 추출 중복 문제 해결, 코드 재출력)
# -------------------- #
def process_event_2(left_column, right_column):
    with left_column:
        st.subheader("이벤트 조우: 3인조 거지")
        event_container = left_column.container()
        with event_container:
            st.write(st.session_state.current_event_text)
            st.write("길을 가던 용사 남윤진과 동료들은 허름한 행색의 3인조 거지를 만났습니다.")
            st.info("거지들은 배고픔에 지쳐 쓰러지기 직전입니다. 과연 용사님은 어떤 선택을 할 것인가?")

        if not st.session_state.event2_triggered:
            with left_column.container():
                if st.button("3인조 거지를 구제하기"):
                    st.session_state.event2_triggered = True
                    st.session_state.show_narration_text = True

                    available_beggars = [
                        comp
                        for comp in st.session_state.companions
                        if comp not in st.session_state.party
                        and comp not in st.session_state.defeated_enemies
                    ]
                    if len(available_beggars) < 3:
                        st.warning("⚠️ 이벤트 진행 불가: 선택 가능한 동료 후보가 부족합니다. ⚠️")
                        st.session_state.event2_beggars = []
                        st.session_state.event2_result_text = "안타깝게도, 거지 이벤트에 참여할 동료 후보가 부족하여 이벤트가 진행되지 않았습니다."
                    else:
                        beggars = random.sample(available_beggars, 3)
                        st.session_state.event2_beggars = beggars
                        st.session_state.defeated_enemies.extend(beggars)
                        party_level = st.session_state.party_level

                        if party_level == "성인군자 클럽":
                            st.session_state.total_score += 20
                        elif party_level == "건실한 청년들":
                            st.session_state.total_score += 10
                        elif party_level == "일반적인 사회":
                            st.session_state.total_score += 0
                        elif party_level == "불효자식 모임":
                            st.session_state.total_score -= 5
                        elif party_level == "금쪽이 짐승들":
                            st.session_state.total_score -= 10
                        else:
                            event_result_text = "**오류**: 파티 인성 레벨을 불러오는 데 실패했습니다. party_level 값을 확인해주세요."
                        st.session_state.current_event_text = "다음 이벤트: 3인조 깡패의 습격!"
                        st.rerun()

        elif st.session_state.show_narration_text:
            event_result_text = st.session_state.event2_result_text
            event_result_text_str = str(event_result_text)
            st.markdown(event_result_text_str)

            beggars = st.session_state.event2_beggars
            if beggars:
                st.write(f"**3인조 거지**: {', '.join(beggars)}")
            party_level = st.session_state.party_level
            st.write(f"**현재 파티 인성 수준**: {party_level} (총 점수: {st.session_state.total_score})")

        create_next_event_button(
            left_column, 2, "다음 이벤트: 3인조 깡패의 습격!", st.session_state.event2_triggered
        )

def process_event_3(left_column, right_column):
    with left_column:
        st.subheader("이벤트 조우: 3인조 깡패의 습격!")
        event_container = left_column.container()
        with event_container:
            st.write(st.session_state.current_event_text)
            st.write("용사 남윤진과 동료들은 불량스러운 3인조 깡패와 마주쳤습니다!")
            st.info("깡패들은 주변 사람들에게 행패를 부리고 괴롭히고 있습니다! 용사님은 어떻게 하시겠습니까?")

        if not st.session_state.event3_triggered:
            with left_column.container():
                if st.button("3인조 깡패를 상대하기"):
                    st.session_state.event3_triggered = True

                    available_bullies = [
                        comp
                        for comp in st.session_state.companions
                        if comp not in st.session_state.party
                        and comp not in st.session_state.defeated_enemies
                    ]
                    if len(available_bullies) < 3:
                        st.warning("⚠️ 이벤트 진행 불가: 선택 가능한 동료 후보가 부족합니다. ⚠️")
                        st.session_state.event3_bullies = []
                        st.session_state.event3_result_text = (
                            "안타깝게도, 깡패 이벤트에 참여할 동료가 부족하여 이벤트가 진행되지 않았습니다."
                        )
                    else:
                        bullies = random.sample(available_bullies, 3)
                        st.session_state.event3_bullies = bullies
                        st.session_state.defeated_enemies.extend(bullies)
                        party_level = st.session_state.party_level

                        if party_level == "성인군자 클럽":
                            st.session_state.total_score += 20
                        elif party_level == "건실한 청년들":
                            st.session_state.total_score += 10
                        elif party_level == "일반적인 사회":
                            st.session_state.total_score += 0
                        elif party_level == "불효자식 모임":
                            st.session_state.total_score -= 5
                        elif party_level == "금쪽이 짐승들":
                            st.session_state.total_score -= 10

                        st.session_state.current_event_text = "다음 이벤트: 3인조 도적의 습격!"
                        st.rerun()

        elif st.session_state.event3_triggered:
            with event_container:
                event_result_text = st.session_state.event3_result_text
                bullies = st.session_state.event3_bullies

                st.write(event_result_text)
                st.write(f"**3인조 깡패**: {', '.join(bullies)}")
                party_level = st.session_state.party_level
                st.write(f"**현재 파티 수준**: {party_level} (총 점수: {st.session_state.total_score})")

        create_next_event_button(
            left_column, 3, "4번째 이벤트: 3인조 도적의 습격!", st.session_state.event3_triggered
        )

def process_event_4(left_column, right_column): # 이벤트 4 처리 함수
    with left_column:
        st.subheader("이벤트 조우: 3인조 도적의 습격!")
        event_container = left_column.container()
        with event_container:
            st.write(st.session_state.current_event_text)
            st.write("용사 남윤진과 동료들은 험악한 인상의 3인조 도적과 마주쳤습니다!")
            st.info("도적들은 칼을 빼 들고 금품을 요구하고 있습니다! 용사님은 이 위기를 어떻게 헤쳐나갈 것인가?")

        if not st.session_state.event4_triggered:
            with left_column.container():
                if st.button("3인조 도적과 전투하기"):
                    st.session_state.event4_triggered = True

                    available_thieves = [comp for comp in st.session_state.companions if comp not in st.session_state.party and comp not in st.session_state.defeated_enemies] # 파티에 없고, 격파되지 않은 동료 중에서 선택
                    if len(available_thieves) < 3: # 선택 가능한 도적 수가 3명 미만일 경우 처리
                        st.warning("⚠️ 이벤트 진행 불가: 선택 가능한 동료 후보가 부족합니다. ⚠️") # 경고 메시지 표시
                        st.session_state.event4_thieves = [] # 빈 리스트 저장
                        st.session_state.event4_result_text = "안타깝게도, 도적 이벤트에 참여할 동료가 부족하여 이벤트가 진행되지 않았습니다." # 결과 텍스트 저장
                    else:
                        thieves = random.sample(available_thieves, 3) # 선택 가능한 동료 중에서 3명 무작위 선택
                        st.session_state.event4_thieves = thieves # 선택된 도적 리스트 저장
                        st.session_state.defeated_enemies.extend(thieves)
                        party_level = st.session_state.party_level

                        if party_level == "성인군자 클럽":
                            st.session_state.total_score += 20
                        elif party_level == "건실한 청년들":
                            st.session_state.total_score += 10
                        elif party_level == "일반적인 사회":
                            st.session_state.total_score += 0
                        elif party_level == "불효자식 모임":
                            st.session_state.total_score -= 5
                        elif party_level == "금쪽이 짐승들":
                            st.session_state.total_score -= 10

                        st.session_state.current_event_text = "다음 이벤트: 마왕 사천왕의 습격!" # 다음 이벤트 텍스트 설정
                        st.rerun()

        elif st.session_state.event4_triggered:
            with event_container:
                event_result_text = st.session_state.event4_result_text # 저장된 결과 텍스트 사용
                thieves = st.session_state.event4_thieves # 저장된 도적 리스트 사용

                st.write(event_result_text)
                if thieves: # 도적 리스트가 비어있지 않을 경우만 표시
                    st.write(f"**3인조 도적**: {', '.join(thieves)}")
                party_level = st.session_state.party_level
                st.write(f"**현재 파티 인성 수준**: {party_level} (총 점수: {st.session_state.total_score})")

            create_next_event_button(left_column, 4, "다음 이벤트: 마왕 사천왕의 습격!", st.session_state.event4_triggered)


def process_event_5(left_column, right_column): # 이벤트 5 처리 함수
    with left_column:
        st.subheader("이벤트 조우: 마왕 사천왕의 습격!")
        event_container = left_column.container()
        with event_container:
            st.write(st.session_state.current_event_text)
            st.write("용사 남윤진과 동료들은 마왕의 사천왕이 모습을 드러냈습니다! 4명의 강력한 적들은 용사 파티를 시험하려 합니다.")
            st.info("마왕의 사천왕은 강력한 힘을 가지고 있습니다! 용사님과 동료들은 힘을 합쳐 사천왕을 격파해야 합니다!")

        if not st.session_state.event5_triggered:
            with left_column.container():
                if st.button("마왕 사천왕 이벤트 진행"):
                    st.session_state.event5_triggered = True

                    available_four_kings = [comp for comp in st.session_state.companions if comp not in st.session_state.party and comp not in st.session_state.defeated_enemies] # 파티에 없고, 격파되지 않은 동료 중에서 선택
                    if len(available_four_kings) < 4: # 선택 가능한 사천왕 수가 4명 미만일 경우 처리
                        st.warning("⚠️ 이벤트 진행 불가: 선택 가능한 동료 후보가 부족합니다. ⚠️") # 경고 메시지 표시
                        st.session_state.event5_four_kings = [] # 빈 리스트 저장
                        st.session_state.event5_result_text = "안타깝게도, 사천왕 이벤트에 참여할 동료가 부족하여 이벤트가 진행되지 않았습니다." # 결과 텍스트 저장
                    else:
                        four_kings = random.sample(available_four_kings, 4) # 선택 가능한 동료 중에서 4명 무작위 선택
                        st.session_state.event5_four_kings = four_kings # 선택된 사천왕 리스트 저장
                        st.session_state.defeated_enemies.extend(four_kings)
                        king_titles = ["마왕의 왼팔", "마왕의 오른팔", "마왕의 왼다리", "마왕의 오른다리"]
                        st.session_state.event5_king_name_titles = [f"{title} {name}" for title, name in zip(king_titles, four_kings)] # 사천왕 이름+칭호 리스트 저장
                        party_level = st.session_state.party_level

                        if party_level == "성인군자 클럽":
                            st.session_state.total_score += 30
                        elif party_level == "건실한 청년들":
                            st.session_state.total_score += 20
                        elif party_level == "일반적인 사회":
                            st.session_state.total_score += 10
                        elif party_level == "불효자식 모임":
                            st.session_state.total_score += 0
                        elif party_level == "금쪽이 짐승들":
                            st.session_state.total_score -= 10

                        st.session_state.current_event_text = "최종 이벤트: 대마왕과의 결전!" # 다음 이벤트 텍스트 설정
                        st.rerun()

        elif st.session_state.event5_triggered:
            with event_container:
                event_result_text = st.session_state.event5_result_text # 저장된 결과 텍스트 사용
                king_name_titles = st.session_state.event5_king_name_titles # 저장된 사천왕 이름+칭호 리스트 사용

                st.write(event_result_text)
                st.write(f"**마왕의 사천왕**: {', '.join(king_name_titles)}")
                party_level = st.session_state.party_level
                st.write(f"**현재 파티 인성 수준**: {party_level} (총 점수: {st.session_state.total_score})")

            create_next_event_button(left_column, 5, "최종 이벤트: 대마왕과의 결전!", st.session_state.event5_triggered)

def process_event_6(left_column, right_column): # 이벤트 6 처리 함수 (최종 대마왕)
    with left_column:
        st.subheader("이벤트 조우: 대마왕과의 결전!")
        event_container = left_column.container()
        with event_container:
            st.write(st.session_state.current_event_text)
            st.write("드디어 최종 보스, 대마왕이 나타났습니다! 세계의 운명을 건 마지막 결전이 눈앞에 펼쳐집니다!")
            st.error("대마왕은 상상 이상의 강력한 존재입니다! 모든 힘을 쏟아부어 대마왕을 쓰러뜨리세요!")

        if not st.session_state.event6_triggered:
            with left_column.container():
                if st.button("대마왕과의 최종 결전"):
                    st.session_state.event6_triggered = True
                    st.rerun()
        elif st.session_state.event6_triggered:
            with event_container:
                demon_king_candidate = [comp for comp in st.session_state.companions if comp not in st.session_state.party and comp not in st.session_state.defeated_enemies] # 파티에 없고 격파되지 않은 동료 중에서 선택
                if demon_king_candidate:
                    st.session_state.demon_king = demon_king_candidate[0]
                else:
                    st.session_state.demon_king = "??? (오류)"

                if st.session_state.demon_king != "??? (오류)":
                    st.error(f"💥 최종 보스, 대마왕 {st.session_state.demon_king}이(가) 드디어 모습을 드러냈습니다!!! 💥")
                    left_column.error(f"😈 **대마왕 {st.session_state.demon_king}**: 크하하하! 어리석은 인간들아, 드디어 최후의 순간이 왔다!")

                    party_level = st.session_state.party_level

                    if party_level == "성인군자 클럽":
                        event_result_text = f"**정의구현 엔딩**: 성인군자 클럽 - 용사 {st.session_state.hero_name} 파티는 대마왕 {st.session_state.demon_king}을(를) **물리적인 자비심**으로 감화시키는 데 성공했습니다! 대마왕은 스스로 **악행을 뉘우치고** 세계 평화에 **헌신**할 것을 맹세했습니다! (인성 수준: 성인군자 클럽 **유지**, 점수 +50!!!)"
                        st.session_state.total_score += 50
                        left_column.balloons()
                        left_column.success(f"🏆 {event_result_text} 🏆")
                        left_column.success(f"🌟 **정의구현 엔딩**: 성인군자 클럽 - 용사 파티는 영웅을 넘어 **무신**으로 칭송받으며, 세계는 **영원한 황금 시대**를 맞이했습니다. 🌟")
                        left_column.success(f"🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️ Ending Credits 🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️")
                        left_column.success(f"거지 이벤트: 용사 파티는 3인조 거지를 **매우 넉넉하게** 도와주었습니다! 인심 좋고 천사 같은 마음에 감동한 거지들은 **눈물**을 흘리며 **최고의 존경**을 표현했습니다.")
                        left_column.success(f"깡패 이벤트: 용사 파티는 3인조 깡패를 **주먹으로 훈계**하여 **눈물**로 **뉘우치게** 만들었습니다! 깡패들은 용사님의 **압도적 무위**에 감복당하여, 새로운 삶을 살 것을 다짐했습니다.")
                        left_column.success(f"도적 이벤트: 용사 파티는 3인조 도적을 **나무 몽둥이로 예의를 주입**시켜 **개과천선**시키는 데 성공했습니다! 도적들은 뉘우침 당하여 용사 파티에게 **깊은 존경**을 표하고, 마을에 **헌신**할 것을 맹세했습니다.")
                        left_column.success(f"사천왕 습격: 용사 파티는 마왕 사천왕을 **오함마로 대화**하여 **정의**를 되찾아주었습니다! 사천왕은 감동당하여 마왕에게 등을 돌리고 세계 평화에 **헌신**할 것을 맹세했습니다!")
                    elif party_level == "건실한 청년들":
                        event_result_text = f"**굳 엔딩**: 건실한 청년들 - 용사 {st.session_state.hero_name} 파티는 대마왕 {st.session_state.demon_king}과의 **운명적인 혈투** 끝에 **승리**했습니다! (인성 수준: 건실한 청년들 **유지**, 점수 +40)"
                        st.session_state.total_score += 40
                        left_column.success(f"🎉 {event_result_text} 🎉")
                        left_column.success(f"⭐ **굳 엔딩**: 건실한 청년들 - 용사 파티는 세계를 구했지만, 칭송은 받지 못하고 **조용히** 사라졌습니다. ⭐")
                        left_column.success(f"🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️ Ending Credits 🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️")
                        left_column.success(f"거지 이벤트: 용사 파티는 3인조 거지를 **넉넉하게** 도와주었습니다! 따뜻한 마음에 감동한 거지들은 **최고의 감사 인사**와 함께 **작은 보답**을 전했습니다.")
                        left_column.success(f"깡패 이벤트: 용사 파티는 3인조 깡패를 **맨주먹**으로 **혼쭐**을 내주었습니다! 깡패들은 용사 파티의 **참교육**에 움찔하며, 잘못을 뉘우치는 듯 했습니다.")
                        left_column.success(f"도적 이벤트: 용사 파티는 3인조 도적과의 전투에서 **압도적인 실력**으로 승리했습니다! 도적들은 용사 파티의 강함에 기겁하며 **가진 것들을 전부 내놓고** 물러났습니다.")
                        left_column.success(f"사천왕 습격: 용사 파티는 마왕 사천왕과의 **뜨거운 몸의 대화**를 나누며 **정정당당한 대결**에서 승리했습니다! 사천왕은 용사 파티의 실력을 인정하고 **존경**을 표했습니다.")
                    elif party_level == "일반적인 사회":
                        event_result_text = f"**노멀 엔딩**: 일반적인 사회 - 용사 {st.session_state.hero_name} 파티는 대마왕 {st.session_state.demon_king}을(를) **필사적인 저항** 끝에 **간신히** 쓰러뜨렸습니다. (인성 수준: 일반적인 사회 **유지**, 점수 +30)"
                        st.session_state.total_score += 30
                        left_column.info(f"😥 {event_result_text} 😥")
                        left_column.info(f"🍀 **노멀 엔딩**: 일반적인 사회 - 대마왕은 사라졌지만, 세계는 혼란에 빠지고 용사 파티의 공적은 **잊혀졌습니다**. 🍀")
                        left_column.info(f"🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️ Ending Credits 🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️")
                        left_column.info(f"거지 이벤트: 용사 파티는 3인조 거지를 **적당히** 도와주었습니다. 거지들은 **굽신거리며** 감사를 표했습니다.")
                        left_column.info(f"깡패 이벤트: 용사 파티는 3인조 깡패를 **죽지 않을 만큼만** 혼내주고 쫓아냈습니다. 깡패들은 **화가 매우** 났지만, 쪽수가 밀려 별 수 없이 물러갔습니다.")
                        left_column.info(f"도적 이벤트: 용사 파티는 3인조 도적과 **치열한 전투** 끝에 간신히 승리하고 심한 욕설을 날렸습니다.")
                        left_column.info(f"사천왕 습격: 용사 파티는 마왕 사천왕과의 **공방합**을 나누며 **힘겨운 전투** 끝에 간신히 승리했습니다.")
                    elif party_level == "불효자식 모임":
                        event_result_text = f"**배드 엔딩**: 불효자식 모임 - 용사 {st.session_state.hero_name} 파티는 대마왕 {st.session_state.demon_king}에게 아부를 떨다 **개수작이 먹히지 않고 패배**했습니다... (인성 수준: 불효자식 모임 **유지**, 점수 -20)"
                        st.session_state.total_score -= 20
                        left_column.warning(f"💥 {event_result_text} 💥")
                        left_column.warning(f"🔥 **배드 엔딩**: 불효자식 모임 - 세계는 **멸망 직전**까지 갔지만, 용사 파티는 겨우 **목숨만 부지**했습니다. 🔥")
                        left_column.warning(f"🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️ Ending Credits 🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️")
                        left_column.warning(f"거지 이벤트: 용사 파티는 3인조 거지를 **매몰차게** 두들겨 팼습니다. 거지들은 **억울한 표정**을 감추지 못했습니다.")
                        left_column.warning(f"깡패 이벤트: 용사 파티는 3인조 깡패와 **으슥한 곳에서** 꽁꽁 묶어두고 **신나게** 두들겨 팼습니다! 깡패들은 **울면서 겨우 도망**쳤지만, 마을 사람들은 **자신들도 맞을까 두려워** 고개를 돌렸습니다.")
                        left_column.warning(f"도적 이벤트: 용사 파티는 3인조 도적과의 전투에서 **고전**했습니다. 살금살금 뒤로 돌아가 **뒷통수를 벽돌로 찍어** 잔악무도하게 승리했지만, 상처뿐인 영광입니다.")
                        left_column.warning(f"사천왕 습격: 용사 파티는 마왕 사천왕과의 전투에서 **중요부위만 때리는** 비겁한 수단을 사용했습니다. 간신히 승리했지만, 찜찜함이 남았습니다.")
                    elif party_level == "금쪽이 짐승들":
                        event_result_text = f"**파멸적 엔딩**: 금쪽이 짐승들 - 용사 {st.session_state.hero_name} 파티는 대마왕 {st.session_state.demon_king}와(과) 함께 세상을 **처참하게 농락**하며 **세계를 멸망**시켰습니다. (인성 수준: 금쪽이 짐승들 **유지**, 점수 -50, 마이너스 점수!!!)"
                        st.session_state.total_score -= 50
                        left_column.error(f"💀 {event_result_text} 💀")
                        left_column.error(f"☠️ **파멸적 엔딩**: 금쪽이 짐승들 - 용사 파티는 **세계 멸망의 원흉**으로 역사에 기록되었습니다. ☠️")
                        left_column.error(f"🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️ Ending Credits 🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️🐿️")
                        left_column.error(f"거지 이벤트: 용사 파티는 3인조 거지를 **동냥 그릇까지** 싹싹 털어먹었습니다! 분노한 거지들은 **저주**를 퍼부으며 원망했으나, 그 소리를 듣고 되돌아온 용사파티에게 **신나게** 두들겨 맞았습니다.")
                        left_column.error(f"깡패 이벤트: 용사 파티는 3인조 깡패와 **친목을 다지며** 온 마을에 **신나게** 불을 질러댔습니다! 마을 사람들은 **울면서 도망**쳤지만, 용사 파티는 텅 빈 마을에 **빈집털이**를 하며 사리사욕을 채웠습니다.")
                        left_column.error(f"도적 이벤트: 용사 파티는 3인조 도적을 사로잡아 **무자비하게** 승차감 좋은 인력거로 만들었습니다! 지나가던 용병들은 악마같은 발상을 한 용사 파티를 **경멸**하게 되었습니다.")
                        left_column.error(f"사천왕 습격: 용사 파티는 마왕 사천왕의 소중한 한정판 애착인형을 **잔인하게** 산산조각 내버렸습니다! 마족들은 공포에 질려 용사 파티를 **쳐다보지도 못하게** 되었습니다.")
                    else:
                        event_result_text = "**오류**: 파티 인성 수준을 불러오는 데 실패했습니다."
                        left_column.error(f"⚠️ {event_result_text} ⚠️")

                    st.write(event_result_text)
                    st.write(f"**대마왕**: {st.session_state.demon_king}")
                    st.write(f"**최종 파티 인성 수준**: {party_level} (총 점수: {st.session_state.total_score})")

                    end_time = time.time()
                    elapsed_time = end_time - st.session_state.start_time
                    left_column.info(f"총 모험 시간: {elapsed_time:.4f} 초")
                    st.session_state.game_over = True

                    # --- "다시하기" 버튼 추가 (여기에 추가) ---
                    if st.button("다시하기"): # "다시하기" 버튼
                        st.session_state['game_started'] = False
                        st.session_state['party'] = []
                        st.session_state['total_score'] = 0
                        st.session_state['prompt'] = ""
                        st.session_state['companion_matrix'] = generate_alignment_matrix(st.session_state['companions']) # 동료 성향 매트릭스 재생성
                        st.session_state['start_time'] = time.time() # 모험 시작 시간 다시 기록
                        st.session_state['bot_responses'] = [] # 봇 응답 기록 초기화
                        st.session_state['companion_responses'] = {} # 동료별 봇 응답 저장 딕셔너리 초기화
                        st.session_state['companion_selections'] = {companion: False for companion in st.session_state['companions']} # 체크박스 상태 초기화
                        st.session_state['party_level'] = "???" # 파티 레벨 초기화
                        st.session_state['events'] = [] # 이벤트 로그 초기화
                        st.session_state['event2_triggered'] = False # 이벤트 2 트리거 초기화
                        st.session_state['event3_triggered'] = False # 이벤트 3 트리거 초기화
                        st.session_state['event4_triggered'] = False # 이벤트 4 트리거 초기화
                        st.session_state['event5_triggered'] = False # 이벤트 5 트리거 초기화
                        st.session_state['event6_triggered'] = False # 이벤트 6 트리거 초기화
                        st.session_state['current_event_text'] = "2번째 이벤트: 3인조 거지" # 시작 이벤트 텍스트 설정
                        st.session_state['defeated_enemies'] = [] # 격파한 적 리스트 초기화
                        st.session_state['game_over'] = False # 게임 오버 상태 초기화
                        st.session_state['event_stage'] = 0 # 이벤트 단계 초기화 (0: 동료 선택)
                        st.session_state['event2_beggars'] = [] # 이벤트 2 거지 리스트 초기화
                        st.session_state['event2_result_text'] = "" # 이벤트 2 결과 텍스트 초기화
                        st.session_state['event3_bullies'] = [] # 이벤트 3 깡패 리스트 초기화
                        st.session_state['event3_result_text'] = "" # 이벤트 3 결과 텍스트 초기화
                        st.session_state['event4_thieves'] = [] # 이벤트 4 도적 리스트 초기화
                        st.session_state['event4_result_text'] = "" # 이벤트 4 결과 텍스트 초기화
                        st.session_state['event5_four_kings'] = [] # 이벤트 5 사천왕 리스트 초기화
                        st.session_state['event5_king_name_titles'] = [] # 이벤트 5 사천왕 이름+칭호 리스트 초기화
                        st.session_state['event5_result_text'] = "" # 이벤트 5 결과 텍스트 초기화
                        st.rerun()

# -------------------- #
# 다음 이벤트 버튼 생성 함수 (수정됨, 코드 재출력)
# -------------------- #
def create_next_event_button(left_column, event_number, next_event_text, event_triggered):
    if event_triggered and event_number < 6 and not st.session_state.game_over: # event_number 6은 최종 이벤트
        with left_column.container():
            if st.button(f"다음 단계 ({event_number+1}단계) 진행"): # 버튼 텍스트 변경
                current_event_state_name = f"event{event_number}_triggered" # 현재 이벤트 상태 변수명
                next_event_state_name = f"event{event_number+1}_triggered" # 다음 이벤트 상태 변수명
                st.session_state[current_event_state_name] = False # **현재 이벤트 트리거 변수를 False로 설정 (종료)**
                st.session_state[next_event_state_name] = False # 다음 이벤트 트리거 초기화 (다시 False로 설정 후 True가 되어야 진행됨)
                st.session_state.current_event_text = next_event_text # 다음 이벤트 텍스트 설정
                st.session_state.event_stage = event_number + 1 # 이벤트 단계 업데이트 (핵심!)
                st.rerun()

# -------------------- #
# Streamlit 앱 UI 및 게임 로직 (체크박스, 컬럼 레이아웃, 동적 정보 업데이트)
# -------------------- #

# --- 초기 설정 (수정됨, 코드 재출력) ---
if 'game_started' not in st.session_state:
    st.session_state['game_started'] = False
if 'party' not in st.session_state:
    st.session_state['party'] = []
if 'total_score' not in st.session_state:
    st.session_state['total_score'] = 0
if 'prompt' not in st.session_state:
    st.session_state['prompt'] = ""
if 'companion_matrix' not in st.session_state:
    st.session_state['companion_matrix'] = None
if 'companions' not in st.session_state:
    st.session_state['companions'] = ["김도연", "김영서", "김우중", "김정훈", "김하늘", "박유진", "박주은", "서예찬", "유지은", "윤환", "이광운", "이다인", "이세진", "이윤재", "이재혁", "임수연", "전성원", "조민훈", "조이현", "최재동", "허정윤"]
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = None
if 'elapsed_time' not in st.session_state:
    st.session_state['elapsed_time'] = 0
if 'demon_king' not in st.session_state:
    st.session_state['demon_king'] = None
if 'companion_selections' not in st.session_state: # 동료 선택 상태 저장
    st.session_state['companion_selections'] = {companion: False for companion in st.session_state['companions']}
if 'party_level' not in st.session_state: # 파티 인성 수준 상태 저장
    st.session_state['party_level'] = "???"
if 'companion_responses' not in st.session_state: # 동료별 봇 응답 저장 딕셔너리
    st.session_state['companion_responses'] = {}
if 'events' not in st.session_state: # 이벤트 로그 저장
    st.session_state['events'] = []
if 'event2_triggered' not in st.session_state: # 이벤트 2 트리거 상태
    st.session_state['event2_triggered'] = False
if 'event3_triggered' not in st.session_state: # 이벤트 3 트리거 상태
    st.session_state['event3_triggered'] = False
if 'event4_triggered' not in st.session_state: # 이벤트 4 트리거 상태
    st.session_state['event4_triggered'] = False
if 'event5_triggered' not in st.session_state: # 이벤트 5 트리거 상태
    st.session_state['event5_triggered'] = False
if 'event6_triggered' not in st.session_state: # 이벤트 6 트리거 상태
    st.session_state['event6_triggered'] = False
if 'current_event_text' not in st.session_state: # 현재 이벤트 텍스트
    st.session_state['current_event_text'] = "2번째 이벤트: 3인조 거지" # 시작 이벤트 텍스트 설정
if 'defeated_enemies' not in st.session_state: # 격파한 적 리스트
    st.session_state['defeated_enemies'] = []
if 'game_over' not in st.session_state: # 게임 오버 상태
    st.session_state['game_over'] = False
if 'hero_name' not in st.session_state: # 용사 이름 (process_event_6 에서 사용)
    st.session_state['hero_name'] = "남윤진" # 용사 이름 초기화 (원하는 이름으로 변경 가능)
if 'event_stage' not in st.session_state: # 현재 이벤트 단계 (추가됨, 코드 재출력)
    st.session_state['event_stage'] = 0 # 0: 동료 선택, 2, 3, 4, 5, 6: 이벤트 단계 (추가됨, 코드 재출력)
if 'event2_beggars' not in st.session_state: # 이벤트 2 거지 리스트 저장 (추가됨)
    st.session_state['event2_beggars'] = []
if 'event2_result_text' not in st.session_state: # 이벤트 2 결과 텍스트 저장 (추가됨)
    st.session_state['event2_result_text'] = ""
if 'event3_bullies' not in st.session_state: # 이벤트 3 깡패 리스트 저장 (추가됨)
    st.session_state['event3_bullies'] = []
if 'event3_result_text' not in st.session_state: # 이벤트 3 결과 텍스트 저장 (추가됨)
    st.session_state['event3_result_text'] = ""
if 'event4_thieves' not in st.session_state: # 이벤트 4 도적 리스트 저장 (추가됨)
    st.session_state['event4_thieves'] = []
if 'event4_result_text' not in st.session_state: # 이벤트 4 결과 텍스트 저장 (추가됨)
    st.session_state['event4_result_text'] = ""
if 'event5_four_kings' not in st.session_state: # 이벤트 5 사천왕 리스트 저장 (추가됨)
    st.session_state['event5_four_kings'] = []
if 'event5_king_name_titles' not in st.session_state: # 이벤트 5 사천왕 이름+칭호 리스트 저장 (추가됨)
    st.session_state['event5_king_name_titles'] = []
if 'event5_result_text' not in st.session_state: # 이벤트 5 결과 텍스트 저장 (추가됨)
    st.session_state['event5_result_text'] = ""

# 환경 변수 로드 및 OpenAI 클라이언트 초기화 (함수 외부에서 한 번만 실행, 코드 재출력)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


# --- UI 레이아웃 ---
st.title("다람쥐 연대기 🐿️")

# 게임 시작 버튼 (코드 재출력)
if not st.session_state['game_started']:
    if st.button("모험 시작!"):
        st.session_state['game_started'] = True
        st.session_state['companion_matrix'] = generate_alignment_matrix(st.session_state['companions']) # 동료 성향 매트릭스 생성 (게임 시작 시 1회)
        st.session_state['start_time'] = time.time() # 모험 시작 시간 기록
        st.session_state['bot_responses'] = [] # 봇 응답 기록 초기화 (이제 사용하지 않음)
        st.session_state['companion_responses'] = {} # 동료별 봇 응답 저장 딕셔너리 초기화
        st.session_state['party'] = [] # 파티 초기화
        st.session_state['total_score'] = 0 # 점수 초기화
        st.session_state['prompt'] = "" # 프롬프트 초기화
        st.session_state['companion_selections'] = {companion: False for companion in st.session_state['companions']} # 체크박스 상태 초기화
        st.session_state['party_level'] = "???" # 파티 레벨 초기화
        st.session_state['events'] = [] # 이벤트 로그 초기화
        st.session_state['event2_triggered'] = False # 이벤트 2 트리거 초기화
        st.session_state['event3_triggered'] = False # 이벤트 3 트리거 초기화
        st.session_state['event4_triggered'] = False # 이벤트 4 트리거 초기화
        st.session_state['event5_triggered'] = False # 이벤트 5 트리거 초기화
        st.session_state['event6_triggered'] = False # 이벤트 6 트리거 초기화
        st.session_state['current_event_text'] = "2번째 이벤트: 3인조 거지" # 시작 이벤트 텍스트 설정
        st.session_state['defeated_enemies'] = [] # 격파한 적 리스트 초기화
        st.session_state['game_over'] = False # 게임 오버 상태 초기화
        st.session_state['event_stage'] = 0 # 이벤트 단계 초기화 (0: 동료 선택)
        st.session_state['event2_beggars'] = [] # 이벤트 2 거지 리스트 초기화
        st.session_state['event2_result_text'] = "" # 이벤트 2 결과 텍스트 초기화
        st.session_state['event3_bullies'] = [] # 이벤트 3 깡패 리스트 초기화
        st.session_state['event3_result_text'] = "" # 이벤트 3 결과 텍스트 초기화
        st.session_state['event4_thieves'] = [] # 이벤트 4 도적 리스트 초기화
        st.session_state['event4_result_text'] = "" # 이벤트 4 결과 텍스트 초기화
        st.session_state['event5_four_kings'] = [] # 이벤트 5 사천왕 리스트 초기화
        st.session_state['event5_king_name_titles'] = [] # 이벤트 5 사천왕 이름+칭호 리스트 초기화
        st.session_state['event5_result_text'] = "" # 이벤트 5 결과 텍스트 초기화
        st.rerun() # 초기 상태를 반영하기 위해 rerun() 추가


if st.session_state['game_started']:
    st.header(f"~ 다람쥐 용사 {st.session_state['hero_name']}의 모험 🐿️ ~") # 용사 이름 표시
    st.write("---")

    left_column, right_column = st.columns(2) # 컬럼 분리

    with left_column: # 왼쪽 컬럼 UI 배치
        # --- 동료 선택 섹션 (checkbox) ---
        if st.session_state['event_stage'] == 0: # 동료 선택 단계 (코드 재출력)
            if len(st.session_state['party']) < 7 and not st.session_state.game_over: # 파티원 수 7명 미만, 게임 오버 아닐 때만 동료 선택 가능
                st.subheader("함께 모험을 떠날 7명의 동료들을 선택해주세요!") # 헤더 텍스트 변경
                col1, col2, col3 = st.columns(3) # 3 컬럼으로 나누어 체크박스 배치
                cols = [col1, col2, col3] # 컬럼 객체 리스트

                for i, companion in enumerate(st.session_state['companions']):
                    col_index = i % 3 # 0, 1, 2 인덱스 순환
                    current_col = cols[col_index] # 현재 컬럼 선택
                    with current_col: # 현재 컬럼에 체크박스 생성
                        st.session_state['companion_selections'][companion] = st.checkbox(companion, key=f"checkbox_{companion}", value=st.session_state['companion_selections'][companion]) # 체크박스 생성 및 상태 저장

                if st.button("동료 영입", key="recruit_button"): # "동료 영입" 버튼 클릭 시 (코드 재출력)
                    selected_companions = [companion for companion, selected in st.session_state['companion_selections'].items() if selected and companion not in st.session_state['party']] # 체크된 동료 목록 생성
                    if not selected_companions:
                        st.warning("선택된 동료가 없습니다. 동료를 선택해주세요.")
                    elif len(st.session_state['party']) + len(selected_companions) > 7:
                        st.warning("최대 7명까지 동료를 영입할 수 있습니다. 선택한 동료 수를 확인해주세요.")
                    elif len(st.session_state['party']) + len(selected_companions) == 7: # 7명 영입 완료 시 이벤트 시작
                        newly_recruited_companions = [] # 새로 영입된 동료 리스트
                        for selected_companion in selected_companions:
                            if selected_companion not in st.session_state['party']: # 중복 영입 방지 (혹시 모를 오류 대비)
                                st.session_state['party'].append(selected_companion)
                                alignment = get_companion_alignment(st.session_state['companion_matrix'], selected_companion)
                                score = calculate_alignment_score(alignment)
                                st.session_state['total_score'] += score

                                # --- 수정된 프롬프트 ---
                                llm_prompt = f"당신은 {selected_companion}입니다. 당신은 {alignment} 성향의 모험가입니다. 당신의 성향을 반영하여 새로운 용사 {st.session_state.hero_name}에게 앞으로의 모험에 대한 짧고 인상적인 한 문장으로 환영 메시지를 생성하세요. 단, 반말로 해야 합니다." # 용사 이름 추가
                                st.session_state['prompt'] = llm_prompt # 프롬프트 덮어쓰기

                                newly_recruited_companions.append({ # 새로 영입된 동료 정보 저장 (더 이상 사용하지 않음)
                                    "name": selected_companion,
                                    "alignment": alignment,
                                    "score": score
                                })

                                # OpenAI API 호출 및 응답 저장 (각 동료별 호출)
                                chat_completion = client.chat.completions.create(
                                    model="gpt-4o-mini", # 또는 다른 OpenAI 모델 선택 / gpt-3.5-turbo
                                    messages=[{"role": "user", "content": st.session_state['prompt']}]
                                )
                                bot_response = chat_completion.choices[0].message.content
                                st.session_state['companion_responses'][selected_companion] = bot_response # 동료별 응답 저장
                                st.session_state['companion_selections'][selected_companion] = False # 영입 후 체크박스 초기화

                            # 파티 인성 수준 업데이트
                            party_score, party_level = calculate_party_personality(st.session_state['party'], st.session_state['companion_matrix'])
                            st.session_state['total_score'] = party_score # 갱신된 파티 점수 적용
                            st.session_state['party_level'] = party_level # 갱신된 파티 레벨 적용
                            st.session_state.party_personality_level = party_level # party_personality_level 업데이트 (이벤트 함수에서 사용)


                        st.session_state['event_stage'] = 2 # 이벤트 2단계로 변경 (추가됨, 코드 재출력)
                        st.session_state['event2_triggered'] = False # 이벤트 2 트리거 초기화 (False로 시작해야 이벤트 진행됨) # 추가됨
                        st.rerun() # 동료 영입 후 UI 업데이트 반영
                    else: # 7명 미만 영입
                        newly_recruited_companions = [] # 새로 영입된 동료 리스트
                        for selected_companion in selected_companions:
                            if selected_companion not in st.session_state['party']: # 중복 영입 방지 (혹시 모를 오류 대비)
                                st.session_state['party'].append(selected_companion)
                                alignment = get_companion_alignment(st.session_state['companion_matrix'], selected_companion)
                                score = calculate_alignment_score(alignment)
                                st.session_state['total_score'] += score

                                # --- 수정된 프롬프트 ---
                                llm_prompt = f"당신은 {selected_companion}입니다. 당신은 {alignment} 성향의 모험가입니다. 당신의 성향을 반영하여 새로운 용사 {st.session_state.hero_name}에게 앞으로의 모험에 대한 짧고 인상적인 한 문장으로 환영 메시지를 생성하세요. 단, 반말로 해야 합니다." # 용사 이름 추가
                                st.session_state['prompt'] = llm_prompt # 프롬프트 덮어쓰기

                                newly_recruited_companions.append({ # 새로 영입된 동료 정보 저장 (더 이상 사용하지 않음)
                                    "name": selected_companion,
                                    "alignment": alignment,
                                    "score": score
                                })

                                # OpenAI API 호출 및 응답 저장 (각 동료별 호출)
                                chat_completion = client.chat.completions.create(
                                    model="gpt-4o-mini", # 또는 다른 OpenAI 모델 선택 / gpt-3.5-turbo
                                    messages=[{"role": "user", "content": st.session_state['prompt']}]
                                )
                                bot_response = chat_completion.choices[0].message.content
                                st.session_state['companion_responses'][selected_companion] = bot_response # 동료별 응답 저장
                                st.session_state['companion_selections'][selected_companion] = False # 영입 후 체크박스 초기화

                        # 파티 인성 수준 업데이트
                        party_score, party_level = calculate_party_personality(st.session_state['party'], st.session_state['companion_matrix'])
                        st.session_state['total_score'] = party_score # 갱신된 파티 점수 적용
                        st.session_state['party_level'] = party_level # 갱신된 파티 레벨 적용
                        st.session_state.party_personality_level = party_level # party_personality_level 업데이트 (이벤트 함수에서 사용)
                        st.rerun() # 동료 영입 후 UI 업데이트 반영


        # --- 이벤트 처리 섹션 (수정됨, 코드 재출력) ---
        if st.session_state['event_stage'] == 2: # 이벤트 2단계 (코드 재출력)
            process_event_2(left_column, right_column) # 이벤트 2 시작
        elif st.session_state['event_stage'] == 3: # 이벤트 3단계 (코드 재출력)
            process_event_3(left_column, right_column) # 이벤트 3 시작
        elif st.session_state['event_stage'] == 4: # 이벤트 4단계 (코드 재출력)
            process_event_4(left_column, right_column) # 이벤트 4 시작
        elif st.session_state['event_stage'] == 5: # 이벤트 5단계 (코드 재출력)
            process_event_5(left_column, right_column) # 이벤트 5 시작
        elif st.session_state['event_stage'] == 6: # 이벤트 6단계 (최종, 코드 재출력)
            process_event_6(left_column, right_column) # 이벤트 6 시작


    with right_column: # 오른쪽 컬럼 UI 배치 (코드 재출력)
        # --- 게임 진행 정보 표시 ---
        st.subheader("현재 파티 정보")
        if st.session_state['party']: # 파티에 동료가 있을 때만 정보 표시
            st.write(f"**현재 파티 점수:** {st.session_state['total_score']} 점") # 파티 점수 먼저 표시
            st.write(f"**파티 인성 수준:** {st.session_state['party_level']}") # 파티 인성 수준 표시
            st.write("---") # UI 구분선
            for companion in st.session_state['party']: # 파티원 정보 순서대로 표시
                alignment = get_companion_alignment(st.session_state['companion_matrix'], companion)
                score = calculate_alignment_score(alignment) # 점수 다시 계산 (혹시 모를 오류 방지)
                st.markdown(f"**{companion}** | {alignment} | {score}점")
                # LLM 응답 찾아서 출력 (companion_responses에서 해당 동료 응답만 가져옴)
                if companion in st.session_state['companion_responses']: # 응답이 있을 경우에만 출력
                    st.write(st.session_state['companion_responses'][companion]) # 해당 동료의 LLM 응답 출력!
                    st.write("-" * 30) # LLM 응답 구분선
            st.write("---") # UI 구분선

        # --- 이벤트 로그 표시 ---
        if st.session_state['events']: # 이벤트가 발생했을 경우에만 표시
            st.subheader("이벤트 로그")
            for event in st.session_state['events']:
                st.write(f"- {event['text']} (점수 변동: {event['score_effect']}점)")
            st.write("---")

        # --- 게임 종료 조건 및 결과 표시 (process_event_6 에서 처리, 코드 재출력) ---
        if st.session_state['event_stage'] == 0 and not st.session_state.game_over: # 파티원 수가 7명 미만일 때 경고 메시지 표시 + 게임 오버 상태 아닐 때만 표시
            st.warning("⚠️ **아직 7명의 동료들을 모두 선택하지 않았습니다.** 용감한 다람쥐 용사를 도울 7명의 동료들을 모아 마왕을 물리치세요! 🐿️", icon="⚠️") # 경고 메시지 강조 및 아이콘 추가
        elif st.session_state.game_over: # 게임 오버 시 결과 표시 제거 (process_event_6 에서 결과 처리)
            pass # process_event_6 에서 게임 결과 및 재시작 버튼 표시
