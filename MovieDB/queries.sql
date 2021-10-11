-- Топ 10 фильмов
-- Рейтинг строится среди фильмов, имеющих кол-во оценок большее или равное среднему кол-ву.
SELECT
	id,
	rus_title AS title, 
	ROUND(rating, 4) AS rating
FROM movies 
WHERE rate_count >= (SELECT AVG(rate_count) FROM movies)
	ORDER BY rating DESC 
	LIMIT 10;


-- информация по фильму
SELECT DISTINCT
	m.id,
	m.rus_title, 
	m.title, 
	FIRST_VALUE(CONCAT(n.first_name, ' ', n.last_name)) OVER(ORDER BY mn.job_id) AS Director,
	NTH_VALUE(CONCAT(n.first_name, ' ', n.last_name), 2) OVER() AS Writer,
	NTH_VALUE(CONCAT(n.first_name, ' ', n.last_name), 3) OVER() AS Producer,
	CONCAT(ms.runtime DIV 60, 'h ', ms.runtime % 60, 'm') AS chrono,
	(SELECT 
		GROUP_CONCAT(genre SEPARATOR ', ') 
	FROM movies_genres AS mg 
	JOIN genres AS g ON mg.genre_id = g.id 
		WHERE movie_id = m.id) AS genres,
	m.release_world, 
	m.release_russia, 
	m.release_dvd, 
	m.budget,
	(SELECT SUM(proceeds) FROM box_office WHERE movie_id = m.id) AS box_office,
	ROUND(m.rating, 4) AS rating
FROM movies AS m 
JOIN movies_specs AS ms ON m.id = ms.movie_id
JOIN movies_names AS mn ON m.id = mn.movie_id 
JOIN names AS n ON mn.name_id = n.id 
	WHERE m.id = 22 AND mn.job_id < 4;


-- актерский состав и исполняемые роли
SELECT 
	CONCAT(n.first_name, ' ', n.last_name) AS Actors, 
	mn.role 
FROM movies_names AS mn 
JOIN names AS n ON mn.name_id = n.id 
	WHERE movie_id = 22 AND mn.job_id = 4;


-- рецензии к фильму
SELECT 
	CONCAT(u.first_name, ' ', u.last_name) AS user, 
	r.head, 
	r.body, 
	r.created_at 
FROM reviews AS r 
JOIN movies AS m ON r.movie_id = m.id 
JOIN users AS u ON r.user_id = u.id
	WHERE r.movie_id = 22;


-- фильмография определенного лица
-- выводятся: название(в российском прокате, оригинальное) фильма, рейтинг фильма, работа в этом фильме, исполняемая роль
SELECT DISTINCT
	m.rus_title, 
	m.title, 
	AVG(r.rate) OVER(PARTITION BY m.id) AS Rating,
	j.job,
	mn.role
FROM movies_names AS mn 
JOIN movies AS m ON mn.movie_id = m.id 
JOIN rating AS r ON r.movie_id = mn.movie_id 
JOIN jobs AS j ON mn.job_id = j.id 
	WHERE name_id = 250;


-- фотографии определенного лица
SELECT id, title, link FROM names_photo WHERE name_id = 250;


-- 5 новых рецензий
SELECT 
	m.rus_title AS movie, 
	r.head, 
	CONCAT(u.first_name, ' ', u.last_name) AS name, 
	r.created_at 
FROM reviews AS r 
JOIN movies AS m ON r.movie_id = m.id 
JOIN users AS u ON r.user_id = u.id 
	ORDER BY r.created_at DESC 
	LIMIT 5;


-- трейлеры и тизеры к фильмам
SELECT 
	m.rus_title,
	m.title,
	mm.title,
	mt.type, 
	mm.created_at 
FROM movies_media AS mm 
JOIN media_types AS mt ON mm.media_type_id = mt.id 
JOIN movies AS m ON m.id = mm.movie_id 
	WHERE mt.type = 'teaser' OR mt.type = 'trailer' 
	ORDER BY created_at DESC;




-- Представления

-- афиша 
-- дата выхода, id фильма, названия (в российском прокате, оригинальное), режиссер, описание
CREATE VIEW 
	announcements AS
SELECT 
	m.release_russia, 
	m.id, 
	m.rus_title, 
	m.title, 
	CONCAT(n.first_name, ' ', n.last_name) AS Director,
	m.story
FROM movies AS m 
JOIN movies_names AS mn ON m.id = mn.movie_id 
JOIN names AS n ON mn.name_id = n.id
	WHERE mn.job_id = 1;


SELECT * FROM announcements;

-- после текущей* даты
-- *вместо NOW() в запросе выставлена конкретная дата
SELECT release_russia, rus_title, Director FROM announcements WHERE release_russia >= '2020-02-16' ORDER BY release_russia;



-- кассовые сборы у фильмов
CREATE VIEW 
	movies_box_offices AS
SELECT DISTINCT
	m.id,
	m.rus_title,
	m.title, 
	bo.date, 
	bo.proceeds 
FROM box_office AS bo
JOIN movies AS m ON m.id = bo.movie_id;


-- примеры
-- топ 10 фильмов по кассовым сборам
SELECT id, rus_title, SUM(proceeds) AS sum FROM movies_box_offices GROUP BY id ORDER BY sum DESC LIMIT 10;

-- общая выручка по датам
SELECT date, SUM(proceeds) AS sum FROM movies_box_offices GROUP BY date ORDER BY date;

-- выручка по фильмам за уик-энд
SELECT 
	rus_title, 
	SUM(proceeds) AS sum 
FROM movies_box_offices 
	WHERE date IN ('2020-02-07', '2020-02-08', '2020-02-09') 
	GROUP BY id 
	ORDER BY sum DESC;
