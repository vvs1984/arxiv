**Проведение моделирования классификации вин**

 В данном проекте ведется исследование возможности использования алгоритмов машинного обучения для автоматизации процесса категоризации вин.
Для отбора ассортимента продаваемых вин в сети магазинов ААА
данный момент для этого используется экспертная оценка.
Была выдвинута гипотеза:
С помощью алгоритмов машинного обучения можно автоматизировать
процесс категоризации новых образцов вин, основываясь на данных
проведенных ранее экспертиз.
При качестве работы модели по критерию accuracy равному  80% и выше можно сократить траты на экспертную оценку на 40000 руб/мес и ускорить процесс категоризации вин на 25мин/образец.


**Содержание проекта.**

**Code.**

 aml7ds9_zak_hw2_bisness_SMOLNIKOV.ipynb — содержит предоброаботку данных, моделирование и анализ результатов моделирования

**Data.** 

-**external**
выгруженный датасет с https://www.kaggle.com/rajyellow46/wine-quality

- Описание переменных
1 - fixed acidity   
2 - volatile acidity   
3 - citric acid   
4 - residual sugar   
5 - chlorides   
6 - free sulfur dioxide   
7 - total sulfur dioxide   
8 - density   
9 - pH   
10 - sulphates   
11 - alcohol   
Output variable (based on sensory data):   
12 - quality (score between 0 and 10)


-**processed**
Датасеты  после обработки признаков, чистки от пустых значений и выбросов
Выбросами считаются данные со следующими свойствами: 

citric acid > 0.75   
residual sugar > 20   
chlorides > 0.4   
free sulfur dioxide > 125  
total sulfur dioxide > 300 
((type == red) &  (total sulfur dioxide > 220 ))
((type == red) &  (residual sugar > 10 ))
density >1.05 
sulphates >  1.5 
alcohol ==  8 
alcohol >  14


full_X.csv – выгрузка из PandasDataset



- Описание переменных
Factor_1 = 'fixed acidity' * 'density'      
Factor_2 = 'volatile acidity'*'citric acid'*'chlorides' * 'total sulfur dioxide',       
Factor_3 = 'residual sugar'*'free sulfur dioxide'*'total sulfur dioxide'*'density',     
Factor_6 = , 'density'*'alcohol'      
pH,       
sulphates,      
white – маркер класса вина белое =1, красное =0




X.csv –  нормированный  датасет full_X с помощью StandatdScaler,  выгрузка из np.array

- Описание переменных
Колонка1 = Factor_1 = 'fixed acidity' * 'density'   
Колонка2 = Factor_2 = 'volatile acidity'*'citric acid'*'chlorides' * 'total sulfur dioxide',    
Колонка3 = Factor_3 = 'residual sugar'*'free sulfur dioxide'*'total sulfur dioxide'*'density',    
Колонка4 = Factor_6 = , 'density'*'alcohol'   
Колонка5 = pH,    
Колонка6 = sulphates,   
Колонка7 = white


y.csv –  массив предсказываемых классов, выгрузка из np.array


train_X.csv.csv – тренировочная выборка  из датасета X.csv с помощью train_test_split, train_size = .7 ,  выгрузка из np.array


train_y.csv.csv – тренировочная выборка  из датасета y.csv с помощью train_test_split, train_size = .7 ,  выгрузка из np.array


test_X.csv – тестовая выборка  из датасет X.csv с помощью train_test_split, train_size = .7 ,  выгрузка из np.array


test_y.csv.csv – тестовая выборка  из датасета y.csv с помощью train_test_split, train_size = .7 ,  выгрузка из np.array


-**import_data.py**

скрипт для выгрузки датасета с https://www.kaggle.com/rajyellow46/wine-quality
!Внимание используется официальная библиотека kaggle – требуется API Token
Подробная информация https://github.com/Kaggle/kaggle-api

**Images.**

-**imput_data** — визуализация данных входного датасета

-**intermid_data** - визуализация данных промежуточной обработки входного датасета

-**output_data** - визуализация данных работы моделей

-**processed_data** - визуализация данных обработанного для обучения моделью датасета.


**Models.**

Picle файлы моделей


**Output.**

Метрики качества по моделям


**Review.**

Отчёты о проделанной работе


**Модели и их настройка**

Был выбран вариант OneVsRestClassifier с SVC классификатором с ядром rbf и балансировкой классов


**Тестирование модели**

Качество работы по критерию accuracy составило 42% на тестовой выборке, что существенно ниже требуемого уровня.


**Возможные пути развития**

Так как математическая модель не смогла показать требуемое качество
работы, возможны следующие варианты дальнейшей работы:

1. Отказ от использования алгоритмов машинного обучения в связи с
недостижением требуемого качества.
2. Остановка исследования для увеличения количества тренировочных данных, импользуемых при машинном обучении.
Классификация производится с помощью экспетизы, новые отчеты
добавляются к тренировочным данным для машинного обучения
3. Огрубление классификации путём уменьшения количетва равному  (использовать не 9, а 3 класса) .
4. Исследование использования других моделей  классификации.
5. Запуск модели в существующем виде для сравнения количества
проданного вина при экспетрной оценке и с помощью алгоритмов
машинного обочения (A/B равному  80% тестирование)
