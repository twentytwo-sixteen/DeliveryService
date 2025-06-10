PORTS := 5432 6379 27017

.PHONY: up check_ports clean

up: check_ports
	docker-compose up

check_ports:
	@for port in $(PORTS); do \
		pids=$$(lsof -ti :$$port); \
		if [ -n "$$pids" ]; then \
			echo "Порт $$port занят процессами: $$pids. Убиваю..."; \
			echo "$$pids" | xargs -r kill -9; \
			sleep 1; \
			if lsof -ti :$$port >/dev/null; then \
				echo "Ошибка: порт $$port всё ещё занят после убийства. Прекращаю."; \
				exit 1; \
			else \
				echo "Порт $$port успешно освобождён."; \
			fi \
		else \
			echo "Порт $$port свободен."; \
		fi \
	done

clean:
	docker-compose down
	docker network prune -f
