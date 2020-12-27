--В каких городах больше одного аэропорта?
--EXPLAIN (ANALYZE)
select 
a.airport_code as code,
a.airport_name ,
a.city 
from bookings.airports a 
where a.city  in 
(
	select 
	aa.city 
	from bookings.airports aa 
	group by aa.city 
	having count(*) >1 
)
order by a.city , a.airport_code 

-- для решения данной задачи используется таблица airports с фильтрацией по таблице из подзапроса 
-- на основании таблицы airports с выводом городов, упоминающихся более 1 раза


--В каких аэропортах есть рейсы, выполняемые самолетом с максимальной дальностью перелета?
--EXPLAIN (ANALYZE)
select 
DISTINCT(r.departure_airport ||' ' || r.departure_airport_name ) as airport
from 
bookings.routes r 
where r.aircraft_code in 
(
	select 
	a.aircraft_code
	from bookings.aircrafts a
	where a."range" = 
		(
		select 
		max(a2."range")
		from bookings.aircrafts a2 
		)
)
order by airport
-- для решения данной задачи таблица routes с фильтрацией по таблице из подзапроса 
-- на основании таблицы aircrafts, в которой ищется ЛА с максимальной дальностью полёта ( за счёт филььтрации по колонке "range")


--Вывести 10 рейсов с максимальным временем задержки вылета
--EXPLAIN (ANALYZE)
select 
f.flight_no ,
f.actual_departure - f.scheduled_departure  as delay_time
from bookings.flights f 
where f.actual_departure notnull 
order by delay_time desc
limit 10
-- для решения данной задачи используется таблица flights
-- с выводом номера рейса и разности между акуальным и планируемым временем.
-- Вывод 10 рейсов с максимальной задержкой осуществляется за счёт сортировке по времени задежки по убыванию
-- выводе только первых 10 строк .
-- В расчётах используются только рейсы с состоявшимся вылетом (проверка where f.actual_departure notnull )



--Были ли брони, по которым не были получены посадочные талоны?
--EXPLAIN (ANALYZE)
select 
case  when  c.counter = null then 'Нет броней без посадочных талонов' 
                             else 'Есть '  || c.counter ||' броней без посадочных талонов'
end as "Брони без посадочных талонов"
from (
	select 
	count(distinct t.book_ref)  as counter
	from bookings.tickets t
	left join bookings.boarding_passes bp on bp.ticket_no = t.ticket_no 
	where bp.ticket_no is null 
) as c
-- https://www.postgresqltutorial.com/postgresql-joins/
-- Для формирования ответа делается подзапрос на соновании таблицы tickets с пересечением 
-- с таблицей boarding_passes по значениям , где ticket_no is null (то есть билеты были куплены, но не 
-- оформлены посадочные талоны  в таблице boarding_passes. 
-- формирование текстового оттвета происходит за счёт искользования    операторов case when   then end 


--
--Найдите свободные места для каждого рейса, их % отношение к общему количеству мест в самолете.
--Добавьте столбец с накопительным итогом - суммарное количество вывезенных пассажиров из аэропорта за день. 
--Т.е. в этом столбце должна отражаться сумма - сколько человек уже вылетело из данного аэропорта на этом 
--или более ранних рейсах за сегодняшний день
--- Оконная функция
--- Подзапрос

--EXPLAIN (ANALYZE)
--Execution time: 1017.510 ms
select 
dt.a_d as "время вылета",
dt.d_a ||' ' || a.airport_name as "аэропорт",
dt.flight_id as "№ рейса",
dt.busy_seats as "мест занято",
dt.total_seat - dt.busy_seats as "свободных мест",
round((dt.total_seat - dt.busy_seats)*100/dt.total_seat, 2) as "свободных мест, %",
-- подсчёт относительного количества свободных мест
sum(dt.busy_seats) over (partition by dt.d_a, dt.d_d order by  dt.a_d, dt.d_d) as "пассажиров в день"
-- оконная функция : суммируется колчиество занятых пест . Вкачестве обьектов группировки выступают аэропорт и день вылета. Сортировка по дате
from(
--подзапрос
	select
	f.actual_departure as a_d ,
	EXTRACT(day FROM f.actual_departure) as d_d,
	--извлечение сущности день из временного поля
	f.departure_airport as d_a,
	f.flight_id ,
	ac.total_seat,
	count(bp.boarding_no ) as busy_seats
	--подсчёт количества посадочных талонов по рейсу (см. group by)
	from bookings.flights f  
	left join bookings.boarding_passes bp on bp.flight_id  = f.flight_id
	--левое присоединение таблицы ticket_flights на flight_id
	left join (
	-- подзапрос
	select 
	s.aircraft_code ,
	count(s.seat_no ) as total_seat
	--подсчёт мест в судне (см. group by)
	from bookings.seats s
	group by s.aircraft_code
-- указание на группирующий элемент для подсчёта количества мест
) as ac on ac.aircraft_code = f.aircraft_code 
-- левое присоединение подзапроса на aircraft_code
where f.actual_departure is  not null 
-- убираются невзлетевшие рейсы
group by f.actual_departure , f.flight_id, ac.total_seat
-- указание на группирующий элементы для подсчёта количества билетов на рейсе
) as dt
left join bookings.airports a on a.airport_code = dt.d_a 
-- левое присоединение таблицы с названиями аэропортов по airport_code 




--Найдите процентное соотношение перелетов по типам самолетов от общего количества.

select 
a.model as "модель самолёта",
counter as "N полётов",
round(counter*100/(sum(fl.counter) OVER ()),1) as "% полётов"
from
(
	select 
	f.aircraft_code ,
	count(flight_id ) as counter
	from bookings.flights f
	group by f.aircraft_code 
) as fl
left join bookings.aircrafts a on a.aircraft_code = fl.aircraft_code
order by "% полётов" desc




--Были ли города, в которые можно  добраться бизнес - классом дешевле, 
--чем эконом-классом в рамках перелета?
--- CTE
with flight_amount as (
	select 
	distinct flight_id ,
	min(case  when fare_conditions = 'Business' 
    	      then amount end) as business,
	max(case  when fare_conditions = 'Economy'
    	      then amount end) as economy
	from bookings.ticket_flights tf
	group by flight_id 
	order by flight_id
)
select
distinct airport_name as airport_b_low
from flight_amount as fa
left join bookings.flights f on f.flight_id = fa.flight_id
left join bookings.airports a on a.airport_code = f.arrival_airport 
where economy - business > 0
-- в данном задании вначале создаётся таблица  flight_amount, содержащая 
-- инфомрацию о идентификаторе рейса, минимальной цене бизнесс-класса
-- на данный вылет и максимальной цене эконом -класса.
-- Поиск городов строится на поиске рейсов, в которых цена 
-- бизнесс- класса меньше чем эконом на на одном перелёте.
-- Для вывода названий городов к flight_amount присоединяются 
-- таблицы flights и airports. Выводятся только уникальные названия городов ( без повторений)







--Между какими городами нет прямых рейсов?
--- Декартово произведение в предложении FROM
--- Представления
--- Оператор EXCEPT
--with city_matrix as (
--)


select
city_m.city1,
city_m.city2
from (
	select
	distinct r.arrival_city  as city1,
	r2.arrival_city as city2
	from 
	bookings.routes r 
	CROSS join
	bookings.routes r2
	where r.arrival_city != r2.arrival_city
	order by r.arrival_city
) as city_m
except 
select
r3.arrival_city,
r3.departure_city 
from bookings.routes r3 
order by city1

-- в данном решении формируется матрица city_m, которая 
-- является вычитанием из полной комбинации  сочетаний городов между собой
-- (Декартово произведение в предложении FROM таблицы routes) и списка существующих пар (из таблицы routes)
-- городов, в которых есть прямое сообщение.

 



--Вычислите расстояние между аэропортами, связанными прямыми рейсами,
-- сравните с допустимой максимальной дальностью перелетов 
-- в самолетах, обслуживающих эти рейсы *
--- Оператор RADIANS или использование sind/cosd


with distance_tbl as (
	select
	distinct c_m.arrival_city,
	c_m.departure_city,
	cast(2*asin(sqrt(sind((aa.latitude-a.latitude)/2)^2 + 
	cosd(a.latitude)*cosd(aa.latitude)*
	sind((aa.longitude - a.longitude)/2)^2))*6371 as int) as dist1,
	--https://en.wikipedia.org/wiki/Haversine_formula
	c_m.aircraft_code,
	a2."range" 
	from (
		select 
		r3.*,
		count(*) over (partition by  least(r3.arrival_airport ,r3.departure_airport ), greatest(r3.arrival_airport ,r3.departure_airport )) as cnt
		from bookings.routes r3 
	) as c_m
	left join bookings.airports a on a.airport_code = c_m.arrival_airport
	left join bookings.airports aa on aa.airport_code = c_m.departure_airport
	left join bookings.aircrafts a2  on a2.aircraft_code = c_m.aircraft_code
	where c_m.arrival_airport < departure_airport 
	or (c_m.arrival_airport < departure_airport and cnt = 1)
	order by c_m.arrival_city
)
select 
dt.arrival_city as "город 1",
dt.departure_city as "город 2",
dt.dist1 as "расстояние (L), км",
dt.aircraft_code as "код ЛА",
a3.model as "название ЛА",
dt."range" as "дальность (R), км",
dt."range" -dt.dist1 as "запас лёта, км",
cast((dt."range" -dt.dist1)*100/dt."range" as int) as "запас лёта, %",
cast((dt.dist1)*100/dt."range" as int) as "L/R"
from distance_tbl as dt
left join bookings.aircrafts a3 on a3.aircraft_code = dt.aircraft_code


--для выполения данного задания формируется таблица distance_tbl, содержащую колонки : arrival_city, departure_city,
--dist1 ( вычисляется по Haversine_formula). Так же удаляются зеркальыне дубли в парах  arrival_city, departure_city.
-- на базе distance_tbl формируется итоговая выдача с подсчётом запаса хода после перелета (относительном и  абсолютном)  и иотношение расстояния к дальности ЛА
-- основа таблицы - routes за вычетом зеркальных дублей, к воторой присоединены с помощью  left join  таблицы airports ( для отображения названий городов),
-- aircrafts ( для отображения названия ЛА)
