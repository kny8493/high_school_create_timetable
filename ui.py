import streamlit as st
import pandas as pd
from data import settings, subjects, teachers, selection_groups, fixed_slots
from algorithm import TimetableManager, ValidationManager

# -----------------------------
# 시각화 모듈
# -----------------------------
class VisualizationManager:
    """시간표 시각화를 담당하는 클래스"""
    
    def __init__(self, settings):
        self.settings = settings
        
        # 과목 그룹별 색상 정의
        self.subject_group_colors = {
            # 기본 항목
            "empty": 'background-color: #f0f0f0',
            "자습": 'background-color: #e9ecef',
            "창체": 'background-color: #d4edda',
            
            # 선택 그룹
            "선택A": 'background-color: #ffcccb',  # 연한 빨간색
            "선택B": 'background-color: #ffec99',  # 연한 노란색
            "선택C": 'background-color: #a8d8ea',  # 연한 파란색
            "선택D": 'background-color: #d8b5ff',  # 연한 보라색
            
            # 국어 계열
            "국어계열": 'background-color: #fff3cd',  # 노란색 계열
            
            # 수학 계열
            "수학계열": 'background-color: #d1ecf1',  # 파란색 계열
            
            # 영어 계열
            "영어계열": 'background-color: #f8d7da',  # 빨간색 계열
            
            # 과학 계열
            "과학계열": 'background-color: #e2e3e5',  # 회색 계열
            
            # 사회 계열
            "사회계열": 'background-color: #ffe0b2',  # 주황색 계열
            
            # 제2외국어 계열
            "외국어계열": 'background-color: #c8e6c9',  # 초록색 계열
            
            # 예체능 계열
            "예체능계열": 'background-color: #bbdefb',  # 하늘색 계열
            
            # 기타 계열
            "기타계열": 'background-color: #d7ccc8'  # 갈색 계열
        }
        
        # 과목별 그룹 매핑
        self.subject_to_group = {
            # 국어 계열 과목
            "국어": "국어계열",
            "문학": "국어계열",
            "독서": "국어계열",
            "화법과 작문": "국어계열",
            "언어와 매체": "국어계열",
            
            # 수학 계열 과목
            "수학": "수학계열",
            "수학Ⅰ": "수학계열",
            "수학Ⅱ": "수학계열",
            "확률과 통계": "수학계열",
            "미적분": "수학계열",
            "기하": "수학계열",
            
            # 영어 계열 과목
            "영어": "영어계열",
            "영어Ⅰ": "영어계열",
            "영어Ⅱ": "영어계열",
            "영어 회화": "영어계열",
            "영어 독해와 작문": "영어계열",
            
            # 과학 계열 과목
            "과학": "과학계열",
            "통합과학": "과학계열",
            "물리학Ⅰ": "과학계열",
            "화학Ⅰ": "과학계열",
            "생명과학Ⅰ": "과학계열",
            "지구과학Ⅰ": "과학계열",
            "물리학Ⅱ": "과학계열",
            "화학Ⅱ": "과학계열",
            "생명과학Ⅱ": "과학계열",
            "지구과학Ⅱ": "과학계열",
            
            # 사회 계열 과목
            "사회": "사회계열",
            "통합사회": "사회계열",
            "한국사": "사회계열",
            "세계사": "사회계열",
            "경제": "사회계열",
            "정치와 법": "사회계열",
            "사회·문화": "사회계열",
            "생활과 윤리": "사회계열",
            "윤리와 사상": "사회계열",
            "한국지리": "사회계열",
            "세계지리": "사회계열",
            "역사": "사회계열",
            
            # 제2외국어 계열
            "중국어Ⅰ": "외국어계열",
            "일본어Ⅰ": "외국어계열",
            "독일어Ⅰ": "외국어계열",
            "프랑스어Ⅰ": "외국어계열",
            "스페인어Ⅰ": "외국어계열",
            "중국어Ⅱ": "외국어계열",
            "일본어Ⅱ": "외국어계열",
            
            # 예체능 계열
            "체육": "예체능계열",
            "음악": "예체능계열",
            "미술": "예체능계열",
            "연극": "예체능계열",
            
            # 기타 계열
            "정보": "기타계열",
            "프로그래밍/Python": "기타계열",
            "진로": "기타계열"
        }
    
    def generate_teacher_timetable_view(self, teacher_schedule):
        """교사별 시간표 뷰 생성"""
        result = {}
        for teacher, schedule in teacher_schedule.items():
            df = pd.DataFrame(index=[f"{i+1}교시" for i in range(7)], columns=self.settings['days'])
            for day in self.settings['days']:
                for i in range(7):
                    df.loc[f"{i+1}교시", day] = schedule[day][i]
            result[teacher] = df
        return result
    
    def display_all_class_timetables(self, timetable, grade, classes):
        """특정 학년의 모든 반 시간표를 표시"""
        col_count = min(3, classes)
        
        cols = st.columns(col_count)
        
        for cls in range(1, classes + 1):
            col_idx = (cls - 1) % col_count
            key = (grade, cls)
            
            with cols[col_idx]:
                st.subheader(f"{grade}학년 {cls}반 시간표")
                if key in timetable:
                    # 색상으로 과목 표시
                    styled_df = timetable[key].T.style.apply(self.color_subjects, axis=None)
                    st.dataframe(styled_df, height=300, use_container_width=True)
                else:
                    st.warning("시간표가 존재하지 않습니다.")
    
    def color_subjects(self, df):
        """시간표에 과목별 색상 적용"""
        styles = pd.DataFrame('', index=df.index, columns=df.columns)
        
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                val = df.iloc[i, j]
                
                # 빈 셀인 경우
                if val == "":
                    styles.iloc[i, j] = self.subject_group_colors["empty"]
                    continue
                
                # 선택 그룹인 경우 (선택A, 선택B, 선택C, 선택D)
                if val in ["선택A", "선택B", "선택C", "선택D"]:
                    styles.iloc[i, j] = self.subject_group_colors[val]
                    continue
                
                # 자습, 창체인 경우
                if val in ["자습", "창체"]:
                    styles.iloc[i, j] = self.subject_group_colors[val]
                    continue
                
                # 과목 그룹 매핑을 확인하여 색상 적용
                for subject_prefix, group in self.subject_to_group.items():
                    if subject_prefix in val:  # 과목명이 포함되어 있는지 확인
                        styles.iloc[i, j] = self.subject_group_colors[group]
                        break
                else:
                    # 매핑된 그룹이 없는 경우 기타 계열로 처리
                    styles.iloc[i, j] = self.subject_group_colors["기타계열"]
        
        return styles

# -----------------------------
# UI 모듈
# -----------------------------
class UIManager:
    """UI 표시를 담당하는 클래스"""
    
    def __init__(self):
        self.settings = settings
        self.teachers = teachers
        self.subjects = subjects
        self.selection_groups = selection_groups
        self.fixed_slots = fixed_slots
        
        self.timetable_manager = TimetableManager(
            settings, teachers, subjects, selection_groups, fixed_slots)
        self.validation_manager = ValidationManager(settings)
        self.visualization_manager = VisualizationManager(settings)
    
    def run(self):
        """UI 실행"""
        st.set_page_config(layout="wide")
        st.title("🏫 고등학교 시간표 자동 제작")
        
        st.text("2025 성균관대학교 교육대학원 인공지능융합교육전공")
        st.text("과목: 데이터 과학을 위한 자료구조와 알고리즘")
        st.text("조명: 갓생, 조원: 김나영, 임혜진")
        
        st.markdown("""
        **사용 방법**  
        - '시간표 생성하기' 버튼을 누르면 시간표가 만들어집니다.  
        - 생성에는 약 1분 정도 소요되니 잠시 기다려 주세요.  
        - 오류가 발생하거나 결과가 없으면 버튼을 여러 번 눌러 다시 시도해 주세요.  
        - 시간표 제작은 복잡한 작업이니 여유를 가지고 시도해 주세요.
        """)
     
        
        # 선택 그룹 정보 표시
        with st.expander("선택 그룹 과목 정보", expanded=False):
            st.markdown("""
            ### 2학년 선택 과목 그룹
            - **선택A**: 윤리와 사상, 물리학Ⅰ, 중국어Ⅰ, 일본어Ⅰ
            - **선택B**: 화학Ⅰ, 생명과학Ⅰ, 한국지리, 프로그래밍/Python
            - **선택C**: 정치와 법, 사회·문화, 지구과학Ⅰ
            - **선택D**: 윤리와 사상, 생명과학Ⅰ, 사회·문화
            """)
        
        # 과목 그룹별 색상 정보 표시
        with st.expander("과목 그룹별 색상 정보", expanded=False):
            st.markdown("""
            ### 과목 그룹별 색상
            - **국어계열** (국어, 문학, 독서, 화법과 작문, 언어와 매체)
            - **수학계열** (수학, 수학Ⅰ, 수학Ⅱ, 확률과 통계, 미적분, 기하)
            - **영어계열** (영어, 영어Ⅰ, 영어Ⅱ, 영어 회화, 영어 독해와 작문)
            - **과학계열** (과학, 물리학Ⅰ, 화학Ⅰ, 생명과학Ⅰ, 지구과학Ⅰ 등)
            - **사회계열** (사회, 역사, 경제, 정치와 법, 사회·문화, 윤리와 사상, 한국지리 등)
            - **외국어계열** (중국어Ⅰ, 일본어Ⅰ, 독일어Ⅰ, 프랑스어Ⅰ 등)
            - **예체능계열** (체육, 음악, 미술, 연극)
            - **기타계열** (정보, 프로그래밍/Python, 진로 등)
            """)
            
            # 색상 샘플 표시
            st.subheader("색상 샘플")
            colors = {
                "국어계열": "#fff3cd",
                "수학계열": "#d1ecf1",
                "영어계열": "#f8d7da",
                "과학계열": "#e2e3e5",
                "사회계열": "#ffe0b2",
                "외국어계열": "#c8e6c9",
                "예체능계열": "#bbdefb",
                "기타계열": "#d7ccc8",
                "선택A": "#ffcccb",
                "선택B": "#ffec99",
                "선택C": "#a8d8ea",
                "선택D": "#d8b5ff",
                "자습": "#e9ecef",
                "창체": "#d4edda"
            }
            
            color_cols = st.columns(4)
            idx = 0
            for group, color in colors.items():
                with color_cols[idx % 4]:
                    st.markdown(f'<div style="background-color: {color}; padding: 10px; margin: 5px; border-radius: 5px;">{group}</div>', unsafe_allow_html=True)
                idx += 1
        
        # 빈칸 채우기 옵션
        fill_empty = st.checkbox("빈 교시를 '자습'으로 표시", value=True)
        
        # 시간표 생성 버튼
        if st.button("시간표 생성하기", key="generate_timetable"):
            with st.spinner("시간표를 생성 중입니다..."):
                # 시간표 생성
                timetable, teacher_schedule = self.timetable_manager.create_timetable()
                
                # 후처리
                if fill_empty:
                    timetable = self.timetable_manager.post_process_timetable(timetable, fill_empty)
                
                # 부가 정보 계산
                teacher_views = self.visualization_manager.generate_teacher_timetable_view(teacher_schedule)
                teacher_hours = self.validation_manager.calculate_teacher_hours(teacher_schedule)
                
                # 세션 스테이트에 결과 저장
                st.session_state.timetable = timetable
                st.session_state.teacher_schedule = teacher_schedule
                st.session_state.teacher_views = teacher_views
                st.session_state.teacher_hours = teacher_hours
                
                st.success("✅ 시간표 생성 완료!")
        
        # 시간표가 생성되었을 때만 표시
        if 'timetable' in st.session_state:
            self.display_timetables()
    
    def display_timetables(self):
        """시간표 및 분석 정보 표시"""
        timetable = st.session_state.timetable
        teacher_schedule = st.session_state.teacher_schedule
        teacher_views = st.session_state.teacher_views
        teacher_hours = st.session_state.teacher_hours
        
        # 탭 설정
        tab1, tab2, tab3 = st.tabs(["모든 학급 시간표", "교사별 시간표", "분석 정보"])
        
        with tab1:
            # 학년 선택 (탭 형식)
            grade_tabs = st.tabs([f"{grade}학년" for grade in self.settings['grades'].keys()])
            
            for i, grade in enumerate(self.settings['grades'].keys()):
                with grade_tabs[i]:
                    # 각 학년별 모든 학급 시간표 표시
                    self.visualization_manager.display_all_class_timetables(
                        timetable, grade, self.settings['grades'][grade])
        
        with tab2:
            selected_teacher = st.selectbox("교사 선택", list(teacher_views.keys()), key="teacher_select")
        
            st.subheader(f"👨‍🏫 {selected_teacher} 시간표 (담당 시수: {teacher_hours[selected_teacher]}시간)")
            st.dataframe(teacher_views[selected_teacher], height=300, use_container_width=True)
    
        with tab3:
            self.display_analysis(timetable, teacher_schedule)
    
    def display_analysis(self, timetable, teacher_schedule):
        """분석 정보 표시"""
        # 시수 완료 검증 및 표시
        missing_hours = self.validation_manager.check_subject_hours_completed(
            timetable, self.teachers, self.selection_groups)
        if missing_hours:
            st.error("⚠️ 일부 과목의 시수가 부족합니다!")
            missing_data = []
            for (subject, grade, cls), (required, assigned) in missing_hours.items():
                missing_data.append({
                    "과목": subject,
                    "학년": grade,
                    "반": cls,
                    "배정 시수": assigned,
                    "필요 시수": required,
                    "부족 시수": required - assigned
                })
            
            if missing_data:
                st.dataframe(pd.DataFrame(missing_data).sort_values(by="부족 시수", ascending=False), 
                            height=200, use_container_width=True)
        else:
            st.success("✅ 모든 과목이 필요한 시수만큼 정확히 배치되었습니다.")
        
        # 연속 수업 시간 분석 결과 표시
        st.subheader("교사별 연속 수업 시간 분석")
        consecutive_analysis = self.validation_manager.analyze_consecutive_teaching(teacher_schedule)
        consecutive_df = pd.DataFrame({
            "교사": list(consecutive_analysis.keys()),
            "최대 연속 수업 시간": list(consecutive_analysis.values())
        })
        consecutive_df = consecutive_df.sort_values("최대 연속 수업 시간", ascending=False)
        st.dataframe(consecutive_df, height=300, use_container_width=True)