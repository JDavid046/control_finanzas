DELIMITER //
CREATE PROCEDURE proc_Programador()
BEGIN
   SET @fecha  = (SELECT day((SELECT NOW())));

	CREATE TEMPORARY TABLE tmpProgramador AS (SELECT * FROM sistema_control_programador where fechaMovimientoProgramado = @fecha);
	
	SELECT * FROM tmpProgramador;
	
	CREATE TEMPORARY TABLE IF NOT EXISTS tmpProfiles AS (SELECT p.user_id, tmp.tipoMovimiento_id, tmp.valorMovimientoProgramado FROM sistema_control_profile p INNER JOIN tmpProgramador tmp ON p.user_id = tmp.usuario_id);
	
	SELECT * FROM tmpProfiles;
		
	
	SET @cantidad = (SELECT COUNT(id) FROM tmpProgramador);
	
	IF @cantidad > 0 THEN
			
		INSERT INTO sistema_control_movimiento (descripcionMovimiento, valorMovimiento, fechaMovimiento, tipoMovimiento_id, usuario_id)
		SELECT descripcionMovimientoProgramado, valorMovimientoProgramado, (SELECT CURDATE()), tipoMovimiento_id, usuario_id
		FROM tmpProgramador
		WHERE (SELECT @cantidad) > 0;			
		
		WHILE (SELECT count(id) FROM tmpProgramador) > 0 DO
		
			CREATE TEMPORARY TABLE tmpMovProgram AS (SELECT * FROM tmpProgramador LIMIT 1);
			SELECT * FROM tmpMovProgram;
			
			UPDATE sistema_control_profile AS p
			INNER JOIN tmpMovProgram AS tmpMov ON p.user_id = tmpMov.usuario_id
			SET p.capitalTotal = 
			case 
			when tmpMov.tipoMovimiento_id = 2 then p.capitalTotal - tmpMov.valorMovimientoProgramado
			when tmpMov.tipoMovimiento_id = 1 then p.capitalTotal + tmpMov.valorMovimientoProgramado
			END
			WHERE (SELECT @cantidad) > 0;
			
			DELETE FROM tmpProgramador WHERE id = (SELECT id FROM tmpMovProgram);
			
			DROP TEMPORARY TABLE tmpMovProgram;
			
		END WHILE;		
		
		UPDATE sistema_control_programador AS pr
		INNER JOIN tmpProfiles as tmp on pr.usuario_id = tmp.user_id
		SET pr.ultimaFechaEjecucion = CURDATE()
		WHERE (SELECT @cantidad) > 0
		AND pr.fechaMovimientoProgramado = @fecha;
		
	END IF;
	
	DROP TEMPORARY TABLE tmpProgramador;
	DROP TEMPORARY TABLE tmpProfiles;
	   
END //
    
DELIMITER ;

CALL proc_Programador();