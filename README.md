# Regex Based Temporal Expression Parser for Turkish

This project currently contains hand crafted regex rules for detecting temporal 
expressions in Turkish. All of these rules are categorized into three categories.
These categories are,

1. datetime, indicating a particular date time. For example "right now". 
2. date-span, indicating a span with a start date time and an end. For example "next 
weekend".
3. date-period, indicating periodic expressions such as "every monday".

 ## Number Detector

Number detection is essential for detecting temporal expressions. 
Therefore a number detector is implemented within the project.
This number detector should work with both textual and numeric expressions.

 ### Number detector examples

````text
>iki yüz elli beş bin 93
[{'type': 'number', 'start_index': 0, 'end_index': 23, 'text': 'iki yüz elli beş bin 93', 'value': 255093.0}]
>3 yumurta 5 de ekmek alacağım.
[{'type': 'number', 'start_index': 0, 'end_index': 1, 'text': '3', 'value': 3}, 
{'type': 'number', 'start_index': 10, 'end_index': 11, 'text': '5', 'value': 5}]
````

 ## Date detector

Note that the rules are defined as a list of tuples. (TODO, read rules from an external file.)
A tuple contains 4 elements:

1. Rule name
2. Date expression type. One of "datetime", "date-span" or "date-period"
3. Regex rule
4. Return datetime(s)

> Note: Currently there are about 78 rules defined. 

### Date detector examples

````text
>şimdi
[{'start_index': 0, 'end_index': 4, 'text': 'şimdi', 'type': 'datetime', 
'start_date': datetime.datetime(2021, 6, 24, 21, 48, 1), 'end_date': datetime.datetime(2021, 6, 24, 21, 48, 1)}]

>sekiz yüz elli gün önce
[{'start_index': 0, 'end_index': 22, 'text': 'sekiz yüz elli gün önce', 
'type': 'datetime', 'start_date': datetime.datetime(2019, 2, 25, 21, 48, 5), 
'end_date': datetime.datetime(2019, 2, 25, 21, 48, 5)}]

>ekim başı ne yapmıştım acaba?
[{'start_index': 0, 'end_index': 8, 'text': 'ekim başı', 'type': 'datetime', 
'start_date': datetime.datetime(2021, 10, 1, 21, 48, 50), 'end_date': datetime.datetime(2021, 10, 1, 21, 48, 50)}]

>5 hafta önce salı
[{'start_index': 0, 'end_index': 16, 'text': '5 hafta önce salı', 'type': 'datetime', 
'start_date': datetime.datetime(2021, 5, 18, 21, 49, 34), 'end_date': datetime.datetime(2021, 5, 18, 21, 49, 34)}]

>işçi bayramı
[{'start_index': 0, 'end_index': 11, 'text': 'işçi bayramı', 'type': 'date-span', 
'start_date': datetime.datetime(2021, 5, 1, 0, 0), 'end_date': datetime.datetime(2021, 5, 1, 23, 59, 59)}]

>son 4 hafta nasıl da geçti
[{'start_index': 0, 'end_index': 10, 'text': 'son 4 hafta', 'type': 'date-span', 
'start_date': datetime.datetime(2021, 5, 27, 21, 52, 13), 'end_date': datetime.datetime(2021, 6, 24, 21, 52, 13)}]

>her ayın 6sı
[{'start_index': 0, 'end_index': 11, 'text': 'her ayın 6sı', 'type': 'date-period', 
'start_date': {'month': '6'}, 'end_date': {'month': '6'}}]
````
 
 
 ### Current Notable Problems
- Detecting religious holidays, as they don't happen at a specific date but once in 11 months.
- Performance on a large scale.
 