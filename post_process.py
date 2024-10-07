import json

def extract_country_and_clean_location(position_location):
    # '[map]' 부분 제거
    cleaned_location = position_location.replace('[map]', '').strip()
    
    # 특정 예외 국가명 리스트
    special_cases = {
        'Korea, The Republic of': 'Republic of Korea',
        # 필요한 다른 예외 케이스들을 여기에 추가할 수 있습니다.
    }
    
    # 예외 국가명이 위치 정보에 포함되어 있는지 확인
    for special_case in special_cases:
        if special_case in cleaned_location:
            country = special_cases[special_case]
            # 국가명을 제거한 위치 정보
            cleaned_location = cleaned_location.replace(special_case, '').strip(', ').strip()
            return cleaned_location, country
    
    # 주소를 쉼표로 분리
    parts = [part.strip() for part in cleaned_location.split(',')]
    
    # 국가명 추출 (마지막 부분)
    if parts:
        country = parts[-1]
        # 국가명을 제거한 위치 정보
        cleaned_location = ', '.join(parts[:-1]).strip()
    else:
        country = ''
    
    return cleaned_location, country

def update_jobs_file(input_filename, output_filename):
    # 기존 데이터를 읽어옵니다.
    with open(input_filename, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    # 각 공고에 대해 처리
    for job in jobs:
        position_location = job.get('position_location', '')
        if position_location:
            cleaned_location, country = extract_country_and_clean_location(position_location)
            job['position_location'] = cleaned_location
            job['country'] = country
        else:
            job['country'] = ''
    
    # 수정된 데이터를 저장합니다.
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
if __name__ == "__main__":
    input_filename = "data/physics_postdocs.json"
    output_filename = "data/physics_postdocs_updated.json"
    update_jobs_file(input_filename, output_filename)
