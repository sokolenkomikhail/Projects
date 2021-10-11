
-- Процедура по обновлению данных по оценкам фильмов.
-- Для отображения текущего рейтинга фильма без обращения к таблице rating.
-- Предполагается регулярный вызов во время наименьшей нагрузки на БД (например раз в сутки, ночью)
DELIMITER //
DROP PROCEDURE IF EXISTS update_movies_ratings//
CREATE PROCEDURE update_movies_ratings()
BEGIN
	UPDATE 
		movies 
	SET 
        rate_count = (SELECT COUNT(*) FROM rating WHERE movie_id = movies.id), 
        rating = (SELECT AVG(rate) FROM rating WHERE movie_id = movies.id);
END //
DELIMITER ;


-- Триггеры по проверке вставляемых/обновляемых данных в таблице movies_names.
-- Для избежания ситуации, когда у человека, с прописанной работой отличной от 'Actor' была прописана роль
DELIMITER //
DROP TRIGGER IF EXISTS check_update_movies_names_role//
CREATE TRIGGER check_update_movies_names_role BEFORE UPDATE ON movies_names
FOR EACH ROW 
BEGIN
	IF (NEW.job_id != 4 AND NEW.role IS NOT NULL) THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UPDATE canceled(role NOT NULL)';
	END IF;
END //

DROP TRIGGER IF EXISTS check_insert_movies_names_role//
CREATE TRIGGER check_insert_movies_names_role BEFORE INSERT ON movies_names
FOR EACH ROW
BEGIN
	IF (NEW.job_id != 4 AND NEW.role IS NOT NULL) THEN 
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'INSERT canceled(role NOT NULL)';
	END IF;
END //
DELIMITER ;
