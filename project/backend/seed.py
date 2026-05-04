from database import engine, SessionLocal
import models

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

if db.query(models.Vakansiya).count() == 0:
    vakansii = [
        models.Vakansiya(nazvanie="Python разработчик", kompaniya="Яндекс", logo="🟡", zarplata="180 000 – 250 000 ₽", rezhim="Удалённо", opisanie="Разработка бэкенда для высоконагруженных сервисов.", trebovaniya="Python 3.8+, FastAPI, PostgreSQL, Git", tegi="Python,Backend,Удалёнка"),
        models.Vakansiya(nazvanie="Frontend разработчик", kompaniya="Сбер", logo="🟢", zarplata="150 000 – 200 000 ₽", rezhim="Офис", opisanie="Разработка интерфейсов для банковских продуктов.", trebovaniya="React, TypeScript, CSS, REST API", tegi="React,TypeScript,Офис"),
        models.Vakansiya(nazvanie="Java разработчик", kompaniya="ВТБ", logo="🔵", zarplata="200 000 – 280 000 ₽", rezhim="Гибрид", opisanie="Разработка микросервисов на Java Spring Boot.", trebovaniya="Java 17+, Spring Boot, Kafka, Docker", tegi="Java,Spring,Гибрид"),
        models.Vakansiya(nazvanie="UX/UI Дизайнер", kompaniya="Авито", logo="🟠", zarplata="120 000 – 170 000 ₽", rezhim="Удалённо", opisanie="Проектирование интерфейсов мобильных приложений.", trebovaniya="Figma, Прототипирование, UX исследования", tegi="Дизайн,Figma,Удалёнка"),
        models.Vakansiya(nazvanie="DevOps инженер", kompaniya="Озон", logo="🔵", zarplata="220 000 – 300 000 ₽", rezhim="Гибрид", opisanie="Поддержка и развитие инфраструктуры.", trebovaniya="Kubernetes, Docker, CI/CD, Terraform", tegi="DevOps,K8s,Гибрид"),
        models.Vakansiya(nazvanie="iOS разработчик", kompaniya="Тинькофф", logo="🟡", zarplata="160 000 – 230 000 ₽", rezhim="Офис", opisanie="Разработка мобильного приложения iOS.", trebovaniya="Swift, UIKit, CoreData, REST API", tegi="iOS,Swift,Офис"),
        models.Vakansiya(nazvanie="Android разработчик", kompaniya="МТС", logo="🔴", zarplata="150 000 – 220 000 ₽", rezhim="Удалённо", opisanie="Разработка Android-приложений.", trebovaniya="Kotlin, Jetpack Compose, MVVM, Coroutines", tegi="Android,Kotlin,Удалёнка"),
        models.Vakansiya(nazvanie="Data Scientist", kompaniya="Яндекс", logo="🟡", zarplata="250 000 – 350 000 ₽", rezhim="Гибрид", opisanie="Построение ML моделей для рекомендаций.", trebovaniya="Python, TensorFlow, SQL, Statistics", tegi="ML,DataScience,Гибрид"),
        models.Vakansiya(nazvanie="Аналитик данных", kompaniya="Сбер", logo="🟢", zarplata="130 000 – 180 000 ₽", rezhim="Офис", opisanie="Анализ данных и дашборды для бизнеса.", trebovaniya="SQL, Python, Tableau, Excel", tegi="Аналитика,SQL,Офис"),
        models.Vakansiya(nazvanie="Тестировщик QA", kompaniya="Авито", logo="🟠", zarplata="100 000 – 140 000 ₽", rezhim="Удалённо", opisanie="Ручное и автоматизированное тестирование.", trebovaniya="Selenium, Python, Postman, TestRail", tegi="QA,Тестирование,Удалёнка"),
        models.Vakansiya(nazvanie="Менеджер проекта", kompaniya="ВТБ", logo="🔵", zarplata="120 000 – 160 000 ₽", rezhim="Офис", opisanie="Управление командой разработки.", trebovaniya="Agile, Jira, MS Project", tegi="PM,Agile,Офис"),
        models.Vakansiya(nazvanie="Системный администратор", kompaniya="МТС", logo="🔴", zarplata="90 000 – 130 000 ₽", rezhim="Офис", opisание="Администрирование серверной инфраструктуры.", trebovaniya="Linux, Windows Server, Active Directory", tegi="SysAdmin,Linux,Офис"),
        models.Vakansiya(nazvanie="Продуктовый менеджер", kompaniya="Озон", logo="🔵", zarplata="180 000 – 260 000 ₽", rezhim="Гибрид", opisanie="Развитие продуктов маркетплейса.", trebovaniya="Продуктовое мышление, A/B тесты, SQL", tegi="Product,Маркетплейс,Гибрид"),
        models.Vakansiya(nazvanie="Fullstack разработчик", kompaniya="Авито", logo="🟠", zarplata="200 000 – 270 000 ₽", rezhim="Гибрид", opisanie="Разработка фронтенда и бэкенда.", trebovaniya="React, Node.js, PostgreSQL, Redis", tegi="Fullstack,React,Гибрид"),
        models.Vakansiya(nazvanie="Технический писатель", kompaniya="Тинькофф", logo="🟡", zarplata="80 000 – 110 000 ₽", rezhim="Удалённо", opisanie="Написание технической документации.", trebovaniya="Русский язык, Markdown, API документация", tegi="Документация,Удалёнка"),
    ]
    db.add_all(vakansii)

if db.query(models.Kompaniya).count() == 0:
    kompanii = [
        models.Kompaniya(nazvanie="Яндекс", logo="🟡", opisanie="Технологическая компания, поисковик, экосистема сервисов.", vakansij_count=42),
        models.Kompaniya(nazvanie="Сбер", logo="🟢", opisanie="Крупнейший банк России, активно развивающий IT.", vakansij_count=87),
        models.Kompaniya(nazvanie="ВТБ", logo="🔵", opisanie="Один из ведущих банков страны.", vakansij_count=34),
        models.Kompaniya(nazvanie="Авито", logo="🟠", opisanie="Крупнейший российский маркетплейс объявлений.", vakansij_count=28),
        models.Kompaniya(nazvanie="Озон", logo="🔵", opisanie="Ведущий e-commerce маркетплейс России.", vakansij_count=56),
        models.Kompaniya(nazvanie="Тинькофф", logo="🟡", opisanie="Онлайн-банк и финтех экосистема.", vakansij_count=61),
        models.Kompaniya(nazvanie="МТС", logo="🔴", opisanie="Крупнейший телеком-оператор России.", vakansij_count=39),
        models.Kompaniya(nazvanie="Mail.ru", logo="🔵", opisanie="Интернет-компания, ВКонтакте, игры.", vakansij_count=25),
        models.Kompaniya(nazvanie="Ростелеком", logo="🔵", opisanie="Государственный телеком-гигант.", vakansij_count=47),
        models.Kompaniya(nazvanie="Лаборатория Касперского", logo="🟢", opisanie="Мировой лидер в кибербезопасности.", vakansij_count=31),
    ]
    db.add_all(kompanii)

db.commit()
db.close()
print("База данных заполнена!")
