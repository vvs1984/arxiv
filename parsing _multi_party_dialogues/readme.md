# Итоговая работа по теме "Исследование методов парсинга в многосторонних диалогах."

>Создание структуры многостороннего диалога может быть полезно 
>при решении многих задач машинного обучения: 
>понимание диалога, создание авторефератов ветвей дискуссии, 
>анализ настроений, визуализация различных ветвей 
>многостороннего диалога в пользовательском интерфейсе и пр. 
>В данной работе проводится исследование о возможности применения 
>наработок для разбора дискурса на английском языке 
>для русскоязычных диалогов. В качестве основной модели 
>используется глубокая последовательная модель для разбора 
>многосторонних диалогов. Данная модель строит дерево зависимостей 
>диалога прогнозированием отношений зависимостей между отдельными
>репликами. Выполняется поиск элементарных модулей дискурса (EDU), 
>после чего модель определяет, с каким из предыдущих EDU есть 
>взаимосвязь и её тип. Эксперименты с переводом данной модели на 
>работу с русским языком показали сохранение качества работы 
>алгоритма при сравнении с моделью, обучавшейся на англискийх диалогах.


## Содержание


### code - папка с различными вариантами кода для модели, а так же дополителные скрипты и ноутбуки для преобразования и анализа данных

**china** - исходная модель (https://github.com/shizhouxing/DialogueDiscourseParsing) 

- Python v2.7 

- Tensorflow 1.3

**fasttext_ru** - вариант модели для русского языка с использованием fasttext эмбеддингов

- Python v3.6 

- Tensorflow 1.13

**glove_ru** - вариант модели для русского языка с использованием glove эмбеддингов

- Python v2.7 

- Tensorflow 1.13
 
>eng_translation.ipynb - перевод датасета на русский язык

>eng_translation_EDA.ipynb -анализ переведенного датасета

>en_test_EDA.ipynb - анализ результатов работы моделей


### data - исходный и предобработанный датасет


### images - изображения, полученные в результате анализа информации


### output - результаты работы моделей


### papers - статьи для изучения и переводы


### review - отчет и презентация по итогам работы


***

## Список источников (основных).

   1. [Semantics, Pragmatics and Discourse](https://depts.washington.edu/hpsg2011/s/Asher.pdf) 
   2. [Evaluating Discourse-based Answer Extraction for Why-Question Answering](https://liacs.leidenuniv.nl/~verbernes/papers/Verberne_2007_Evaluating%20discourse-based%20answer%20extraction%20for%20why-QA.pdf)
   4. [Discourse Structure and Dialogue Acts in Multiparty Dialogue:the STAC Corpus.]( https://www.cs.brandeis.edu/~cs140b/CS140b_docs/AnnotationPapers/STAC_corpus_Dialog.pdf)
   5. [STAC dataset.](https://www.irit.fr/STAC/corpus.html)
   6. [Discourse parsing for multi-party chat dialogues. Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing, pages 928–937,Lisbon, Portugal, 17-21 September 2015.c©2015 Association for Computational Linguistics.](https://www.aclweb.org/anthology/D15-1109.pdf)
   7.  [LEARNING MULTI-PARTY DISCOURSE STRUCTURE USING WEAK SUPERVISION](http://www.dialog-21.ru/media/4584/badenesplusetal-112.pdf)
   8. [A Deep Sequential Model for Discourse Parsing on Multi-Party Dialogues]( https://arxiv.org/pdf/1812.00176.pdf)
   9. [Dialogue Discourse Parsing. Сode to Zhouxing Shi and Minlie Huang. A Deep Sequential Model for Discourse Parsing on Multi-Party Dialogues. In AAAI, 2019.]( https://github.com/shizhouxing/DialogueDiscourseParsing)







