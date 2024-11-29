import os
import requests
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.conf import settings
import matplotlib
matplotlib.use('Agg')


def search_profession(request):
    if request.method == "POST":
        profession = request.POST.get("profession", "").strip()
        if profession:
            create_skill_images(profession)

            pie_chart_url = os.path.join("media", "pie_chart.png")
            table_url = os.path.join("media", "skills_table.png")

            return render(request, 'search/results.html', {
                "profession": profession,
                "pie_chart_url": pie_chart_url,
                "table_url": table_url,
            })

    return render(request, 'search/search.html')


def create_skill_images(vac_name):
    all_skills = []
    desired_vacancy_count = 100
    vacancies_per_page = 20
    pages_to_fetch = (desired_vacancy_count + vacancies_per_page - 1) // vacancies_per_page

    for page in range(pages_to_fetch):
        response = requests.get(
            f"https://api.hh.ru/vacancies?text={vac_name}&page={page}&per_page={vacancies_per_page}"
        )

        if response.status_code == 200:
            vacancies = response.json()["items"]
            for i in vacancies:
                vac_id = i["id"]
                vac_response = requests.get(f"https://api.hh.ru/vacancies/{vac_id}")
                if vac_response.status_code == 200:
                    for j in vac_response.json().get("key_skills", []):
                        all_skills.append(j["name"])

    each_element = []
    sizes = []
    for skill in all_skills:
        if skill not in each_element:
            each_element.append(skill)

    for skill in each_element:
        count = all_skills.count(skill)
        sizes.append(count)

    max5_elements = []
    sizes_max5 = []
    total_count = sum(sizes)
    for i in range(len(sizes)):
        percentage = (sizes[i] / total_count) * 100
        if percentage > 2.5:  
            max5_elements.append(each_element[i])
            sizes_max5.append(sizes[i])

    sizes_other = total_count - sum(sizes_max5)
    if sizes_other > 0:
        max5_elements.append("other")
        sizes_max5.append(sizes_other)

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        sizes_max5, labels=max5_elements, autopct='%1.1f%%', startangle=140,
        pctdistance=0.85, labeldistance=1.1
    )
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(8)
    plt.title("Распределение ключевых навыков")
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'pie_chart.png'), bbox_inches='tight')
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('tight')
    ax.axis('off')
    table_data = [["Навык", "Количество упоминаний", "Процент"]]
    for skill, size in zip(max5_elements, sizes_max5):
        percentage = round((size / total_count) * 100, 1)
        table_data.append([skill, size, f"{percentage}%"])

    table = ax.table(cellText=table_data, cellLoc='center', loc='center', edges='horizontal')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'skills_table.png'), bbox_inches='tight')
    plt.close()
